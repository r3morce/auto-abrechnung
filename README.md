# 💰 Monatsabrechnung

Automatische Aufteilung von Monatskosten zwischen zwei Personen.

**Zwei Modi:**
1. **Bank Statement** - DKB-Kontoauszüge automatisch aufteilen
2. **Personal Expenses** - Manuelle Ausgaben 50/50 teilen

## ⚡ Schnellstart

```bash
make setup              # Projekt einrichten (bank + paper)
make run                # Beide Abrechnungen ausführen
# oder einzeln:
make bank-run           # Bank-Abrechnung
make paper-run          # Personal-Abrechnung
```

## 📋 Voraussetzungen

- Python 3.7+
- PyYAML (`pip install pyyaml`)

## 🔧 Verfügbare Commands

### General
```bash
make setup            # Komplettes Setup (bank + paper)
make run              # Beide Abrechnungen ausführen
make clean            # Temporäre Dateien löschen
```

### Bank Statement Processing
```bash
make bank-setup       # Bank-Setup
make bank-run         # Abrechnung ausführen
make bank-archive     # Output archivieren
make bank-clean       # Archiv leeren
```

### Personal Expense Settlement
```bash
make paper-setup      # Paper-Setup
make paper-run        # Abrechnung ausführen
make paper-clean      # Archiv leeren
```

---

## 🏦 Bank Statement Processing

### Setup
1. Projekt einrichten: `make setup`
2. Konfigurationsdateien anpassen:
   - `config/allowlist.yaml` - Erlaubte Eingänge
   - `config/blocklist.yaml` - Ignorierte Ausgaben

### Konfiguration

**`config/allowlist.yaml`** - Welche Eingänge werden berücksichtigt:
```yaml
income_senders:
  - "Arbeitgeber GmbH"
  - "Krankenkasse"
```

**`config/blocklist.yaml`** - Welche Ausgaben werden ignoriert:
```yaml
expense_recipients:
  - "Hausverwaltung"
  - "Stadtwerke"
  - "Sparkasse"
```

### Verwendung
1. CSV-Kontoauszug von Bank herunterladen
2. In `input/bank/` Ordner legen
3. `make bank-run` ausführen
4. Ergebnisse in `output/bank/` prüfen

### CSV-Format (DKB Bank)
Benötigte Spalten: `Buchungsdatum`, `Zahlungspflichtige*r`, `Zahlungsempfänger*in`, `Betrag (€)`, `Verwendungszweck`, `Umsatztyp`

---

## 💵 Personal Expense Settlement

### Setup
1. Projekt einrichten: `make setup`
2. Verzeichnisse erstellen: `make settlement-setup`
3. Config erstellen: `cp config_paper.example.yaml config_paper.yaml`
4. Config anpassen (Pfade, falls nötig)

### CSV-Format (Personal Expenses)

Siehe `input/expenses/example.csv` als Vorlage. Erstelle CSV-Datei in `input/expenses/`:

```csv
25
11
person;amount;comment
a;45,50;Supermarkt
b;120,00;Elektronik
a;30,00;Tankstelle
```

**Format:**
- Zeile 1: Jahr (2-stellig, z.B. "25" für 2025)
- Zeile 2: Monat (1- oder 2-stellig, z.B. "11" für November)
- Zeile 3: Header-Zeile
- Zeile 4+: Daten

**Felder:**
- `person` - 'a', 'b', oder 'm' (case-insensitive, konfigurierbar)
- `amount` - Betrag (Dezimalformat gemäß `csv_delimiter` in config)
- `comment` - Optional

**Hinweis:** Trennzeichen muss mit `csv_delimiter` in `config_paper.yaml` übereinstimmen

### Konfiguration

Kopiere `config_paper.example.yaml` zu `config_paper.yaml` und passe an:

**`config_paper.yaml`:**
```yaml
input_folder: input/paper             # Eingabe-Ordner
output_folder: output/paper           # Ausgabe-Ordner
csv_delimiter: ";"                    # CSV-Trennzeichen (Semikolon oder Komma)
input_encoding: "utf-8"               # Zeichenkodierung
valid_persons:
  - a                                 # Erlaubte Personen-Kennungen
  - b                                 # (kann auch 'm' enthalten)
  - m
generate_text_report: true            # TXT-Report generieren
generate_csv_report: true             # CSV-Report generieren
archive_old_files: true               # Alte Dateien archivieren
```

**Hinweis:** Das Script verwendet automatisch die neueste CSV-Datei im Eingabe-Ordner.

### Verwendung
1. CSV-Datei in `input/paper/` erstellen
2. `make paper-run` ausführen
3. Ergebnisse in `output/paper/` prüfen

### Beispiel-Ausgabe
```
Person A:            150.00 €
Person M:            200.00 €
------------------------------------------------------------
Gesamt:              350.00 €
Pro Person:          175.00 €

AUSGLEICHSZAHLUNG:
  A zahlt an M: 25.00 €
```

---

## 📁 Verzeichnisstruktur

```
auto-abrechnung/
├── bank.py                 # Bank Statement Processing
├── paper.py                # Personal Expense Settlement
├── modules/                # Programmmodule
├── config/                 # Konfigurationsdateien
├── input/
│   ├── bank/              # Bank-CSVs
│   └── paper/             # Personal Expense CSVs
└── output/
    ├── bank/              # Bank Reports & archiv/
    └── paper/             # Paper Reports & archiv/
```

## 🐛 Fehlerbehebung

**"Keine CSV-Dateien gefunden"**
- Datei in richtigen Ordner legen (`input/bank/` oder `input/paper/`)

**"PyYAML nicht installiert"**
- `pip install pyyaml` oder `make install`

**"Ungültige Person 'x'"**
- Nur erlaubte Personen im `person`-Feld verwenden (Standard: 'a', 'b', 'm')
- Prüfe `valid_persons` in `config_paper.yaml`

**"Validierung fehlgeschlagen"**
- CSV-Format prüfen: `person,amount,comment`
- Betrag als Zahl eingeben (12.50 oder 12,50)
