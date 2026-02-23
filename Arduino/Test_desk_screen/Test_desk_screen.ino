#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128 // OLED display width, in pixels
#define SCREEN_HEIGHT 64 // OLED display height, in pixels

#define OLED_RESET     -1 // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

#define pressed_state LOW
#define BUTTON_PIN 2

#define DEBOUNCE_TIME     30
#define LONG_PRESS_TIME   800
#define DOUBLE_PRESS_TIME 400

enum BUTTON_STATUS {
  noPress,
  press,
  doublePress,
  longPress
};

BUTTON_STATUS key = noPress;

void setup() {
  Serial.begin(9600);

  pinMode(13, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);



  // if(key == noPress)
    digitalWrite(13, LOW);
  // else 
  //   digitalWrite(13, HIGH);

  delay(500);

  // SSD1306_SWITCHCAPVCC = generate display voltage from 3.3V internally
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  // Clear the buffer
  display.clearDisplay();

  // Draw a single pixel in white
  // display.drawPixel(10, 10, SSD1306_WHITE);

  // display.display();
  // delay(2000);

  // testdrawchar();      // Draw characters of the default font

  // testdrawstyles();    // Draw 'stylized' characters

  // testscrolltext();    // Draw scrolling text

}


void loop() {
  // digitalWrite(13, digitalRead(BUTTON_PIN));
  readKey();
  updateDisplay();
  delay(50);
}



void readKey() {

  static bool lastPhysicalState = HIGH;
  static bool stableState = HIGH;
  static unsigned long lastDebounceTime = 0;

  static unsigned long pressStartTime = 0;
  static unsigned long lastReleaseTime = 0;
  static bool waitingForDouble = false;

  bool reading = digitalRead(BUTTON_PIN);
  unsigned long now = millis();

  // -------- Debounce --------
  if (reading != lastPhysicalState) {
    lastDebounceTime = now;
  }

  if ((now - lastDebounceTime) > DEBOUNCE_TIME) {
    stableState = reading;
  }

  lastPhysicalState = reading;

  key = noPress;

  // -------- Pressed --------
  if (stableState == LOW) {
    if (pressStartTime == 0) {
      pressStartTime = now;
    }

    if ((now - pressStartTime) > LONG_PRESS_TIME) {
      key = longPress;
      waitingForDouble = false;
    }
  }

  // -------- Released --------
  if (stableState == HIGH && pressStartTime != 0) {

    unsigned long pressDuration = now - pressStartTime;
    pressStartTime = 0;

    if (pressDuration < LONG_PRESS_TIME) {

      if (waitingForDouble && (now - lastReleaseTime) < DOUBLE_PRESS_TIME) {
        key = doublePress;
        waitingForDouble = false;
      } else {
        waitingForDouble = true;
        lastReleaseTime = now;
      }
    }
  }

  // -------- Single press timeout --------
  if (waitingForDouble && (now - lastReleaseTime) > DOUBLE_PRESS_TIME) {
    key = press;
    waitingForDouble = false;
  }
}

void updateDisplay(){

  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);

  char text[]="placeholderfor";
  switch(key){
    case noPress:
      strcpy(text,"noPress");
      break;
    case press:
      strcpy(text,"press");
      break;
    case longPress:
      strcpy(text,"longPress");
      break;
    case doublePress:
      strcpy(text,"doublePress");
      break;
    default:
      break;
  }

  display.println(text);
  display.display();

  delay(50);
}


void testdrawchar(void) {
  display.clearDisplay();

  display.setTextSize(1);      // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE); // Draw white text
  display.setCursor(0, 0);     // Start at top-left corner
  display.cp437(true);         // Use full 256 char 'Code Page 437' font

  // Not all the characters will fit on the display. This is normal.
  // Library will draw what it can and the rest will be clipped.
  for(int16_t i=0; i<256; i++) {
    if(i == '\n') display.write(' ');
    else          display.write(i);
  }

  display.display();
  delay(2000);
}

void testdrawstyles(void) {
  display.clearDisplay();

  display.setTextSize(1);             // Normal 1:1 pixel scale
  display.setTextColor(SSD1306_WHITE);        // Draw white text
  display.setCursor(0,0);             // Start at top-left corner
  display.println(F("Hello, world!"));

  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE); // Draw 'inverse' text
  display.println(3.141592);

  display.setTextSize(2);             // Draw 2X-scale text
  display.setTextColor(SSD1306_WHITE);
  display.print(F("0x")); display.println(0xDEADBEEF, HEX);

  display.display();
  delay(2000);
}

void testscrolltext(void) {
  display.clearDisplay();

  display.setTextSize(2); // Draw 2X-scale text
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(10, 0);
  display.println(F("scroll"));
  display.display();      // Show initial text
  delay(100);

  // Scroll in various directions, pausing in-between:
  display.startscrollright(0x00, 0x0F);
  delay(2000);
  display.stopscroll();
  delay(1000);
  display.startscrollleft(0x00, 0x0F);
  delay(2000);
  display.stopscroll();
  delay(1000);
  display.startscrolldiagright(0x00, 0x07);
  delay(2000);
  display.startscrolldiagleft(0x00, 0x07);
  delay(2000);
  display.stopscroll();
  delay(1000);
}
