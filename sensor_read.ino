#define ANALOG_PIN 15  // Using GPIO 15 for analog input

void setup() {
    Serial.begin(115200);  // Start serial communication
}

void loop() {
    int analogValue = analogRead(ANALOG_PIN);  // Read analog input
      // Convert ADC value to voltage

    Serial.println("Analog Value: ");
    Serial.println(analogValue);
//    Serial.print(" | Voltage: ");
//    Serial.println(voltage, 3);  // Print voltage with 3 decimal places

    delay(500);  // Delay for readability
}
