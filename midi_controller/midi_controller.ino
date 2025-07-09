#include <MIDI.h>

MIDI_CREATE_DEFAULT_INSTANCE();

const int buttonPin = 2;
const int ledPin = 10;

int buttonState = 0;
int lastButtonState = 0;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);
  
  MIDI.begin(MIDI_CHANNEL_OMNI);
  Serial.begin(31250);
}

void loop() {
  int reading = digitalRead(buttonPin);
  
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }
  
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;
      
      if (buttonState == LOW) {
        digitalWrite(ledPin, HIGH);
        MIDI.sendControlChange(1, 127, 1);
      } else {
        digitalWrite(ledPin, LOW);
        MIDI.sendControlChange(1, 0, 1);
      }
    }
  }
  
  lastButtonState = reading;
}