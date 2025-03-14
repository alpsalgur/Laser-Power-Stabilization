import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
# import threading
# import time
import csv
import numpy as np
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from nkt_tools.extreme import Extreme
from nkt_tools.varia import Varia

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Open-Loop Laser Control Using Calibration Data")

    # Create a main frame for padding and layout
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(expand=True, fill="both")

    # Add a title label
    title_label = ttk.Label(main_frame, text="Open-Loop Laser Control", 
                            font=("Helvetica", 16, "bold"))
    title_label.pack(pady=(0, 10))

    # Create a Treeview to display calibration data in a table
    columns = ("Wavelength (nm)", "Laser Setting (%)", "Measured Power (µW)")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, stretch=True, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    # Add a scrollbar for the Treeview
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="left", fill="y")

    # A status label to show ongoing status
    status_label = ttk.Label(root, text="Status: Idle", font=("Helvetica", 12))
    status_label.pack(pady=10)

    # Additional frame for extra buttons
    button_frame = ttk.Frame(root, padding="10")
    button_frame.pack()

    # Setup Laser and Filter (hardware for open-loop control)
    Laser = Extreme()
    Filter = Varia()

    # List to store calibration results, each element is a tuple: (wavelength, laser_setting, measured_power)
    calibration_results = []

    # Function to load calibration data from CSV
    def load_calibration_data(filename="calibration_data.csv"):
        nonlocal calibration_results
        calibration_results.clear()
        # Clear Treeview as well
        for item in tree.get_children():
            tree.delete(item)
        try:
            with open(filename, mode="r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    wavelength = float(row["Wavelength (nm)"])
                    laser_setting = float(row["Laser Setting (%)"])
                    measured_power = float(row["Measured Power (µW)"])
                    calibration_results.append((wavelength, laser_setting, measured_power))
                    tree.insert("", "end", values=(f"{wavelength:.1f}", f"{laser_setting:.1f}", f"{measured_power:.1f}"))
            status_label.config(text=f"Loaded calibration data from {filename}.")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    # Function to plot the calibration curve using matplotlib
    def plot_calibration_curve(cal_data):
        if not cal_data:
            messagebox.showerror("Plot Error", "No calibration data available!")
            return
        wavelengths = [item[0] for item in cal_data]
        laser_settings = [item[1] for item in cal_data]
        measured_powers = [item[2] for item in cal_data]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
        fig.suptitle("Calibration Curve")
        
        ax1.plot(wavelengths, measured_powers, 'bo-', label="Measured Power (µW)")
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel("Measured Power (µW)")
        ax1.legend()
        ax1.grid(True)
        
        ax2.plot(wavelengths, laser_settings, 'ro-', label="Laser Setting (%)")
        ax2.set_xlabel("Wavelength (nm)")
        ax2.set_ylabel("Laser Setting (%)")
        ax2.legend()
        ax2.grid(True)
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.show()

    # Function to create interpolation functions from calibration data
    def create_interpolation_functions(cal_data):
        wavelengths = np.array([item[0] for item in cal_data])
        laser_settings = np.array([item[1] for item in cal_data])
        measured_powers = np.array([item[2] for item in cal_data])
        laser_setting_interp = interp1d(wavelengths, laser_settings, kind='linear', fill_value="extrapolate")
        measured_power_interp = interp1d(wavelengths, measured_powers, kind='linear', fill_value="extrapolate")
        return laser_setting_interp, measured_power_interp

    # Function to perform interpolation and show result
    def interpolate_calibration():
        if not calibration_results:
            messagebox.showerror("Interpolation Error", "No calibration data available!")
            return
        try:
            wavelength_input = simpledialog.askfloat("Interpolate", "Enter desired wavelength (nm):")
            if wavelength_input is None:
                return
            laser_interp, power_interp = create_interpolation_functions(calibration_results)
            estimated_setting = float(laser_interp(wavelength_input))
            estimated_power = float(power_interp(wavelength_input))
            messagebox.showinfo("Interpolation Result",
                                f"At {wavelength_input:.1f} nm:\nEstimated Laser Setting: {estimated_setting:.1f}%\nEstimated Power: {estimated_power:.1f} µW")
        except Exception as e:
            messagebox.showerror("Interpolation Error", str(e))

    # Function to set the laser power based on the calibration data (open-loop mode)
    def set_laser_for_wavelength():
        if not calibration_results:
            messagebox.showerror("Error", "No calibration data loaded!")
            return
        try:
            desired_wavelength = simpledialog.askfloat("Set Laser", "Enter desired wavelength (nm):")
            if desired_wavelength is None:
                return
            laser_interp, _ = create_interpolation_functions(calibration_results)
            required_setting = float(laser_interp(desired_wavelength))
            # Clamp the setting between 0 and 100%
            required_setting = min(max(required_setting, 0), 100)
            Laser.set_power(required_setting)
            status_label.config(text=f"Laser set to {required_setting:.1f}% for {desired_wavelength:.1f} nm.")
            messagebox.showinfo("Laser Setting", f"Laser set to {required_setting:.1f}% for {desired_wavelength:.1f} nm.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Buttons for open-loop mode
    load_button = ttk.Button(button_frame, text="Load Calibration Data", command=lambda: load_calibration_data())
    load_button.pack(side="left", padx=5, pady=5)

    plot_button = ttk.Button(button_frame, text="Plot Calibration Curve", command=lambda: plot_calibration_curve(calibration_results))
    plot_button.pack(side="left", padx=5, pady=5)

    interp_button = ttk.Button(button_frame, text="Interpolate Calibration", command=interpolate_calibration)
    interp_button.pack(side="left", padx=5, pady=5)

    set_laser_button = ttk.Button(button_frame, text="Set Laser for Wavelength", command=set_laser_for_wavelength)
    set_laser_button.pack(side="left", padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()