# Arduino Nano MIDI Controller Setup

## Benötigte Software

### Arduino IDE
```bash
# Mac - Arduino IDE ist nicht mehr über Homebrew verfügbar
# Download direkt von: https://www.arduino.cc/en/software
# Oder Arduino IDE 2.0 über Homebrew:
brew install --cask arduino-ide

# Alternative: Arduino CLI
brew install arduino-cli
```

### Python Dependencies
```bash
# Für Serial-Verbindung (empfohlen)
pip install pyserial

# Für MIDI-Verbindung (optional)
pip install mido python-rtmidi
```

### MIDI Library für Arduino
1. Arduino IDE öffnen
2. Tools → Manage Libraries
3. Nach "MIDI Library" suchen (von FortySevenEffects)
4. Installieren

## Hardware Setup

1. Verkabelung nach `wiring_diagram.txt`
2. Arduino Nano per USB mit PC verbinden
3. Button und LED auf Steckboard aufbauen

## Arduino Code flashen

1. `midi_controller.ino` in Arduino IDE öffnen
2. Board: Tools → Board → Arduino Nano
3. Processor: Tools → Processor → ATmega328P (Old Bootloader)
4. Port: Entsprechenden USB-Port auswählen
5. Upload-Button drücken

## PC-Software starten

### Option 1: Serial-Verbindung (empfohlen)
1. Python Dependencies installieren:
```bash
pip install pyserial
```

2. Verfügbare Ports anzeigen:
```bash
python3 serial_macro_bridge.py
```

3. Mit Arduino verbinden:
```bash
python3 serial_macro_bridge.py "/dev/cu.usbserial-10"
# oder den Port, der in der Liste angezeigt wird
```

### Option 2: MIDI-Verbindung
1. MIDI-Ports anzeigen:
```bash
python3 midi_macro_bridge.py
```

2. Mit Arduino verbinden (falls als MIDI-Gerät erkannt):
```bash
python3 midi_macro_bridge.py "Arduino Nano"
```

## Macros anpassen

In `serial_macro_bridge.py` (oder `midi_macro_bridge.py`) die `macro_1` Funktion bearbeiten:

```python
def macro_1(self):
    # Aktuelles Beispiel: Terminal öffnen und "hello world" ausgeben
    subprocess.run(["osascript", "-e", 'tell application "Terminal" to do script "echo hello world"'])
    
    # Weitere Beispiele:
    # Screenshot auf Mac
    # subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke "4" using {command down, shift down}'])
    
    # App öffnen
    # subprocess.run(["open", "-a", "Calculator"])
```

## Troubleshooting

- **Arduino nicht erkannt**: Treiber installieren oder anderen USB-Port probieren
- **MIDI funktioniert nicht**: Baud Rate auf 31250 prüfen
- **Button reagiert nicht**: Pull-up Widerstand prüfen oder internen Pull-up verwenden
- **Python Fehler**: `pip install mido python-rtmidi` erneut ausführen

## Weitere Buttons hinzufügen

1. Weitere Pins im Arduino Code definieren
2. Verschiedene Control Change Nummern senden
3. Entsprechende Macros in Python hinzufügen