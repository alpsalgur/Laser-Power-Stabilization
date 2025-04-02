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
from datetime import datetime

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Laser Power Stabilization System")

    # Create a main frame for padding and layout
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(expand=True, fill="both")

    # Add a title label
    title_label = ttk.Label(main_frame, text="Laser Power Stabilization System", 
                          font=("Helvetica", 16, "bold"))
    title_label.pack(pady=(0, 10))

    # Create a Treeview to display data
    columns = ("Process", "Wavelength (nm)", "Laser Power Setting (%)", "Measured Power (µW)")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, stretch=True, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="left", fill="y")

    # Status label
    status_label = ttk.Label(root, text="Status: Idle", font=("Helvetica", 12))
    status_label.pack(pady=10)

    # Button frame
    button_frame = ttk.Frame(root, padding="10")
    button_frame.pack()

    # Hardware Setup
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource('USB0::0x1313::0x8078::P0017991::INSTR')
    power_meter = ThorlabsPM100(inst=inst)
    Laser = Extreme()
    Filter = Varia()

    # Constants
    MIN_LASER_POWER = 10.0  # Minimum allowed laser power setting (10%) by default
    min_wavelength = 400
    max_wavelength = 835
    NumberOfSteps = 85   # Number of calibration steps

    # Calibration data storage
    calibration_results = []

    def log_entry(step, wavelength, laser_setting, measured_power):
        item_id = tree.insert("", "end", values=(step, f"{wavelength:.1f}", 
                             f"{laser_setting:.1f}", f"{measured_power:.1f}" if measured_power else "N/A"))
        tree.see(item_id)  # Auto-scroll to new entry

    def add_separator():
        item_id = tree.insert("", "end", values=("─"*10, "─"*10, "─"*10, "─"*10))
        tree.see(item_id)  # Auto-scroll to separator

    def plot_calibration_curve(cal_data):
        if not cal_data:
            messagebox.showerror("Error", "No calibration data to plot")
            return
            
        wavelengths = [item[0] for item in cal_data]
        laser_settings = [item[1] for item in cal_data]
        measured_powers = [item[2] for item in cal_data]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10))
        fig.suptitle("Calibration Curve")

        ax1.plot(wavelengths, measured_powers, 'bo-', label="Measured Power")
        ax1.set_xlabel("Wavelength (nm)")
        ax1.set_ylabel("Power (µW)")
        ax1.grid(True)

        ax2.plot(wavelengths, laser_settings, 'ro-', label="Laser Setting")
        ax2.set_xlabel("Wavelength (nm)")
        ax2.set_ylabel("Setting (%)")
        ax2.grid(True)

        plt.tight_layout()
        plt.show()

    def export_data(data, default_name):
        if not data:
            messagebox.showerror("Error", "No data to export")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{default_name}_{timestamp}.csv"
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Wavelength (nm)", "Laser Setting (%)", "Measured Power (µW)"])
                writer.writerows(data)
            messagebox.showinfo("Export Successful", f"Data saved to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def create_interpolation():
        if not calibration_results:
            messagebox.showerror("Error", "No calibration data available")
            return None
        wavelengths = np.array([x[0] for x in calibration_results])
        settings = np.array([x[1] for x in calibration_results])
        return interp1d(wavelengths, settings, kind='linear', fill_value="extrapolate")

    def run_calibration():
        try:
            status_label.config(text="Starting calibration...")
            target_power = 100.0  # µW
            tolerance = 0.5
            max_iterations = 10

            # Initial setup
            Filter.short_setpoint = 400
            Filter.long_setpoint = 410
            Laser.set_power(max(30.0, MIN_LASER_POWER))  # Enforce minimum
            Laser.set_emission(True)
            time.sleep(3)

            # Initial calibration
            current_setting = 30.0
            for _ in range(max_iterations):
                power = power_meter.read * 1e6
                if abs(power - target_power) <= tolerance:
                    break
                current_setting *= target_power / power
                current_setting = max(MIN_LASER_POWER, min(100, current_setting))
                Laser.set_power(current_setting)
                time.sleep(0.5)

            initial_wl = (Filter.short_setpoint + Filter.long_setpoint) / 2
            log_entry("Calibration", initial_wl, current_setting, power)
            calibration_results.append((initial_wl, current_setting, power))

            # Wavelength sweep
            for step in range(NumberOfSteps):
                new_short = Filter.short_setpoint + 5
                new_long = Filter.long_setpoint + 5
                if (new_short + new_long)/2 > max_wavelength:
                    break

                Filter.short_setpoint = new_short
                Filter.long_setpoint = new_long
                time.sleep(0.5)

                # Power adjustment
                for _ in range(max_iterations):
                    power = power_meter.read * 1e6
                    if abs(power - target_power) <= tolerance:
                        break
                    current_setting *= target_power / power
                    current_setting = max(MIN_LASER_POWER, min(100, current_setting))
                    Laser.set_power(current_setting)
                    time.sleep(0.5)

                current_wl = (new_short + new_long)/2
                log_entry("Calibration", current_wl, current_setting, power)
                calibration_results.append((current_wl, current_setting, power))
                status_label.config(text=f"Calibrated {current_wl:.1f}nm")
                time.sleep(1)

            Laser.set_emission(False)
            status_label.config(text="Calibration complete")
            plot_calibration_curve(calibration_results)
            root.after(0, add_separator)
            
        except Exception as e:
            Laser.set_emission(False)
            messagebox.showerror("Calibration Error", str(e))
            status_label.config(text="Calibration failed")

    def start_measurement():
        # Get parameters in main thread with focus enforcement
        start_wl = simpledialog.askfloat("Start Wavelength", "Enter start (nm):",
                                        parent=root,
                                        minvalue=min_wavelength, 
                                        maxvalue=max_wavelength)
        if start_wl is None: return
        
        # Bring main window back to front after first dialog
        root.lift()
        
        end_wl = simpledialog.askfloat("End Wavelength", "Enter end (nm):",
                                      parent=root,
                                      minvalue=start_wl, 
                                      maxvalue=max_wavelength)
        if end_wl is None: return
        
        # Bring main window back to front again
        root.lift()
        
        step_size = simpledialog.askfloat("Step Size", "Enter step (nm):",
                                         parent=root,
                                         minvalue=1, 
                                         maxvalue=end_wl-start_wl)
        if step_size is None: return

        # Start thread with parameters
        threading.Thread(target=lambda: run_measurement(start_wl, end_wl, step_size), daemon=True).start()

    def run_measurement(start_wl, end_wl, step_size):
        try:
            if not calibration_results:
                root.after(0, lambda: messagebox.showerror("Error", "Perform calibration first!"))
                return

            interp_func = create_interpolation()
            calibrated_wls = [x[0] for x in calibration_results]
            min_cal_wl, max_cal_wl = min(calibrated_wls), max(calibrated_wls)

            Laser.set_emission(True)
            current_wl = start_wl
            num_steps = int((end_wl - start_wl)/step_size) + 1

            for step_idx in range(num_steps):
                short = round(current_wl - 5)
                long = round(current_wl + 5)
                if not (min_wavelength <= short <= max_wavelength-10):
                    root.after(0, lambda: messagebox.showerror("Error", "Wavelength out of range!"))
                    break

                Filter.short_setpoint = short
                Filter.long_setpoint = long
                time.sleep(0.5)

                setting = float(interp_func(current_wl))
                setting = max(MIN_LASER_POWER, min(100, setting))
                Laser.set_power(setting)
                
                if step_idx == 0:
                    time.sleep(10)  # 10-second stabilization for first step
                else: 
                    time.sleep(3)   # Normal stabilization for other steps

                root.after(0, lambda: log_entry("Measurement", current_wl, setting, None))
                root.after(0, lambda: status_label.config(
                    text=f"Measuring {current_wl:.1f}nm ({setting:.1f}%)"))

                if current_wl < min_cal_wl or current_wl > max_cal_wl:
                    root.after(0, lambda: messagebox.showwarning(
                        "Warning", "Extrapolating beyond calibration range!"))

                current_wl += step_size
                current_wl = round(current_wl, 1)

            Laser.set_emission(False)
            root.after(0, lambda: status_label.config(text="Measurement complete"))
            root.after(0, add_separator)

        except Exception as e:
            Laser.set_emission(False)
            root.after(0, lambda: messagebox.showerror("Measurement Error", str(e)))
            root.after(0, lambda: status_label.config(text="Measurement failed"))

    # Control buttons
    ttk.Button(button_frame, text="Calibrate", 
              command=lambda: threading.Thread(target=run_calibration, daemon=True).start(),
              width=15).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Measure", command=start_measurement,
              width=15).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Export Calibration", 
              command=lambda: export_data(calibration_results, "calibration"),
              width=20).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Plot Calibration", 
              command=lambda: plot_calibration_curve(calibration_results),
              width=20).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Exit", command=root.quit,
              width=10).pack(side="right", padx=5)

    root.mainloop()

if __name__ == "__main__":
    main()