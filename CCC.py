import re
import os
import sys
import time

from pyproj import Transformer
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QLabel

import keyboard
import pywinctl
import pyperclip
import pyautogui
import pygetwindow

# OCR Functions from ocr_test.py
def copy_coords_from_window(window_name):
    win = pywinctl.getWindowsWithTitle(window_name)
    if not win:
        return None
    
    win = win[0]
    win.activate()
    #time.sleep(0.3)  # Allow time for the window to activate
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.hotkey('ctrl', 'c')
    #time.sleep(0.3)  # Allow time for clipboard to update
    test = pyperclip.paste()
    coords = extract_coordinates(test)
    return coords

# Coordinate extraction from clipboard text (from CCC.py)
def extract_coordinates(text):
    """
    Extracts coordinates from clipboard text in the format "Position: X Y Zm".
    """
    pattern = r"Position:\s*(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)m"
    match = re.search(pattern, text)
    if match:
        x, y, z = match.groups()
        
        # Validate that X has 6 integer digits and Y has 7 integer digits
        x_int_digits = len(str(int(float(x))))
        y_int_digits = len(str(int(float(y))))
        
        if x_int_digits == 6 and y_int_digits == 7:
            return x, y, z            
    return None


# Keyboard Hotkey Monitor Thread (new for F1 functionality)
class KeyboardMonitorThread(QThread):
    status_update = pyqtSignal(str)
    coordinates_captured = pyqtSignal(tuple)
    
    def __init__(self, window_name="Measurements"):
        super().__init__()
        self.running = False
        self.window_name = window_name
        
    def run(self):
        self.running = True
        self.status_update.emit("F1 hotkey activated - Press F1 to capture coordinates from screen")
        
        # Register hotkey
        keyboard.add_hotkey('f1', self.capture_and_process)
        
        # Keep thread alive
        while self.running:
            time.sleep(0.1)
            
    def capture_and_process(self):
        """Extract coordinates when F1 is pressed"""
        self.status_update.emit("Capturing screenshot...")
        
        try:
            coords = copy_coords_from_window(self.window_name)
            if coords:
                x, y, z = coords
                self.status_update.emit(f"Extracted coordinates: ({x}, {y}, {z})")
                self.coordinates_captured.emit((str(x), str(y), str(z)))
            else:
                self.status_update.emit("Failed to extract coordinates from screenshot")
        except Exception as e:
            self.status_update.emit(f"Error: {e} at line {sys.exc_info()[-1].tb_lineno}")
    
    def stop(self):
        self.running = False
        keyboard.unhook_all()  # Remove all hotkey bindings

