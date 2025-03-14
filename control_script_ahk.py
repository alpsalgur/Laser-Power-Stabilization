import pyautogui
import time
import subprocess
from nkt_tools.extreme import Extreme
from nkt_tools.varia import Varia

# Setting up the laser and the filter
Laser = Extreme()
Filter = Varia()

# Start wavelength in nm
InitialWavelength = 532

# Step size with the wavelength is increased
Step = 5

# Number of steps that should be executed
NumberOfSteps = 10  # 52

# Duration of each step
StepDurationMs = 5  # 5 seconds

# Start CONTROL software
subprocess.Popen('"C:\\Program Files (x86)\\NKT Photonics\\CONTROL\\CONTROL.exe"')
time.sleep(10)  # Wait 10 seconds

# Activate the window of the CONTROL program (requires window title to be consistent)
pyautogui.getWindowsWithTitle('CONTROL - Version')[0].activate()

time.sleep(0.625)
# Send ALT + C to connect to COM3 device
pyautogui.hotkey('alt', 'c')
time.sleep(0.2)
pyautogui.press('down')
time.sleep(0.2)
pyautogui.press('enter')
time.sleep(10)

# ***UNFORTUNATELY INTERLOCK RESET MUST BE DONE MANUALLY FOR NOW***
# Interlock reset
# try:
#     Laser.set_interlock(value=1)
#     print("Interlock reset successful.")
# except Exception as e:
#     print(f"Failed to reset interlock: {e}")


# try:
#     status = Laser.interlock_status
#     print(f"Interlock Status Raw Data: {status}")
#     if len(status) < 2:
#         print("Error: Received data has fewer than 2 bytes.")
#     else:
#         lsb, description = status
#         print(f"Interlock Status: LSB = {lsb}, Description = {description}")
# except Exception as e:
#     print(f"Error reading interlock status: {e}")


# Navigate to required options using tab and down keys
pyautogui.press('tab')
time.sleep(1)
pyautogui.press('down')
time.sleep(1)

# Loop through 7 tab presses
for _ in range(7):
    pyautogui.press('tab')
    time.sleep(0.5)

# Set Power value
time.sleep(1)
pyautogui.write('30')
time.sleep(1)

# Loop through 5 more tab presses
for _ in range(5):
    pyautogui.press('tab')
    time.sleep(0.5)

# Select VARIA entry
time.sleep(3)  # Wait for some reason
pyautogui.press('down')
time.sleep(0.5)

# 5x Tab to Center
for _ in range(5):
    pyautogui.press('tab')
    time.sleep(0.5)

# Set Wavelength Center
pyautogui.write(str(InitialWavelength))
time.sleep(1)

# Loop through 17 more tabs
for _ in range(17):
    pyautogui.press('tab')
    time.sleep(0.5)

# Press Emission button
pyautogui.press('space')
time.sleep(1)

# Loop through 8 more tabs
for _ in range(8):
    pyautogui.press('tab')
    time.sleep(0.5)

time.sleep(StepDurationMs)

# Loop through NumberOfSteps
for i in range(NumberOfSteps):
    # Set Wavelength Center
    new_wavelength = InitialWavelength + ((i + 1) * Step)
    pyautogui.write(str(new_wavelength))
    time.sleep(0.5)
    
    # Go one field up and back to select whole value
    pyautogui.hotkey('shift', 'tab')
    time.sleep(0.5)
    pyautogui.press('tab')
    time.sleep(StepDurationMs / 1000)  # Convert ms to seconds for pyautogui's sleep