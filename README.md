# 💰 Monatsabrechnung

Automatische Aufteilung von Monatskosten zwischen zwei Personen.

**Zwei Modi:**
1. **Bank Statement** - DKB-Kontoauszüge automatisch aufteilen
2. **Personal Expenses** - Manuelle Ausgaben 50/50 teilen

## ⚡ Schnellstart

```bash
make setup              # Projekt einrichten
make run                # Bank-Abrechnung
make settlement         # Personal-Abrechnung
```

## 📋 Voraussetzungen

- Python 3.7+
- PyYAML (`pip install pyyaml`)

## 🔧 Verfügbare Commands

### Bank Statement Processing
```bash
make setup       # Projekt einrichten
make run         # Abrechnung ausführen
make archive     # Output archivieren
make clean       # Temporäre Dateien löschen
```

### Personal Expense Settlement
```bash
make settlement-setup  # Verzeichnisse erstellen
make settlement        # Abrechnung ausführen
make settlement-clean  # Archiv leeren
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
2. In `input/` Ordner legen
3. `make run` ausführen
4. Ergebnisse in `output/` prüfen

### CSV-Format (DKB Bank)
Benötigte Spalten: `Buchungsdatum`, `Zahlungspflichtige*r`, `Zahlungsempfänger*in`, `Betrag (€)`, `Verwendungszweck`, `Umsatztyp`

---

## 💵 Personal Expense Settlement

### Setup
1. Projekt einrichten: `make setup`
2. Verzeichnisse erstellen: `make settlement-setup`
3. Config erstellen: `cp settlement_config.example.yaml settlement_config.yaml`
4. Config anpassen (Pfade, falls nötig)

### CSV-Format (Personal Expenses)

Siehe `input/expenses/example.csv` als Vorlage. Erstelle CSV-Datei in `input/expenses/`:

```csv
person;amount;comment
a;45,50;Supermarkt
b;120,00;Elektronik
a;30,00;Tankstelle
```

**Felder:**
- `person` - 'a' oder 'b' (case-insensitive)
- `amount` - Betrag (Dezimalformat gemäß `csv_delimiter` in config)
- `comment` - Optional

**Hinweis:** Trennzeichen muss mit `csv_delimiter` in `settlement_config.yaml` übereinstimmen

### Konfiguration

Kopiere `settlement_config.example.yaml` zu `settlement_config.yaml` und passe an:

**`settlement_config.yaml`:**
```yaml
input_folder: input/expenses          # Eingabe-Ordner
output_folder: output/settlements     # Ausgabe-Ordner
csv_delimiter: ";"                    # CSV-Trennzeichen (Semikolon oder Komma)
input_encoding: "utf-8"               # Zeichenkodierung
auto_find_latest: true                # Automatisch neueste Datei verwenden
valid_persons:
  - a                                 # Erlaubte Personen-Kennungen
  - b
generate_text_report: true            # TXT-Report generieren
generate_csv_report: true             # CSV-Report generieren
archive_old_files: true               # Alte Dateien archivieren
```

### Verwendung
1. CSV-Datei in `input/expenses/` erstellen
2. `make settlement` ausführen
3. Ergebnisse in `output/settlements/` prüfen

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
├── main.py                 # Bank Statement Processing
├── settlement.py           # Personal Expense Settlement
├── modules/                # Programmmodule
├── config/                 # Konfigurationsdateien
├── input/                  # Bank-CSVs
│   └── expenses/          # Personal Expense CSVs
└── output/                 # Generierte Reports
    ├── archiv/
    └── settlements/
```

## 🐛 Fehlerbehebung

**"Keine CSV-Dateien gefunden"**
- Datei in richtigen Ordner legen (`input/` oder `input/expenses/`)

**"PyYAML nicht installiert"**
- `pip install pyyaml` oder `make install`

**"Ungültige Person 'x'"**
- Nur 'a' oder 'b' im `person`-Feld verwenden

**"Validierung fehlgeschlagen"**
- CSV-Format prüfen: `person,amount,comment`
- Betrag als Zahl eingeben (12.50 oder 12,50)