# Main GUI Class
class SimpleGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.coordinates = None
        self.monitoring = False
        self.last_clipboard = ""
        self.initUI()
        
        # Initialize keyboard monitor thread for F1 hotkey
        self.keyboard_thread = KeyboardMonitorThread()
        self.keyboard_thread.status_update.connect(self.update_status)
        self.keyboard_thread.coordinates_captured.connect(self.process_captured_coordinates)
        
    def get_resource_path(self, relative_path):
        """ Get the absolute path to the resource, accounting for PyInstaller's handling. """
        if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
            base_path = sys._MEIPASS  # The path to the temporary folder where files are unpacked
        else:
            base_path = os.path.dirname(__file__)  # Regular script location
        return os.path.join(base_path, relative_path)

    def initUI(self):
        layout = QVBoxLayout()
        # rename the window to 'Simple PyQt5 GUI'
        self.setWindowTitle('Context Capture Click - CCC with OCR')
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)


        self.setStyleSheet("background-color: #aaacad;")
        # SET width to 400
        self.setFixedWidth(400)

        # Determine the path to the image file
        if hasattr(sys, '_MEIPASS'):
            logo_path = os.path.join(sys._MEIPASS, 'Map-Greece-Logo_white.png')
        else:
            logo_path = self.get_resource_path('Map-Greece-Logo_white.png')
            
        logo_label = QLabel(self)
        pixmap = QPixmap(logo_path)
        pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Resize the image
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        self.no_z_Values = QCheckBox('no Z-values', self)
        self.no_z_Values.setChecked(False)
        
        # New button for F1 OCR capture functionality
        self.ocrCaptureButton = QPushButton('Enable F1 OCR Capture', self)
        self.ocrCaptureButton.setStyleSheet("background-color: green")
        self.ocrCaptureButton.setCheckable(True)
        self.ocrCaptureButton.clicked.connect(self.toggleOcrCapture)

        self.convertAutoCADbutton = QPushButton('Convert CAD', self)
        self.convertAutoCADbutton.clicked.connect(self.convertAutoCAD)

        self.convertXYZbutton = QPushButton('Convert XYZ', self)
        self.convertXYZbutton.clicked.connect(self.convertXYZ)

        self.streetViewbutton = QPushButton('Street View', self)
        self.streetViewbutton.clicked.connect(self.streetView)

        # Status label
        self.status_label = QLabel("Idle - Click 'Start Monitoring' to begin")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        
        layout.addWidget(self.ocrCaptureButton)  # Add the new OCR button
        layout.addWidget(self.status_label)

        layout.addWidget(self.convertAutoCADbutton)
        layout.addWidget(self.convertXYZbutton)
        layout.addWidget(self.streetViewbutton)

        # Create a horizontal layout for the checkbox and logo
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.no_z_Values)
        h_layout.addWidget(logo_label, alignment=Qt.AlignRight | Qt.AlignBottom)
        
        # Add the horizontal layout to the main vertical layout
        layout.addLayout(h_layout)

        self.setLayout(layout)
        self.updateStreetViewButtonState() 
        self.show()

    def updateStreetViewButtonState(self):
        # Gray out the Street View button if self.coordinates is None
        self.streetViewbutton.setEnabled(self.coordinates is not None)

    def toggleOcrCapture(self):
        """Toggle OCR capture using F1 key"""
        if self.ocrCaptureButton.isChecked():
            self.ocrCaptureButton.setText("Disable F1 OCR Capture")
            self.ocrCaptureButton.setStyleSheet("background-color: red")
            self.keyboard_thread.start()
        else:
            self.ocrCaptureButton.setText("Enable F1 OCR Capture")
            self.ocrCaptureButton.setStyleSheet("background-color: green")
            self.keyboard_thread.stop()
            self.keyboard_thread.wait()
            
            # Create a new thread for next time
            self.keyboard_thread = KeyboardMonitorThread()
            self.keyboard_thread.status_update.connect(self.update_status)
            self.keyboard_thread.coordinates_captured.connect(self.process_captured_coordinates)

    def process_captured_coordinates(self, coords):
        """Process coordinates captured via OCR"""
        if coords:
            x, y, z = coords
            
            # Additional validation to ensure X has 6 integer digits and Y has 7 integer digits
            x_int_digits = len(str(int(float(x))))
            y_int_digits = len(str(int(float(y))))
            
            if x_int_digits != 6 or y_int_digits != 7:
                self.update_status(f"Invalid coordinates format: X should have 6 digits, Y should have 7 digits. Got X: {x_int_digits}, Y: {y_int_digits}")
                return
                
            self.coordinates = [x, y, z]
            self.updateStreetViewButtonState()
            
            # Send coordinates to progeCAD
            try:
                # Locate and activate the progeCAD window
                progecad_windows = pygetwindow.getWindowsWithTitle("progeCAD")
                if not progecad_windows:
                    self.update_status("progeCAD window not found.")
                    return
                    
                progecad_window = progecad_windows[0]
                if progecad_window.isMinimized:
                    progecad_window.restore()
                progecad_window.activate()
                #time.sleep(0.3)
                
                # Check if no_z_Values is checked and adjust command accordingly
                if self.no_z_Values.isChecked():
                    # Only send X and Y coordinates
                    pyautogui.typewrite(f"_POINT {x},{y}")
                    self.update_status(f"Point created at ({x}, {y}) - Z omitted")
                else:
                    # Send all three coordinates
                    pyautogui.typewrite(f"_POINT {x},{y},{z}")
                    self.update_status(f"Point created at ({x}, {y}, {z})")
                    
                pyautogui.press("enter")
            except Exception as e:
                self.update_status(f"Error: {e}")

    def convertXYZ(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        lines = text.split('\n')
        print(lines)
        coordinates = []
        for line in lines:
            if line.strip() and line.strip() != 'Position:':
                parts = line.strip().replace('m', '').split()
                coordinates.append(' '.join(parts))

        if self.no_z_Values.isChecked():
            clipboard_values =  coordinates[:2]
        else:
            clipboard_values = coordinates

        self.coordinates = clipboard_values
        self.updateStreetViewButtonState()
        print(clipboard_values)
        #if self.no_z_Values.isChecked():            
        result = ' '.join(clipboard_values)
        clipboard.setText(result)

    def convertAutoCAD(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        lines = text.split('\n')
        print(lines)
        coordinates = []
        for line in lines:
            if line.strip() and line.strip() != 'Position:':
                parts = line.strip().replace('m', '').split()
                coordinates.append(' '.join(parts))

        if self.no_z_Values.isChecked():
            clipboard_values =  coordinates[:2]
        else:
            clipboard_values = coordinates

        self.coordinates = clipboard_values
        self.updateStreetViewButtonState()
        result = 'PO ' + ','.join(clipboard_values) + '\n'
        clipboard.setText(result)

                
    def update_status(self, status):
        self.status_label.setText(status)
        
    def streetView(self):
        """
        Reads the XYZ Values from the clipboard (Greek grid) and turns them into WGS84 coordinates and then opens the street view
        """
        try:
            if self.coordinates:
                coordinates = self.coordinates
                print('sadasd:', float(coordinates[0]), float(coordinates[1]))
                # Convert from Greek grid (EPSG:2100) to WGS84 (EPSG:4326)
                transformer = Transformer.from_crs("EPSG:2100", "EPSG:4326")
                wgs84_coordinates = []
                #x, y, z = map(float, coordinates)
                print(f"Coordinates: {coordinates}")  # Debugging statement
                print(f"Coordinates[0]: {coordinates[0]}")  # Debugging statement
                lat, lon = transformer.transform(float(coordinates[0]), float(coordinates[1]))
                wgs84_coordinates.append((lat, lon,))
                print(f"WGS84 Coordinates: {wgs84_coordinates}")  # Debugging statement

                # Open street view using the first coordinate
                if wgs84_coordinates:
                    lat, lon = wgs84_coordinates[0][:2]
                    url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lon}"
                    print(f"Opening URL: {url}")  # Debugging statement
                    import webbrowser
                    webbrowser.open(url)
        except Exception as e:
            print(f"An error occurred: {e}, at line {sys.exc_info()[-1].tb_lineno}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = SimpleGUI()
    sys.exit(app.exec_())