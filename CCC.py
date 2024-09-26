import sys

import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QCheckBox
from pyproj import Transformer

class SimpleGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        # SET width to 400
        self.setFixedWidth(400)
        #         # check box for z-values
        self.no_z_Values = QCheckBox('no Z-values', self)
        self.no_z_Values.setChecked(False)

        self.convertXYZbutton = QPushButton('Convert XYZ', self)
        self.convertXYZbutton.clicked.connect(self.convertXYZ)

        self.convertAutoCADbutton = QPushButton('Convert AutoCAD', self)
        self.convertAutoCADbutton.clicked.connect(self.convertAutoCAD)

        self.streetViewbutton = QPushButton('Street View', self)
        self.streetViewbutton.clicked.connect(self.streetView)

        layout.addWidget(self.convertXYZbutton)
        layout.addWidget(self.convertAutoCADbutton)
        layout.addWidget(self.streetViewbutton)

        layout.addWidget(self.no_z_Values)

        self.setLayout(layout)
        self.setWindowTitle('Simple PyQt5 GUI')
        self.show()

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

        result = 'PO ' + ','.join(clipboard_values)
        clipboard.setText(result)
    
    def streetView(self):
        """
        Reads the XYZ Values from the clipboard (Greek grid) and turns them into WGS84 coordinates and then opens the street view
        """
        try:
            clipboard = QApplication.clipboard()
            text = clipboard.text()
            print(f"Clipboard text: {text}")  # Debugging statement
            lines = text.split('\n')
            print(f"Lines: {lines}")  # Debugging statement
            coordinates = []
            for line in lines:
                if line.strip() and line.strip() != 'Position:':
                    parts = line.strip().replace('m', '').split()
                    coordinates.append(parts)
            print(f"Coordinates before Z-check: {coordinates}")  # Debugging statement

            if self.no_z_Values.isChecked():
                coordinates = [coordinates[0][:2], coordinates[1][:2]]
                print(f"Coordinates after Z-check: {coordinates}")  # Debugging statement

            # Convert from Greek grid (EPSG:2100) to WGS84 (EPSG:4326)
            transformer = Transformer.from_crs("EPSG:2100", "EPSG:4326")
            wgs84_coordinates = []
            #x, y, z = map(float, coordinates)
            print(f"Coordinates: {coordinates}")  # Debugging statement
            print(f"Coordinates[0]: {coordinates[0]}")  # Debugging statement
            lat, lon = transformer.transform(float(coordinates[0][0]), float(coordinates[1][0]))
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