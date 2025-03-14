import tkinter as tk
from tkinter import ttk
import threading
import time
import pyvisa
from ThorlabsPM100 import ThorlabsPM100
from nkt_tools.extreme import Extreme
from nkt_tools.varia import Varia

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Laser Power Feedback Sequence")

    # Create a main frame for padding and layout
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(expand=True, fill="both")

    # Add a title label
    title_label = ttk.Label(main_frame, text="Laser Power Feedback Sequence", 
                            font=("Helvetica", 16, "bold"))
    title_label.pack(pady=(0, 10))

    # Create a Treeview to display measurements in a table
    columns = ("Step", "Short SP", "Long SP", "Wavelength (nm)", "Power (µW)")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, stretch=True, anchor="center")
    tree.pack(side="left", fill="both", expand=True)

    # Add a scrollbar for the Treeview
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="left", fill="y")

    # A status label to show ongoing status (e.g., current power)
    status_label = ttk.Label(root, text="Status: Idle", font=("Helvetica", 12))
    status_label.pack(pady=10)

    # Hardware Setup (similar to your existing code)
    rm = pyvisa.ResourceManager()
    inst = rm.open_resource('USB0::0x1313::0x8078::P0017991::INSTR')
    power_meter = ThorlabsPM100(inst=inst)

    Laser = Extreme()
    Filter = Varia()

    # Define a function to insert rows into the table
    def log_measurement(step, short_sp, long_sp, wavelength, power_uw):
        """Inserts one row of data into the Treeview."""
        tree.insert(
            "", "end",
            values=(
                step,
                f"{short_sp:.1f}",
                f"{long_sp:.1f}",
                f"{wavelength:.1f}",
                f"{power_uw:.1f}"
            )
        )

    def calibrate_initial_power(target_power_uW, tolerance, max_iterations):
        iteration = 0
        current_laser_setting = 30.0
        Laser.set_power(current_laser_setting)
        Laser.set_emission(True)
        time.sleep(3)

        while iteration < max_iterations:
            power_W = power_meter.read
            measured_uW = power_W * 1e6

            if abs(measured_uW - target_power_uW) <= tolerance:
                break

            adjustment_factor = target_power_uW / measured_uW if measured_uW != 0 else 1.0
            new_setting = current_laser_setting * adjustment_factor
            Laser.set_power(new_setting)
            current_laser_setting = new_setting

            time.sleep(0.5)
            iteration += 1

        return power_meter.read * 1e6

    # Main sequence logic in a separate thread
    def run_sequence():
        status_label.config(text="Status: Initializing hardware...")

        # --- Parameters ---
        Step = 5
        NumberOfSteps = 10
        StepDuration = 2
        target_power_uW = 10.0
        tolerance = 0.5
        max_iterations = 10

        # --- Laser and Filter setup ---
        initial_laser_power_setting = 30.0
        Laser.set_power(initial_laser_power_setting)
        Laser.set_emission(True)
        current_laser_setting = initial_laser_power_setting

        Filter.short_setpoint = 527
        Filter.long_setpoint = 537
        starting_wavelength = (Filter.short_setpoint + Filter.long_setpoint) / 2

        # --- Measure initial power before the sequence starts ---
        initial_power_uW = calibrate_initial_power(target_power_uW, tolerance, max_iterations)
        log_measurement("Start", Filter.short_setpoint, Filter.long_setpoint, starting_wavelength, initial_power_uW)
        status_label.config(text=f"Status: Initial Power Calibrated = {initial_power_uW:.1f} µW")

        # Optional range checks
        min_wavelength = 500
        max_wavelength = 800

        for i in range(NumberOfSteps):
            # Calculate new setpoints
            new_short_setpoint = Filter.short_setpoint + Step
            new_long_setpoint = Filter.long_setpoint + Step
            proposed_wavelength = (new_short_setpoint + new_long_setpoint) / 2

            # Check if we're within wavelength limits
            if proposed_wavelength < min_wavelength or proposed_wavelength > max_wavelength:
                status_label.config(text=f"Status: Reached wavelength limit at step {i+1}")
                break

            # Update the filter
            Filter.short_setpoint = new_short_setpoint
            Filter.long_setpoint = new_long_setpoint
            actual_wavelength = proposed_wavelength

            time.sleep(0.5)  # Wait for filter to settle

            # --- Feedback loop to maintain target power ---
            iteration = 0
            while iteration < max_iterations:
                power_W = power_meter.read
                measured_uW = power_W * 1e6

                # Check if we're within tolerance
                if abs(measured_uW - target_power_uW) <= tolerance:
                    break

                # Adjust laser power proportionally
                if measured_uW == 0:
                    adjustment_factor = 1.0
                else:
                    adjustment_factor = target_power_uW / measured_uW

                new_setting = current_laser_setting * adjustment_factor
                Laser.set_power(new_setting)
                current_laser_setting = new_setting

                time.sleep(0.5)
                iteration += 1

            # Final measurement after feedback
            power_W = power_meter.read
            measured_uW = power_W * 1e6

            # Insert row into the table
            log_measurement(
                i+1,
                Filter.short_setpoint,
                Filter.long_setpoint,
                actual_wavelength,
                measured_uW
            )
            status_label.config(text=f"Status: Step {i+1}, Power = {measured_uW:.1f} µW")

            # Sleep for the duration of the step
            time.sleep(StepDuration)

        # Turn off laser
        Laser.set_emission(False)
        status_label.config(text="Status: Sequence completed.")

    # 10. Function to start the sequence in a separate thread
    def start_sequence():
        threading.Thread(target=run_sequence, daemon=True).start()

    # 11. A button to kick off the sequence
    start_button = ttk.Button(root, text="Start Sequence", command=start_sequence)
    start_button.pack(pady=10)

    # 12. Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()