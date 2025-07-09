# Arduino Nano MIDI Macro Controller

Ein Arduino Nano basierter MIDI Controller, der Button-Presses in PC-Macros verwandelt. Perfekt für Shortcuts, App-Starts oder automatisierte Aktionen.

## Features

- 🎹 **MIDI Controller**: Arduino sendet MIDI Control Change Messages
- 🖥️ **PC Macros**: Python Script führt beliebige Aktionen aus
- 🔘 **Button Input**: Einfache Taster-Eingabe mit Debouncing
- 💡 **LED Feedback**: Visueller Status-Indikator
- 🌍 **Platform Support**: Mac, Linux, Windows
- 🔌 **Plug & Play**: USB-Verbindung, keine zusätzliche Hardware

## Hardware

### Komponenten
- Arduino Nano (ATmega328P)
- Steckboard (Breadboard)
- Taster (Push Button)
- LED (optional)
- Widerstände (10kΩ Pull-up, 220Ω für LED)

### Verkabelung
```
Arduino Pin 2  ← Button → GND
Arduino Pin 10 ← LED (mit 220Ω) → GND
```

Detaillierte Verkabelung siehe `wiring_diagram.txt`

## Software

### Dateien
- `midi_controller.ino` - Arduino Sketch
- `serial_macro_bridge.py` - Serial-zu-Macro Bridge (empfohlen)
- `midi_macro_bridge.py` - MIDI-zu-Macro Bridge (optional)
- `setup_guide.md` - Detaillierte Installationsanleitung
- `wiring_diagram.txt` - Hardware-Verkabelung

## Quick Start

1. **Hardware aufbauen** (siehe `wiring_diagram.txt`)
2. **Arduino flashen**:
   ```bash
   # Arduino IDE installieren
   brew install --cask arduino-ide
   
   # MIDI Library installieren (Tools → Manage Libraries → "MIDI Library")
   # midi_controller.ino laden und auf Arduino Nano flashen
   ```

3. **Python Dependencies**:
   ```bash
   pip install pyserial
   ```

4. **Macro Bridge starten**:
   ```bash
   # Verfügbare Ports anzeigen
   python3 serial_macro_bridge.py
   
   # Mit Arduino verbinden
   python3 serial_macro_bridge.py "/dev/cu.usbserial-10"
   ```

5. **Testen**: Button drücken → Terminal öffnet sich mit "hello world"

## Macros anpassen

In `serial_macro_bridge.py` die `macro_1` Funktion bearbeiten:

```python
def macro_1(self):
    # Beispiele:
    
    # Terminal mit Befehl öffnen
    subprocess.run(["osascript", "-e", 'tell application "Terminal" to do script "echo hello world"'])
    
    # Screenshot machen
    subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke "4" using {command down, shift down}'])
    
    # App öffnen
    subprocess.run(["open", "-a", "Calculator"])
    
    # Spotlight öffnen
    subprocess.run(["osascript", "-e", 'tell application "System Events" to keystroke space using command down'])
```

## Erweiterte Nutzung

### Mehrere Buttons
1. Weitere Pins im Arduino Code definieren
2. Verschiedene Control Change Nummern senden
3. Entsprechende Macros in Python hinzufügen

### Weitere Platforms
- **Linux**: `xdotool` für Tastatur-Simulation
- **Windows**: PowerShell SendKeys für Automation

## Troubleshooting

| Problem | Lösung |
|---------|---------|
| Arduino nicht erkannt | Treiber installieren, anderen USB-Port probieren |
| Button reagiert nicht | Pull-up Widerstand prüfen |
| Python Fehler | `pip install pyserial` erneut ausführen |
| Keine seriellen Ports | Arduino IDE Serial Monitor schließen |

## Lizenz

Open Source - frei verwendbar für private und kommerzielle Projekte.

## Beiträge

Gerne! Issues und Pull Requests sind willkommen.

---

*Erstellt mit ❤️ für Maker und Automation-Enthusiasten*