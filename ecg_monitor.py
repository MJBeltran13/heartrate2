import serial
import time
from flask import Flask, render_template, jsonify
from threading import Thread, Lock
import json
import winsound  # For beep sound on Windows

# Global variables for data storage
ecg_data = []
bpm_data = []
avg_bpm_data = []
beat_count = 0
last_beat_count = 0  # To track when a new beat occurs
data_lock = Lock()
serial_port = None  # Global serial port object

# Initialize Flask app
app = Flask(__name__)

# Serial port configuration
SERIAL_PORT = 'COM11'
BAUD_RATE = 115200

# Maximum number of data points to store
MAX_DATA_POINTS = 200

# Signal quality parameters
MIN_VALID_ECG = 100    # Minimum valid ECG value
MAX_VALID_ECG = 4000   # Maximum valid ECG value
SIGNAL_VALID_THRESHOLD = 0.8  # 80% of samples must be valid

# Sound configuration
BEEP_FREQ = 1000      # Frequency in Hz for heartbeat
BEEP_DUR = 50        # Duration in milliseconds for heartbeat
FLATLINE_FREQ = 2000  # Frequency in Hz for flatline alarm
FLATLINE_DUR = 5000   # Duration in milliseconds for flatline alarm
NO_BEAT_TIMEOUT = 3.0  # Seconds before considering flatline
last_beat_time = time.time()  # Track time of last beat
flatline_alarm_active = False  # Track if alarm is currently sounding

def play_flatline_alarm():
    """Play flatline alarm sound in a loop until beat detected"""
    global flatline_alarm_active
    while flatline_alarm_active:
        try:
            winsound.Beep(FLATLINE_FREQ, FLATLINE_DUR)
       
        except:
            pass

def cleanup_serial():
    global serial_port
    if serial_port is not None:
        try:
            serial_port.close()
        except:
            pass
        serial_port = None

def is_valid_data(ecg_value, bpm_value, avg_bpm_value):
    # Check ECG value range
    if not (MIN_VALID_ECG <= ecg_value <= MAX_VALID_ECG):
        return False
        
    # Check BPM values if present
    if bpm_value != 0:  # 0 is used when no beat is detected
        if not (40 <= bpm_value <= 150):
            return False
    
    if avg_bpm_value != 0:
        if not (40 <= avg_bpm_value <= 150):
            return False
            
    return True

def read_serial():
    global ecg_data, bpm_data, avg_bpm_data, beat_count, last_beat_count, serial_port, last_beat_time, flatline_alarm_active
    flatline_alarm_thread = None
    
    while True:
        try:
            if serial_port is None:
                cleanup_serial()  # Make sure old connections are closed
                time.sleep(1)  # Wait before attempting to reconnect
                serial_port = serial.Serial(SERIAL_PORT, BAUD_RATE)
                print(f"Connected to {SERIAL_PORT}")
                
                # Skip header line
                serial_port.readline()
            
            # Variables for signal quality assessment
            valid_samples = 0
            total_samples = 0
            
            while True:
                try:
                    if serial_port is None:
                        break
                        
                    line = serial_port.readline().decode('utf-8').strip()
                    current_time = time.time()
                    
                    # Check for flatline condition
                    if current_time - last_beat_time > NO_BEAT_TIMEOUT:
                        if not flatline_alarm_active:
                            print("WARNING: No heartbeat detected!")
                            flatline_alarm_active = True
                            flatline_alarm_thread = Thread(target=play_flatline_alarm, daemon=True)
                            flatline_alarm_thread.start()
                    
                    if line and not line.startswith("Leads off"):
                        try:
                            # Parse CSV format: ecg,bpm,bpm_avg,beat_count
                            values = [v.strip() for v in line.split(',')]
                            if len(values) == 4:
                                ecg_value = int(values[0])
                                current_bpm = int(values[1])
                                avg_bpm = int(values[2])
                                new_beat_count = int(values[3])
                                
                                # Validate data
                                if is_valid_data(ecg_value, current_bpm, avg_bpm):
                                    valid_samples += 1
                                total_samples += 1
                                
                                # Update signal quality status every 100 samples
                                if total_samples >= 100:
                                    signal_quality = valid_samples / total_samples
                                    print(f"Signal Quality: {signal_quality:.2%}")
                                    valid_samples = 0
                                    total_samples = 0
                                
                                with data_lock:
                                    # Store ECG data
                                    ecg_data.append(ecg_value)
                                    if len(ecg_data) > MAX_DATA_POINTS:
                                        ecg_data.pop(0)
                                    
                                    # Store BPM data
                                    bpm_data.append(current_bpm if current_bpm > 0 else None)
                                    if len(bpm_data) > MAX_DATA_POINTS:
                                        bpm_data.pop(0)
                                    
                                    # Store average BPM data
                                    avg_bpm_data.append(avg_bpm if avg_bpm > 0 else None)
                                    if len(avg_bpm_data) > MAX_DATA_POINTS:
                                        avg_bpm_data.pop(0)
                                    
                                    # Update beat count and handle sounds
                                    if new_beat_count > beat_count:
                                        beat_count = new_beat_count
                                        last_beat_time = current_time
                                        # Stop flatline alarm if active
                                        flatline_alarm_active = False
                                        # Play heartbeat sound
                                        Thread(target=lambda: winsound.Beep(BEEP_FREQ, BEEP_DUR), daemon=True).start()
                                    
                                    print(f"ECG: {ecg_value}, BPM: {current_bpm}, AVG BPM: {avg_bpm}, Beats: {beat_count}")
                                    
                        except ValueError as ve:
                            print(f"Invalid data format: {line}")
                        except Exception as e:
                            print(f"Error processing data: {e}")
                            
                except Exception as e:
                    print(f"Error reading line: {e}")
                    cleanup_serial()
                    break
                    
        except Exception as e:
            print(f"Serial connection error: {e}")
            cleanup_serial()
            time.sleep(2)  # Wait longer before retrying
            continue

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    with data_lock:
        # Get the most recent valid BPM values
        current_bpm = next((x for x in reversed(bpm_data) if x is not None), 0)
        avg_bpm = next((x for x in reversed(avg_bpm_data) if x is not None), 0)
        
        return jsonify({
            'ecg': ecg_data,
            'bpm': bpm_data,
            'avg_bpm': avg_bpm_data,
            'current_bpm': current_bpm,
            'average_bpm': avg_bpm,
            'beat_count': beat_count
        })

def cleanup():
    global flatline_alarm_active
    flatline_alarm_active = False
    cleanup_serial()

if __name__ == '__main__':
    # Register cleanup handler
    import atexit
    atexit.register(cleanup)
    
    # Start serial reading in a separate thread
    serial_thread = Thread(target=read_serial, daemon=True)
    serial_thread.start()
    
    try:
        # Run Flask app
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        flatline_alarm_active = False
        cleanup_serial()  # Ensure serial port is closed when app exits 