import time
import pyvisa
from ThorlabsPM100 import ThorlabsPM100
from nkt_tools.extreme import Extreme
from nkt_tools.varia import Varia

rm = pyvisa.ResourceManager()  # Let PyVISA choose the available backend
# resources = rm.list_resources()
# print("Available VISA Resources:", resources)

inst = rm.open_resource('USB0::0x1313::0x8078::P0017991::INSTR')
power_meter = ThorlabsPM100(inst=inst)

# print(power_meter.read) # Read-only property
# print(power_meter.sense.average.count) # read property
# power_meter.sense.average.count = 10 # write property
# power_meter.system.beeper.immediate() # method

# Coloring for text
GREEN = "\033[32m"
CYAN = "\033[36m"
RESET = "\033[0m"

# Setting up the laser (SuperK Extreme) and the filter (SuperK Varia)
Laser = Extreme()
Filter = Varia()

# Start wavelength in nm
InitialWavelength = 532

# Step size for the wavelength increase
Step = 5

# Number of steps that should be executed
NumberOfSteps = 10  # Adjust based on your needs

# Duration of each step
StepDuration = 2  # 5 seconds

# Initialize laser settings
Laser.set_power(30)  # Set power to 30%
Laser.set_emission(True)  # Turn on the emission

# Initialize filter settings (set initial short and long setpoints)
Filter.short_setpoint = 527  # Set initial short wave pass value
Filter.long_setpoint = 537   # Set initial long wave pass value

starting_wavelength = (Filter.short_setpoint + Filter.long_setpoint)/2 # Starting wavelength

# Print the starting value for wavelength
print(f"{GREEN}Starting wavelength is: {starting_wavelength}{RESET}")

# Loop through the number of steps and adjust both short and long setpoints
for i in range(NumberOfSteps):
    # Increase both short and long setpoints by the step size
    new_short_setpoint = Filter.short_setpoint + Step
    new_long_setpoint = Filter.long_setpoint + Step
    
    # Set the new short and long setpoints on the Varia filter
    Filter.short_setpoint = new_short_setpoint
    Filter.long_setpoint = new_long_setpoint
    
    # Print current wavelengths
    print(f"{GREEN}Step {i + 1}: Set short setpoint to {new_short_setpoint} nm, long setpoint to {new_long_setpoint} nm. Actual wavelength is: {(new_short_setpoint + new_long_setpoint)/2}{RESET}")
    
    # Sleep for precise power output
    time.sleep(.5)

    # Read the current power measurement
    power_W = power_meter.read  # Power in Watts
    power_uW = power_W * 1e6    # Convert to µW

    # # Print formatted output
    # print(f"{CYAN}Current Power: {power_uW:.2f} µW{RESET}")

    print(f"{CYAN}Current Power: {power_uW} µW{RESET}")

    # Wait for the step duration
    time.sleep(StepDuration)  # Seconds for sleep

# Turn off the emission after completing the sequence
Laser.set_emission(False)

# Print final status
Laser.print_status()
Filter.print_status()

print(f"{GREEN}Sequence completed successfully.{RESET}")