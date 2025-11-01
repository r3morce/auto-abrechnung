# 💰 Monatsabrechnung

Ein Python-Programm zur automatischen Aufteilung von Monatskosten zwischen zwei Personen basierend auf Bankkontoauszügen der DKB.

## 🎯 Zweck

Das Programm liest Kontoauszüge ein und teilt alle relevanten Ausgaben 50/50 auf. Einnahmen werden berücksichtigt und reduzieren die zu teilenden Kosten. Am Ende zahlt jeder die Hälfte der Nettoausgaben.

## ⚡ Schnellstart

```bash
# Projekt einrichten
make setup

# CSV-Datei in input/ Ordner legen
# Konfiguration anpassen (siehe unten)

# Abrechnung ausführen
make run
```

## 📋 Voraussetzungen

- Python 3.7+
- PyYAML
- Make (optional, aber empfohlen)

## 🔧 OS-spezifisches Setup

**Wichtig:** Beim ersten Checkout des Projekts führe das Setup-Script aus:

```bash
./setup.sh
```

## 🛠️ Installation

### Mit Make (empfohlen)
```bash
make setup
```

### Manuell
```bash
# Virtual Environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Dependencies
pip install pyyaml

# Verzeichnisse erstellen
mkdir input output config modules
```

## ⚙️ Konfiguration

Erstelle zwei YAML-Dateien in `config/`:

### `config/allowlist.yaml`
Eingänge die berücksichtigt werden sollen:
```yaml
income_senders:
  - "Mein Arbeitgeber GmbH"
  - "Steueramt"
  - "Krankenkasse"
```

### `config/blocklist.yaml`
Ausgaben die NICHT berücksichtigt werden sollen:
```yaml
expense_recipients:
  - "Hausverwaltung"
  - "Stadtwerke"
  - "Sparkasse"
  - "Deutsche Bank"
```

## 📁 Verzeichnisstruktur

```
auto-abrechnung/
├── main.py                 # Hauptprogramm
├── modules/                # Programmmodule
│   ├── csv_reader.py      # CSV-Einlesung
│   ├── transaction_filter.py  # Filterung
│   ├── settlement_calculator.py  # Berechnung
│   ├── report_generator.py   # TXT-Report
│   └── csv_exporter.py    # CSV-Export
├── config/                 # Konfiguration
│   ├── settings.py        # Settings-Klasse
│   ├── allowlist.yaml     # Erlaubte Eingänge (erstellen)
│   └── blocklist.yaml     # Blockierte Ausgaben (erstellen)
├── input/                  # Kontoauszüge (CSV-Dateien)
├── output/                 # Generierte Abrechnungen
│   └── archiv/            # Archivierte Abrechnungen
├── Makefile               # Make-Commands
└── README.md              # Diese Datei
```

## 🚀 Verwendung

### 1. Kontoauszug vorbereiten
- CSV-Datei von der Bank herunterladen
- In `input/` Ordner legen
- Das Programm verwendet automatisch die neueste Datei

### 2. Konfiguration prüfen
- `config/allowlist.yaml` - Eingänge die zählen sollen
- `config/blocklist.yaml` - Ausgaben die ignoriert werden sollen

### 3. Abrechnung erstellen
```bash
make run
```

### 4. Ergebnisse prüfen
- **TXT-Report**: `output/monatsabrechnung_TIMESTAMP.txt`
- **Excel-CSV**: `output/abrechnung_import_TIMESTAMP.csv`

## 📊 CSV-Format (Bankauszug)

Das Programm erwartet CSV-Dateien mit folgenden Spalten:
- `Buchungsdatum`
- `Zahlungspflichtige*r` (Sender)
- `Zahlungsempfänger*in` (Empfänger)
- `Betrag (€)`
- `Verwendungszweck`
- `Umsatztyp`

## 🔧 Make-Commands

```bash
make help        # Alle verfügbaren Commands anzeigen
make setup       # Projekt komplett einrichten
make run         # Abrechnung ausführen
make clean       # Temporäre Dateien löschen
make archive     # Output manuell archivieren
```

## 📈 Beispiel-Ausgabe

```
=== Monatsabrechnung Programm ===

Verwende Kontoauszug: input\kontoauszug_mai.csv
Gefunden: 44 Transaktionen
Relevante Transaktionen: 30

Abrechnung erstellt: output\monatsabrechnung_20250602_151045.txt
Excel-Import erstellt: output\abrechnung_import_20250602_151045.csv

Gesamtausgaben: 847.23 €
Gesamteinnahmen: 150.00 €
Nettoausgaben: 697.23 €
Pro Person: 348.62 €
```

## 🧮 Berechnungslogik

1. **Ausgaben sammeln**: Alle Ausgaben außer blocklist
2. **Eingänge sammeln**: Nur Eingänge von allowlist
3. **Nettoausgaben**: Ausgaben - Eingänge
4. **Pro Person**: Nettoausgaben ÷ 2

**Beispiel:**
- Ausgaben: 1000€ (Supermarkt, Restaurants, etc.)
- Eingänge: 200€ (Krankenkassen-Erstattung)
- Nettoausgaben: 800€
- **Jeder zahlt: 400€**

## 🗃️ Archivierung

Alte Abrechnungen werden automatisch nach `output/archiv/` verschoben. Der `output/` Ordner enthält immer nur die neueste Abrechnung.

## 🔒 Datenschutz

- Kontoauszüge und Abrechnungen werden nicht versioniert (`.gitignore`)
- Persönliche Konfigurationsdateien bleiben lokal
- Nur der Programmcode wird geteilt

## 🐛 Fehlerbehebung

### "No module named 'config.settings'"
```bash
# Stelle sicher dass alle __init__.py Dateien existieren
make setup
```

### "Keine CSV-Dateien im input/ Ordner gefunden"
```bash
# CSV-Datei in input/ Ordner legen
# Dateiname ist egal, das neueste wird verwendet
```

### "PyYAML ist nicht installiert"
```bash
pip install pyyaml
# oder
make install
```