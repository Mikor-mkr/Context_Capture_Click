# Context Capture Click (CCC)
A utility tool for capturing and converting coordinates between different formats, designed to work with Context Capture and progeCAD software.

## Description
Context Capture Click (CCC) is a PyQt5-based desktop application that helps surveyors and GIS professionals to:

* Extract coordinates from Context Capture using OCR functionality
* Convert coordinates between different formats (XYZ, AutoCAD)
* Open captured locations in Google Street View
* Send coordinates directly to progeCAD for point creation

## Features
* F1 hotkey OCR capture from "Measurements" window
* Coordinate format conversion
* One-click Street View opening with automatic projection transformation (Greek grid EPSG:2100 to WGS84)
* Integration with progeCAD for point placement
* Toggle Z-value inclusion/exclusion
* Always-on-top window for easy access

## Installation
### Prerequisites
```
pip install PyQt5 numpy pyproj keyboard pywinctl pyperclip pyautogui pygetwindow
```

## Usage
1. Run the application: `python CCC.py`
2. Click "Enable F1 OCR Capture" to activate the F1 hotkey
3. Press F1 while the "Measurements" window is visible to capture coordinates
4. Use the conversion buttons as needed:
    * "Convert CAD" - Format coordinates for CAD input
    * "Convert XYZ" - Process XYZ coordinates
    * "Street View" - Open the location in Google Street View

## Creating an Executable (.exe)
To create a standalone executable that includes all dependencies:

1. Install PyInstaller:
```
pip install pyinstaller
```

2. Create the executable:
```
pyinstaller --onefile --windowed --add-data "Map-Greece-Logo_white.png;." CCC.py
```

For a more optimized build with icon:
```
pyinstaller --onefile --windowed --icon=your_icon.ico --add-data "Map-Greece-Logo_white.png;." CCC.py
```

The executable will be created in the `dist` folder.
