# Context Capture Click

A utility tool for capturing, converting, and utilizing coordinate data across different platforms.

## Description

Context Capture Click (CCC) is a specialized tool designed for surveying and mapping professionals working with coordinate systems in Greece. It provides functionality to capture coordinates from measurement windows, convert between coordinate formats, and quickly visualize locations using Google Street View.

## Features

- **F1 Hotkey Coordinate Capture**: Capture coordinates from a "Measurements" window with one keystroke
- **Coordinate Format Conversion**: Convert captured coordinates for use in different applications
  - Convert to plain XYZ format
  - Convert to AutoCAD-compatible format (PO command)
- **Google Street View Integration**: Instantly view any location on Google Street View by converting Greek grid coordinates (EPSG:2100) to WGS84
- **VBA Integration**: Optional VBA macro for IntelliCAD integration that monitors clipboard for coordinate data

## Requirements

- Python 3.6+
- PyQt5
- pyproj
- keyboard
- pywinctl
- pyautogui

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/Context_Capture_Click.git
   cd Context_Capture_Click
   ```

2. Install required Python packages:
   ```
   pip install pyqt5 pyproj keyboard pywinctl pyautogui
   ```

3. Run the application:
   ```
   python CCC.py
   ```

### Creating Standalone Executable

For distributing to users without Python installed, you can create a standalone executable:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Create the executable:
   ```
   pyinstaller --onefile --windowed --icon=icon.ico --name="ContextCaptureClick" CCC.py
   ```

3. Find the executable in the `dist` folder

Additional options:
- Remove `--windowed` if you want to show console output for debugging
- Add `--add-data "path/to/resource;resource"` if your app needs additional files
- Use `--noconsole` instead of `--windowed` for newer PyInstaller versions

## Usage

### Python GUI Application

1. Launch the application (`python CCC.py`)
2. Enable F1 OCR Capture by clicking the button (turns red when active)
3. Press F1 when focused on a "Measurements" window to capture coordinates
4. Use the conversion buttons to format coordinates as needed:
   - "Convert XYZ" - Converts to simple space-delimited coordinates
   - "Convert CAD" - Formats coordinates for AutoCAD point creation (PO command)
5. Click "Street View" to open the location in Google Street View
6. Toggle "no Z-values" checkbox to exclude Z coordinate values if needed

### VBA Macro Integration

#### Installing in progeCAD

1. Open Visual Basic Editor (Alt+F11 or Tools > Macro > Visual Basic Editor)
2. Under CommonProjects, right-click on Modules and select "Import File"
3. In the file dialog, navigate to and select `proge_vba_macro/ClipboardListener.bas`

#### Running in progeCAD

1. Load macro manager (Alt+F8 or Tools > Macro > Macro)
2. In the dropdown menu, select "CommonProjects"
3. Select either:
   - `ClipboardListener.StartMonitoring` to begin monitoring the clipboard
   - `ClipboardListener.StopMonitoring` to end monitoring
4. Click "Run"

#### How It Works

When active, the macro monitors your clipboard for content matching the pattern "Position: X Y Zm" and automatically creates points in the active document.

## Technical Details

- Coordinate system conversion: Greek grid (EPSG:2100) to WGS84 (EPSG:4326)
- Regular expression pattern for coordinate extraction: `Position:[\s\r\n]*(\d+\.\d+)[\s\r\n]+(\d+\.\d+)[\s\r\n]+(\d+\.\d+)m`
- Supports 32-bit and 64-bit VBA environments