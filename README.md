# Heart Rate Monitoring System

This project consists of an Arduino-based heart rate sensor and a Python web application for real-time ECG monitoring.

## Components

### Arduino Setup

1. Hardware Requirements:

   - Arduino board
   - AD8232 Heart Rate sensor
   - 3 electrodes (2 for measuring, 1 for reference)

2. Connections:

   - Connect the AD8232 sensor to Arduino:
     - LO+ to Arduino pin 2
     - LO- to Arduino pin 3
     - OUTPUT to Arduino analog pin A0
     - 3.3V to Arduino 3.3V
     - GND to Arduino GND

3. Electrode Placement:
   - Place the electrodes on your body:
     - Red electrode: Right arm
     - Yellow electrode: Left arm
     - Green electrode: Right leg (reference)

### Python Web Application

1. Requirements:

   - Python 3.x
   - Required packages (install using `pip install -r requirements.txt`):
     - Flask
     - pyserial
     - numpy
     - matplotlib

2. Running the Application:
   ```bash
   python ecg_monitor.py
   ```
   The web interface will be available at `http://localhost:5000`

## Usage Instructions

1. Start the Arduino:

   - Upload the `heartrate.ino` sketch to your Arduino board
   - Connect the AD8232 sensor and electrodes as described above
   - Power on the Arduino

2. Start the Python Application:

   - Open a terminal in the project directory
   - Run `python ecg_monitor.py`
   - Open a web browser and navigate to `http://localhost:5000`

3. Monitoring:
   - The web interface will show real-time ECG readings
   - Ensure the electrodes maintain good contact with your skin
   - Keep the reference electrode (green) properly placed
   - Avoid movement during measurements for best results

## Troubleshooting

1. No Signal:

   - Check all connections
   - Ensure electrodes are properly placed
   - Verify the Arduino is powered
   - Check if the correct COM port is selected in the Python application

2. Poor Signal Quality:

   - Clean the electrode contact points
   - Ensure proper skin contact
   - Minimize movement
   - Check for loose connections

3. Application Issues:
   - Verify Python dependencies are installed
   - Check if the correct COM port is being used
   - Restart both Arduino and Python application if needed

## Notes

- Keep the electrodes clean and properly placed for accurate readings
- Avoid movement during measurements
- The system is for educational purposes only and should not be used for medical diagnosis
- Always follow proper safety guidelines when working with electronic equipment
