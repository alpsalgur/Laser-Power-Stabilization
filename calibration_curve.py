import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import threading
import time
import csv
import pyvisa
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from ThorlabsPM100 import ThorlabsPM100
from nkt_tools.extreme import Extreme
from nkt_tools.varia import Varia

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Calibration Curve Acquisition")

    # Create a main frame for padding and layout
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(expand=True, fill="both")

    # Add a title label
    title_label = ttk.Label(main_frame, text="Calibration Curve Acquisition", 
                            font=("Helvetica", 16, "bold"))
    title_label.pack(pady=(0, 10))

    # Create a Treeview to display calibration data in a table
    columns = ("Step", "Wavelength (nm)", "Laser Power Setting (%)", "Measured Power (µW)")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, stretch=True, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    # Add a scrollbar for the Treeview
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="left", fill="y")

    # A status label to show ongoing status (e.g., current calibration step)
    status_label = ttk.Label(root, text="Status: Idle", font=("Helvetica", 12))
    status_label.pack(pady=10)

    # Additional frame for extra buttons
    button_frame = ttk.Frame(root, padding="10")
    button_frame.pack()

    # Hardware Setup (using PyVISA and device libraries)
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource('USB0::0x1313::0x8078::P0017991::INSTR')
    power_meter = ThorlabsPM100(inst=inst)

    Laser = Extreme()
    Filter = Varia()

    # List to store calibration results: each element is a tuple (wavelength, laser_setting, measured_power)
    calibration_results = []

    # Define a function to insert rows into the calibration table
    def log_calibration(step, wavelength, laser_setting, measured_power):
        tree.insert("", "end", values=(step, f"{wavelength:.1f}", f"{laser_setting:.1f}", f"{measured_power:.1f}"))

    def plot_calibration_curve(cal_data):
        # Unpack calibration data
        wavelengths = [item[0] for item in cal_data]
        laser_settings = [item[1] for item in cal_data]
        measured_powers = [item[2] for item in cal_data]

        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
        fig.suptitle("Calibration Curve")

        # Plot measured power vs. wavelength
        ax1.plot(wavelengths, measured_powers, 'bo-', label="Measured Power (µW)")
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel("Measured Power (µW)")
        ax1.legend()
        ax1.grid(True)

        # Plot laser power setting vs. wavelength
        ax2.plot(wavelengths, laser_settings, 'ro-', label="Laser Setting (%)")
        ax2.set_xlabel("Wavelength (nm)")
        ax2.set_ylabel("Laser Setting (%)")
        ax2.legend()
        ax2.grid(True)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    def export_calibration_data(cal_data, filename="calibration_data.csv"):   # I will modify here to save the csv files with different names every run
        try:
            with open(filename, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Wavelength (nm)", "Laser Setting (%)", "Measured Power (µW)"])
                for (w, s, p) in cal_data:
                    writer.writerow([w, s, p])
            messagebox.showinfo("Export Data", f"Calibration data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def create_interpolation_functions(cal_data):
        # Extract arrays from calibration data
        wavelengths = np.array([item[0] for item in cal_data])
        laser_settings = np.array([item[1] for item in cal_data])
        measured_powers = np.array([item[2] for item in cal_data])
        # Create interpolation functions (linear interpolation)
        laser_setting_interp = interp1d(wavelengths, laser_settings, kind='linear', fill_value="extrapolate")
        measured_power_interp = interp1d(wavelengths, measured_powers, kind='linear', fill_value="extrapolate")
        return laser_setting_interp, measured_power_interp

    def interpolate_calibration():
        if not calibration_results:
            messagebox.showerror("Interpolation Error", "No calibration data available!")
            return
        # Ask user for a desired wavelength
        try:
            wavelength_input = simpledialog.askfloat("Interpolate", "Enter desired wavelength (nm):")
            if wavelength_input is None:
                return
        except Exception as e:
            messagebox.showerror("Input Error", str(e))
            return

        laser_interp, power_interp = create_interpolation_functions(calibration_results)
        estimated_setting = laser_interp(wavelength_input)
        estimated_power = power_interp(wavelength_input)
        messagebox.showinfo("Interpolation Result",
                            f"At {wavelength_input:.1f} nm:\nEstimated Laser Setting: {estimated_setting:.1f}%\nEstimated Power: {estimated_power:.1f} µW")

    # Calibration routine: For each wavelength step, adjust laser power until target output is reached
    def run_calibration():
        status_label.config(text="Status: Starting calibration...")
        target_power_uW = 5.0    # Desired output power in µW
        tolerance = 0.5            # Acceptable deviation (µW)
        max_iterations = 10        # Maximum iterations for feedback loop

        # Set initial filter settings for starting wavelength
        Filter.short_setpoint = 400
        Filter.long_setpoint = 410
        starting_wavelength = (Filter.short_setpoint + Filter.long_setpoint) / 2

        # Set initial laser power and turn on emission
        initial_laser_power_setting = 30.0
        Laser.set_power(initial_laser_power_setting)
        Laser.set_emission(True)
        current_laser_setting = initial_laser_power_setting

        # Wait for the system to stabilize
        time.sleep(3)

        # Feedback loop to calibrate at starting wavelength
        iteration = 0
        while iteration < max_iterations:
            power_W = power_meter.read
            measured_uW = power_W * 1e6
            if abs(measured_uW - target_power_uW) <= tolerance:
                break
            adjustment_factor = target_power_uW / measured_uW if measured_uW != 0 else 1.0
            new_setting = current_laser_setting * adjustment_factor

            # Clamp the new setting between 0 and 100%
            new_setting = min(max(new_setting, 0), 100)

            Laser.set_power(new_setting)
            current_laser_setting = new_setting
            time.sleep(0.5)
            iteration += 1

        # Log the calibrated starting power
        power_W = power_meter.read
        initial_power_uW = power_W * 1e6
        log_calibration("Start", starting_wavelength, current_laser_setting, initial_power_uW)
        calibration_results.append((starting_wavelength, current_laser_setting, initial_power_uW))
        status_label.config(text=f"Status: Initial Power Calibrated = {initial_power_uW:.1f} µW at {starting_wavelength:.1f} nm")

        # Calibration parameters for wavelength stepping
        NumberOfSteps = 85   # Number of calibration steps (can be increased)
        Step = 5             # Wavelength step size in nm
        min_wavelength = 400
        max_wavelength = 835

        for i in range(NumberOfSteps):
            # Calculate new filter setpoints to achieve the next wavelength step
            new_short_setpoint = Filter.short_setpoint + Step
            new_long_setpoint = Filter.long_setpoint + Step
            proposed_wavelength = (new_short_setpoint + new_long_setpoint) / 2

            # Check if we're within acceptable wavelength limits
            if proposed_wavelength < min_wavelength or proposed_wavelength > max_wavelength:
                status_label.config(text=f"Status: Reached wavelength limit at step {i+1}")
                break

            # Update filter settings
            Filter.short_setpoint = new_short_setpoint
            Filter.long_setpoint = new_long_setpoint

            time.sleep(0.5)  # Wait for filter to settle

            # Feedback loop: adjust laser power until measured output is within tolerance of target power
            iteration = 0
            while iteration < max_iterations:
                power_W = power_meter.read
                measured_uW = power_W * 1e6
                if abs(measured_uW - target_power_uW) <= tolerance:
                    break
                adjustment_factor = target_power_uW / measured_uW if measured_uW != 0 else 1.0
                new_setting = current_laser_setting * adjustment_factor

                # Clamp new setting to valid range
                new_setting = min(max(new_setting, 0), 100)
                Laser.set_power(new_setting)
                current_laser_setting = new_setting
                time.sleep(0.5)
                iteration += 1

            # Final measurement after feedback
            power_W = power_meter.read
            measured_uW = power_W * 1e6
            current_wavelength = proposed_wavelength
            log_calibration(i+1, current_wavelength, current_laser_setting, measured_uW)
            calibration_results.append((current_wavelength, current_laser_setting, measured_uW))
            status_label.config(text=f"Calibrated step {i+1}: {current_wavelength:.1f} nm, Laser = {current_laser_setting:.1f}%, Power = {measured_uW:.1f} µW")
            time.sleep(2)  # Pause before next step

        Laser.set_emission(False)
        status_label.config(text="Calibration completed.")
        
        # After calibration is complete, plot the calibration curve.
        plot_calibration_curve(calibration_results)

    # Function to start calibration in a separate thread
    def start_calibration():
        threading.Thread(target=run_calibration, daemon=True).start()

    # Button to start the calibration routine
    start_button = ttk.Button(root, text="Start Calibration", command=start_calibration)
    start_button.pack(pady=10)

    # Button to export calibration data
    export_button = ttk.Button(root, text="Export Data", command=lambda: export_calibration_data(calibration_results))
    export_button.pack(pady=10)

    # Button to perform interpolation on calibration data
    interp_button = ttk.Button(root, text="Interpolate", command=interpolate_calibration)
    interp_button.pack(pady=10)

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()