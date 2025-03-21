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
import pyautogui

def copy_coords_from_window(window_name):
    try:
        win = pywinctl.getWindowsWithTitle(window_name)
        if not win:
            return None
        
        win = win[0]  # First matching window
        win.activate()
        time.sleep(0.1)  # Allow time for the window to activate
        print("Window activated")
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(0.1)  # Allow time for clipboard to update
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return None

# Keyboard Hotkey Monitor Thread (new for F1 functionality)
class KeyboardMonitorThread(QThread):
    coordinates_captured = pyqtSignal(tuple)
    
    def __init__(self, window_name="Measurements"):
        super().__init__()
        self.running = False
        self.window_name = window_name
        
    def run(self):
        self.running = True
        
        # Register hotkey
        keyboard.add_hotkey('f1', self.capture_and_process)
        
        # Keep thread alive
        while self.running:
            time.sleep(0.1)
            
    def capture_and_process(self):
        try:
            # Capture screenshot of the window
            copy_coords_from_window(self.window_name)
        except Exception as e:
            print(f"Error capturing coordinates: {e}")

    
    def stop(self):
        self.running = False
        keyboard.unhook_all()  # Remove all hotkey bindings   


# Main GUI Class
class SimpleGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.coordinates = None
        self.initUI()
        
        
        # Initialize keyboard monitor thread for F1 hotkey
        self.keyboard_thread = KeyboardMonitorThread()
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
        self.setWindowTitle('Context Capture Click')
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
        
        layout.addWidget(self.ocrCaptureButton)  # Add the new OCR button

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
            self.keyboard_thread.coordinates_captured.connect(self.process_captured_coordinates)

    def process_captured_coordinates(self, coords):
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
                lat, lon = transformer.transform(float(coordinates[0]), float(coordinates[1]))
                wgs84_coordinates.append((lat, lon,))
                print(f"WGS84 Coordinates: {wgs84_coordinates}")  # Debugging statement

                # Open street view using the first coordinate
                if wgs84_coordinates:
                    lat, lon = wgs84_coordinates[0][:2]
                    url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lon}"
                    import webbrowser
                    webbrowser.open(url)
        except Exception as e:
            print(f"An error occurred: {e}, at line {sys.exc_info()[-1].tb_lineno}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = SimpleGUI()
    sys.exit(app.exec_())