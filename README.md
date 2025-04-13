# Heart Rate Monitoring System

This project consists of an ESP32-based heart rate sensor and a Python web application for real-time ECG monitoring.

## Components

### ESP32 Setup

1. Hardware Requirements:

   - ESP32 board
   - AD8232 Heart Rate sensor
   - 3 electrodes (2 for measuring, 1 for reference)

2. Connections:

   - Connect the AD8232 sensor to ESP32:
     - LO+ to ESP32 pin 32
     - LO- to ESP32 pin 33
     - OUTPUT to ESP32 ADC pin 35
     - 3.3V to ESP32 3.3V
     - GND to ESP32 GND

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

1. Start the ESP32:

   - Upload the `heartrate.ino` sketch to your ESP32 board
   - Connect the AD8232 sensor and electrodes as described above
   - Power on the ESP32

2. Start the Python Application:

   - Open a terminal in the project directory
   - Run `python ecg_monitor.py`
   - Open a web browser and navigate to `http://localhost:5000`

3. Monitoring:
   - The web interface will show real-time ECG readings
   - The system provides:
     - Raw ECG signal
     - Current BPM
     - Average BPM
     - Beat count
   - Ensure the electrodes maintain good contact with your skin
   - Keep the reference electrode (green) properly placed
   - Avoid movement during measurements for best results

## Signal Processing Features

The system includes several signal processing features:
- DC removal filter for baseline correction
- Moving average filter for noise reduction
- Dynamic threshold adjustment
- Signal amplification for weak readings
- Beat detection with validation
- BPM calculation with range checking (45-120 BPM)

## Troubleshooting

1. No Signal:

   - Check all connections
   - Ensure electrodes are properly placed
   - Verify the ESP32 is powered
   - Check if the correct COM port is selected in the Python application
   - Look for "Leads off!" message in serial monitor

2. Poor Signal Quality:

   - Clean the electrode contact points
   - Ensure proper skin contact
   - Minimize movement
   - Check for loose connections
   - Monitor debug output for signal levels

3. Application Issues:
   - Verify Python dependencies are installed
   - Check if the correct COM port is being used
   - Restart both ESP32 and Python application if needed
   - Check serial monitor for debug information

## Notes

- Keep the electrodes clean and properly placed for accurate readings
- Avoid movement during measurements
- The system is for educational purposes only and should not be used for medical diagnosis
- Always follow proper safety guidelines when working with electronic equipment
- The system samples at 400Hz and includes various filters for signal quality
