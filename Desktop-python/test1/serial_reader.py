import sys
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import QTimer

class SerialReaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initSerial()

    def initUI(self):
        # Set up the window
        self.setWindowTitle("Serial Port Reader")
        self.setGeometry(100, 100, 400, 300)

        # Create a layout
        layout = QVBoxLayout()

        # Label for status
        self.status_label = QLabel("Status: Not Connected", self)
        layout.addWidget(self.status_label)

        # Text area to display received messages
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        # Button to connect/disconnect
        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.toggle_connection)
        layout.addWidget(self.connect_button)

        # Set the layout
        self.setLayout(layout)

    def initSerial(self):
        # Initialize serial port
        self.serial_port = serial.Serial()
        self.serial_port.timeout = 0.1  # Non-blocking read
        self.connected = False

        # Timer to read from the serial port
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial)

    def toggle_connection(self):
        if not self.connected:
            # Try to connect to the serial port
            port = "COM3"  # Change this to your serial port
            baudrate = 9600  # Change this to match your device's baud rate
            try:
                self.serial_port.port = port
                self.serial_port.baudrate = baudrate
                self.serial_port.open()
                self.connected = True
                self.status_label.setText(f"Status: Connected to {port}")
                self.connect_button.setText("Disconnect")
                self.timer.start(100)  # Check for data every 100ms
            except Exception as e:
                self.status_label.setText(f"Error: {str(e)}")
        else:
            # Disconnect
            self.serial_port.close()
            self.connected = False
            self.status_label.setText("Status: Not Connected")
            self.connect_button.setText("Connect")
            self.timer.stop()

    def read_serial(self):
        if self.serial_port.is_open:
            try:
                # Read data from the serial port
                data = self.serial_port.readline().decode('utf-8').strip()
                if data:
                    self.text_area.append(f"Received: {data}")
            except Exception as e:
                self.text_area.append(f"Error reading serial data: {str(e)}")

    def closeEvent(self, event):
        # Close the serial port when the application is closed
        if self.serial_port.is_open:
            self.serial_port.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialReaderApp()
    window.show()
    sys.exit(app.exec_())