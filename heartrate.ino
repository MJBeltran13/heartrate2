#define ECG_PIN 35   // AD8232 OUTPUT to ESP32 ADC pin
#define LO_PLUS 32   // LO+ pin (lead-off detection)
#define LO_MINUS 33  // LO- pin (lead-off detection)

// Signal processing parameters
const int SAMPLES_TO_AVERAGE = 8;     // Increased for better noise reduction
const int MIN_INTERVAL = 750;         // Minimum ms between beats (80 BPM max)
const int MAX_INTERVAL = 1200;        // Maximum ms between beats (50 BPM min)
const int CALIBRATION_PERIOD = 3000;  // Increased calibration time

// Signal amplification
const float GAIN = 20.0;  // Amplification factor for low signals

// Variables for signal processing
float threshold = 50;  // Lower initial threshold for small signals
float peakValue = 0;
float valleyValue = 4095;
const float ALPHA = 0.125;          // Moderate adaptation rate
const float THRESHOLD_RATIO = 0.6;  // Increased for better detection of small peaks
const int MIN_PEAK_HEIGHT = 20;     // Reduced for small signals
const int MIN_SIGNAL = 5;           // Minimum valid signal value

// Moving average filter
float samples[SAMPLES_TO_AVERAGE];
int sampleIndex = 0;
float filteredValue = 0;
float amplifiedValue = 0;

// DC removal
float dcLevel = 0;
const float DC_ALPHA = 0.95;  // DC removal filter coefficient

// For signal quality
int zeroCount = 0;
const int MAX_ZEROS = 10;  // Maximum consecutive zeros before considering signal lost
bool signalValid = false;

// BPM variables
int currentBPM = 0;
int averageBPM = 0;
unsigned long lastBeatTime = 0;
bool peakDetected = false;
int beatCount = 0;

// For rolling average BPM
const int MAX_BEATS = 8;  // Reduced for faster response
unsigned long beatIntervals[MAX_BEATS];
int intervalIndex = 0;
bool isCalibrated = false;
unsigned long calibrationStartTime = 0;

// Debug info
unsigned long lastDebugTime = 0;
const int DEBUG_INTERVAL = 1000;

void setup() {
  Serial.begin(115200);
  pinMode(ECG_PIN, INPUT);
  pinMode(LO_PLUS, INPUT);
  pinMode(LO_MINUS, INPUT);

  // Initialize sample buffer
  for (int i = 0; i < SAMPLES_TO_AVERAGE; i++) {
    samples[i] = 0;
  }

  // Initialize beat intervals
  for (int i = 0; i < MAX_BEATS; i++) {
    beatIntervals[i] = 0;
  }

  Serial.println("ECG Monitor Started");
  Serial.println("ecg,bpm,bpm_avg,beat_count");

  calibrationStartTime = millis();
}

void loop() {
  // Check electrode connection
  if (digitalRead(LO_PLUS) == HIGH || digitalRead(LO_MINUS) == HIGH) {
    Serial.println("Leads off!");
    delay(10);
    return;
  }

  // Read ECG value
  float rawValue = analogRead(ECG_PIN);

  // Check for valid signal
  if (rawValue < MIN_SIGNAL) {
    zeroCount++;
    if (zeroCount > MAX_ZEROS) {
      signalValid = false;
      Serial.print("0,0,0,0\n");
      delay(2);
      return;
    }
  } else {
    zeroCount = 0;
    signalValid = true;
  }

  // DC removal (high-pass filter)
  dcLevel = (DC_ALPHA * dcLevel) + ((1 - DC_ALPHA) * rawValue);
  float dcRemoved = rawValue - dcLevel;

  // Amplify the signal
  amplifiedValue = dcRemoved * GAIN;

  // Moving average filter
  samples[sampleIndex] = amplifiedValue;
  sampleIndex = (sampleIndex + 1) % SAMPLES_TO_AVERAGE;

  float sum = 0;
  for (int i = 0; i < SAMPLES_TO_AVERAGE; i++) {
    sum += samples[i];
  }
  filteredValue = sum / SAMPLES_TO_AVERAGE;

  // Update peak and valley with baseline consideration
  if (filteredValue > peakValue) {
    peakValue = filteredValue;
  } else {
    peakValue = peakValue - (peakValue - filteredValue) * ALPHA;
  }

  if (filteredValue < valleyValue) {
    valleyValue = filteredValue;
  } else {
    valleyValue = valleyValue + (filteredValue - valleyValue) * ALPHA;
  }

  // Dynamic threshold calculation
  float signalRange = peakValue - valleyValue;
  if (signalRange > MIN_PEAK_HEIGHT) {
    threshold = valleyValue + (signalRange * THRESHOLD_RATIO);
  }

  // Beat detection
  unsigned long currentTime = millis();

  if (!peakDetected && filteredValue > threshold && (currentTime - lastBeatTime) > MIN_INTERVAL) {
    unsigned long beatInterval = currentTime - lastBeatTime;

    if (beatInterval >= MIN_INTERVAL && beatInterval <= MAX_INTERVAL) {
      int instantBPM = 60000 / beatInterval;

      if (instantBPM >= 45 && instantBPM <= 120) {
        currentBPM = instantBPM;
        averageBPM = (averageBPM == 0) ? instantBPM : (averageBPM + instantBPM) / 2;
        beatCount++;
        lastBeatTime = currentTime;
      }
    }
    peakDetected = true;
  }

  // Reset peak detection
  if (filteredValue < threshold) {
    peakDetected = false;
  }

  // Output data
  if (signalValid) {
    Serial.print(int(filteredValue));
    Serial.print(",");
    Serial.print(currentBPM);
    Serial.print(",");
    Serial.print(averageBPM);
    Serial.print(",");
    Serial.println(beatCount);
  }

  // Debug info every second
  if (currentTime - lastDebugTime > 1000) {
    lastDebugTime = currentTime;
    Serial.print("Debug: Raw=");
    Serial.print(rawValue);
    Serial.print(" Filtered=");
    Serial.print(filteredValue);
    Serial.print(" Threshold=");
    Serial.print(threshold);
    Serial.print(" DC=");
    Serial.println(dcLevel);
  }

  delayMicroseconds(2500);  // 400Hz sampling rate
}
