#include <MIDI.h>

MIDI_CREATE_DEFAULT_INSTANCE();

// Button pins (up to 5 buttons)
const int buttonPins[] = {2, 3, 4, 5, 6};
const int ledPins[] = {10, 11, 12, 13, A0};
const int numButtons = 5;

// Button states for each button
int buttonStates[numButtons];
int lastButtonStates[numButtons];
unsigned long lastDebounceTimes[numButtons];
const unsigned long debounceDelay = 50;

void setup() {
  // Initialize all buttons and LEDs
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
    pinMode(ledPins[i], OUTPUT);
    
    // Initialize button states
    buttonStates[i] = HIGH;
    lastButtonStates[i] = HIGH;
    lastDebounceTimes[i] = 0;
    
    // Turn off all LEDs initially
    digitalWrite(ledPins[i], LOW);
  }
  
  MIDI.begin(MIDI_CHANNEL_OMNI);
  Serial.begin(31250);
}

void loop() {
  // Check each button
  for (int i = 0; i < numButtons; i++) {
    int reading = digitalRead(buttonPins[i]);
    
    // If button state changed, reset debounce timer
    if (reading != lastButtonStates[i]) {
      lastDebounceTimes[i] = millis();
    }
    
    // If debounce time has passed, check for state change
    if ((millis() - lastDebounceTimes[i]) > debounceDelay) {
      if (reading != buttonStates[i]) {
        buttonStates[i] = reading;
        
        // Button pressed (goes LOW due to INPUT_PULLUP)
        if (buttonStates[i] == LOW) {
          digitalWrite(ledPins[i], HIGH);
          // Send MIDI Control Change with different control numbers (1-5)
          MIDI.sendControlChange(i + 1, 127, 1);
        } else {
          digitalWrite(ledPins[i], LOW);
          // Send button release
          MIDI.sendControlChange(i + 1, 0, 1);
        }
      }
    }
    
    lastButtonStates[i] = reading;
  }
}