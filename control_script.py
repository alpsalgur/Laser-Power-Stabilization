import time
import pyvisa
from ThorlabsPM100 import ThorlabsPM100
from nkt_tools.extreme import Extreme
from nkt_tools.varia import Varia

rm = pyvisa.ResourceManager()  # Let PyVISA choose the available backend
inst = rm.open_resource('USB0::0x1313::0x8078::P0017991::INSTR')
power_meter = ThorlabsPM100(inst=inst)

# Coloring for text
GREEN = "\033[32m"
CYAN = "\033[36m"
RESET = "\033[0m"

# Setting up the laser (SuperK Extreme) and the filter (SuperK Varia)
Laser = Extreme()
Filter = Varia()

# Parameters
Step = 5                  # Step size for the wavelength increase (nm)
NumberOfSteps = 10        # Number of steps
StepDuration = 2          # Duration of each step (seconds)

# Target power (in µW) and feedback settings
target_power_uW = 109.0   # Target power in microwatts (µW)
tolerance = 0.5           # Tolerance in µW
max_iterations = 10       # Maximum number of feedback iterations per step

# Initialize laser settings
initial_laser_power_setting = 30.0  # initial power setting (percentage)
Laser.set_power(initial_laser_power_setting)
Laser.set_emission(True)            # Turn on the emission

# Initialize filter settings (set initial short and long setpoints)
Filter.short_setpoint = 527  # Initial short wave pass value
Filter.long_setpoint = 537   # Initial long wave pass value

starting_wavelength = (Filter.short_setpoint + Filter.long_setpoint) / 2
print(f"{GREEN}Starting wavelength is: {starting_wavelength} nm{RESET}")

# Use a variable to keep track of the current laser power setting
current_laser_setting = initial_laser_power_setting

# Loop through the number of steps and adjust both short and long setpoints
for i in range(NumberOfSteps):
    # Increase filter setpoints by the step size
    new_short_setpoint = Filter.short_setpoint + Step
    new_long_setpoint = Filter.long_setpoint + Step

    # Update filter setpoints
    Filter.short_setpoint = new_short_setpoint
    Filter.long_setpoint = new_long_setpoint

    # Compute and print the actual wavelength (average of setpoints)
    actual_wavelength = (new_short_setpoint + new_long_setpoint) / 2
    print(f"{GREEN}Step {i+1}: Set short setpoint to {new_short_setpoint} nm, "
          f"long setpoint to {new_long_setpoint} nm. Actual wavelength is: {actual_wavelength} nm{RESET}")

    # Allow the system to settle after changing the filter settings
    time.sleep(.5)

    # Feedback loop: Adjust laser power to reach the target power reading
    iteration = 0
    while iteration < max_iterations:
        # Read power (in Watts) and convert to µW
        power_W = power_meter.read
        measured_uW = power_W * 1e6

        # If within tolerance, break out of the loop
        if abs(measured_uW - target_power_uW) <= tolerance:
            break

        # Compute adjustment factor (avoid division by zero)
        if measured_uW == 0:
            adjustment_factor = 1.0
        else:
            adjustment_factor = target_power_uW / measured_uW

        # Calculate new laser power setting using a simple proportional controller
        new_setting = current_laser_setting * adjustment_factor
        Laser.set_power(new_setting)
        current_laser_setting = new_setting

        time.sleep(0.5)  # Wait for the laser to respond
        iteration += 1

    # Final power measurement after adjustments
    power_W = power_meter.read
    measured_uW = power_W * 1e6
    print(f"{CYAN}Current Power: {measured_uW:.1f} µW{RESET}")

    # Wait for the remainder of the step duration
    time.sleep(StepDuration)

# Turn off the laser emission after the sequence
Laser.set_emission(False)

# Print final status
Laser.print_status()
Filter.print_status()

print(f"{GREEN}Sequence completed successfully.{RESET}")