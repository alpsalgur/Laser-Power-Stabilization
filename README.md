# Laser Power Stabilization

> ⚠️ **Note:** This repository contains the complete Python implementation developed for a bachelor thesis project on automated laser power stabilization using NKT Photonics hardware. It provides a fully functional and tested system for performing both calibration and measurement procedures.

## Overview

This project presents a comprehensive system for **automated power stabilization of a tunable supercontinuum laser**, utilizing a Python-based interface alongside real-time feedback algorithms. The system integrates and controls an **NKT Photonics SuperK Extreme laser**, a **SuperK VARIA tunable filter**, and a **Thorlabs PM100D power meter**.

It enables precise calibration and stabilization of the laser output power across a defined wavelength range, and supports automated measurement sweeps with high precision and repeatability.

## Objectives

1. **Hardware and Software Integration**  
   - Interfacing with the NKT Photonics CONTROL software using the `nkt-tools` library.  
   - Communicating with the Thorlabs PM100D power meter via `PyVISA`.  

2. **Automation of Laser Power Stabilization**  
   - Implementing an adaptive feedback loop to dynamically adjust laser power.  
   - Using calibration data and interpolation to predict optimal power settings.  

3. **Measurement Routine**  
   - Executing wavelength sweeps over a user-defined range.  
   - Applying calibration-based power corrections in open-loop mode.  

4. **Graphical User Interface (GUI)**  
   - A Tkinter-based GUI for real-time interaction.  
   - Options for calibration, measurement, data export, and live status monitoring.

## Technology Stack

| Component          | Description                                    |
|--------------------|------------------------------------------------|
| Language           | Python 3.9                                     |
| GUI Framework      | Tkinter                                        |
| Communication      | PyVISA, ThorlabsPM100, nkt-tools               |
| Visualization      | matplotlib                                     |
| Control Hardware   | NKT Photonics SuperK Extreme, VARIA, CONNECT   |
| Sensing Hardware   | Thorlabs PM100D Power Meter                    |

## Features

✅ **Calibration Routine** with power feedback loop  
✅ **Real-time interpolation** for automated measurement  
✅ **Laser and filter control** via Python  
✅ **Measurement sweep interface** with configurable parameters  
✅ **Graph export and CSV output**  
✅ **GUI with logging and visual feedback**

## Installation

1. **Clone the repository:**  

   ```bash
   git clone https://github.com/alpsalgur/Laser-Power-Stabilization.git
   cd Laser-Power-Stabilization

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt

4. **Install the ThorlabsPM100 driver (manually):**

   ```bash
   git clone https://github.com/clade/ThorlabsPM100.git
   cd ThorlabsPM100
   python setup.py install

> **Note:** The nkt-tools package is available via pip and includes the necessary SDK bindings.

## Usage

**Start the application with:**

   ```bash
   python main.py
   ```

The GUI will prompt for a target power and allow calibration and measurement across wavelengths.

## Acknowledgments

This project was developed as part of a bachelor thesis at *Czech Technical University in Prague*, supervised by *Egor Ukraintsev, Ph.D.*, and carried out in cooperation with the NKT Photonics CONTROL software platform.
