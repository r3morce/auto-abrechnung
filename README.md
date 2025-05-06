# Kontoauszug-Auswertung

Ein Python-Tool zur automatischen Auswertung von Kontoauszügen im CSV-Format.

## Funktionen

- Liest Kontoauszüge im CSV-Format ein
- Listet alle ausgehenden Umsätze mit Details auf
- Berechnet die Gesamtsumme und die halbe Summe
- Erstellt eine Übersicht der Ausgaben nach Empfängern
- Unterstützt eine Blocklist von Empfängern, die ignoriert werden sollen

## Projektstruktur

```
kontoauszug_auswertung/
│
├── main.py               # Hauptskript
├── config.py             # Konfigurationsfunktionen
├── utils.py              # Hilfsfunktionen
├── reporting.py          # Berichtsfunktionen
├── Makefile              # Automatisierungsskript für häufige Aufgaben
│
├── config/               # Konfigurationsdateien
│   └── blocklist.yml     # Liste der zu ignorierenden Empfänger
│
├── input/                # Eingabe-Dateien
│   └── *.csv             # CSV-Kontoauszüge
│
└── output/               # Ausgabe-Dateien
    ├── kontoauszug_auswertung_*.txt     # Detaillierte Auswertung
    ├── empfaenger_uebersicht_*.txt      # Übersicht nach Empfängern
    └── debug_log.txt                    # Detailliertes Debug-Log
```

## Installation

### Mit Make (empfohlen)

1. Installation unter Linux/macOS:
   ```
   make setup
   ```

2. Installation unter Windows:
   ```
   make setup-win
   ```

### Manuelle Installation

1. Stelle sicher, dass Python 3.6 oder höher installiert ist
2. Erstelle eine virtuelle Umgebung:
   ```
   python -m venv venv
   source venv/bin/activate  # unter Linux/macOS
   venv\Scripts\activate     # unter Windows
   ```
3. Installiere die benötigten Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```

## Verwendung

### Mit Make (empfohlen)

1. Platziere deine CSV-Kontoauszugsdatei im Ordner `input/`
2. Führe das Skript aus:
   ```
   make run       # unter Linux/macOS
   make run-win   # unter Windows
   ```

### Manuelle Verwendung

1. Platziere deine CSV-Kontoauszugsdatei im Ordner `input/`
2. Aktiviere die virtuelle Umgebung:
   ```
   source venv/bin/activate  # unter Linux/macOS
   venv\Scripts\activate     # unter Windows
   ```
3. Führe das Skript aus:
   ```
   python main.py
   ```

### Weitere Make-Befehle

- `make help` - Zeigt alle verfügbaren Befehle an
- `make clean` - Bereinigt temporäre Dateien und den Output-Ordner
- `make clean-all` - Bereinigt alle generierten Dateien und die virtuelle Umgebung
- `make update-deps` - Aktualisiert die Abhängigkeiten

## Blocklistformat

Die Blocklist-Datei (`config/blocklist.yml`) hat folgendes Format:

```yaml
blocklist:
  - "Empfänger 1"
  - "Empfänger 2"
  - "Weitere Empfänger"
```

Alle Empfänger, die in dieser Liste stehen, werden bei der Auswertung ignoriert.

## CSV-Format

Das Tool erwartet CSV-Dateien im folgenden Format:

- Semikolon (`;`) als Trennzeichen
- Doppelte Anführungszeichen (`"`) als Textkennzeichen
- Folgende Spalten müssen vorhanden sein:
  - `Betrag (€)`
  - `Zahlungsempfänger*in`
  - `Verwendungszweck`
  - `Umsatztyp`