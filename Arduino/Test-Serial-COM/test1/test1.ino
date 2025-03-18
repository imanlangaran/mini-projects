void setup() {
  // Initialize serial communication at 9600 baud rate
  Serial.begin(9600);
}

int counter = 0;  // Variable to store the number we'll send

void loop() {
  // Send the current value of counter through serial
  Serial.println(counter);
  
  // Increment counter
  counter++;
  
  // Wait for 1 second (1000 milliseconds)
  delay(1000);
}