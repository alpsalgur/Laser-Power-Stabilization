import pyvisa
from ThorlabsPM100 import ThorlabsPM100

rm = pyvisa.ResourceManager()  # Let PyVISA choose the available backend
# resources = rm.list_resources()
# print("Available VISA Resources:", resources)

inst = rm.open_resource('USB0::0x1313::0x8078::P0017991::INSTR')
power_meter = ThorlabsPM100(inst=inst)

# print(power_meter.read) # Read-only property
# print(power_meter.sense.average.count) # read property
# power_meter.sense.average.count = 10 # write property
# power_meter.system.beeper.immediate() # method

# Read the current power measurement
power = power_meter.read
print(f"Current Power: {power} W")