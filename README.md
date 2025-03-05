# Laser Power Stabilization

## Overview
This project is developed as part of a **bachelor thesis** focused on the **automation of laser power stabilization** across a tunable laser spectrum. The system integrates a **laser source**, a **power meter**, and a **filter system**, all controlled through a **Python-based GUI**.

## Objectives
The main goals of this project include:

1. **Familiarization with Hardware & Software Control**
   - Understanding the operation of tunable lasers and power meters.
   - Establishing software-based control over these components.

2. **Hardware Setup & Interfacing**
   - Designing a setup that interconnects the power meter, photodiode, and tunable laser.
   - Enabling **bi-directional communication** between the hardware and software.

3. **Software Development & Automation**
   - Implementing **data acquisition and control algorithms**.
   - Using available libraries (e.g., **PyVISA, ThorlabsPM100, and NKT tools**) for device communication.
   - Developing a feedback loop that stabilizes laser power dynamically.

4. **Testing & Validation**
   - Creating a **test protocol** to verify the efficiency of power control.
   - Performing real-world testing under different wavelength conditions.

5. **Graphical User Interface (GUI)**
   - Designing and developing a **user-friendly application**.
   - Visualizing real-time power adjustments and wavelength shifts.

## Technology Stack
- **Programming Language:** Python
- **GUI Framework:** Tkinter
- **Hardware Communication:** PyVISA, ThorlabsPM100, NKT tools
- **Instruments:** NKT Photonics Extreme, Varia filter, Thorlabs Power Meter

## Features
✅ **Automatic laser power adjustment** to maintain target power levels.<br>
✅ **Real-time data visualization** via GUI.<br>
✅ **Tunable wavelength control** with feedback stabilization.<br>
✅ **Bi-directional hardware communication** for dynamic adjustments.<br>
✅ **User-configurable parameters** (target power, wavelength range, step size).<br>

## Installation
To install the required dependencies, run:
```sh
pip install -r requirements.txt
```

## Usage
Run the main script to start the GUI:
```sh
python main.py
```

## Acknowledgment
This project is part of a **bachelor thesis** focusing on advanced laser stabilization methods for applications in bio-imaging, semiconductor inspection, and scientific instrumentation.
