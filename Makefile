# Makefile für Monatsabrechnung

.PHONY: help setup install clean run venv freeze install-deps config test tui
.PHONY: bank-setup bank-run bank-clean bank-archive
.PHONY: paper-setup paper-run paper-clean

# Standard target
help:
	@echo "Verfügbare Commands:"
	@echo ""
	@echo "General:"
	@echo "  setup          - Komplettes Setup (bank + paper)"
	@echo "  run            - Beide Abrechnungen ausführen (bank + paper)"
	@echo "  install        - Dependencies installieren"
	@echo "  clean          - Temporäre Dateien löschen"
	@echo ""
	@echo "Bank Processing:"
	@echo "  bank-setup     - Bank-Verzeichnisse erstellen"
	@echo "  bank-run       - Bank-Abrechnung ausführen"
	@echo "  bank-clean     - Bank-Archiv leeren"
	@echo "  bank-archive   - Bank-Output archivieren"
	@echo ""
	@echo "Paper Processing:"
	@echo "  paper-setup    - Paper-Verzeichnisse erstellen"
	@echo "  paper-run      - Paper-Abrechnung ausführen"
	@echo "  paper-clean    - Paper-Archiv leeren"

# Komplettes Setup
setup: venv install dirs config bank-setup paper-setup
	@echo "✅ Projekt ist bereit!"
	@echo "Führe 'make bank-run' aus um die Bank-Abrechnung zu starten"
	@echo "Führe 'make paper-run' aus um die Paper-Abrechnung zu starten"

# Virtual Environment erstellen
venv:
	@echo "📦 Erstelle Virtual Environment..."
	python3 -m venv venv
	@echo "Aktiviere mit: source venv/bin/activate"

# Dependencies installieren
install:
	@echo "📥 Installiere Dependencies..."
	pip install pyyaml

# Verzeichnisse erstellen
dirs:
	@echo "📁 Erstelle Verzeichnisse..."
	@mkdir -p config modules
	@mkdir -p input/bank input/paper
	@mkdir -p output/bank/archiv output/paper/archiv

# Beispiel-Konfiguration erstellen
config:
	@echo "⚙️ Erstelle Beispiel-Konfiguration..."
	@[ ! -f "config/allowlist.yaml" ] && (echo "# Beispiel allowlist.yaml" > config/allowlist.yaml && echo "income_senders:" >> config/allowlist.yaml && echo "  - \"Beispiel Arbeitgeber\"" >> config/allowlist.yaml) || true
	@[ ! -f "config/blocklist.yaml" ] && (echo "# Beispiel blocklist.yaml" > config/blocklist.yaml && echo "expense_recipients:" >> config/blocklist.yaml && echo "  - \"Beispiel Bank\"" >> config/blocklist.yaml) || true
	@echo "✏️ Passe config/allowlist.yaml und config/blocklist.yaml an!"

# Temporäre Dateien löschen
clean:
	@echo "🧹 Lösche temporäre Dateien..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Aufräumen abgeschlossen"

# Python aus dem venv bevorzugen, sonst system python3
PY := $(shell [ -x venv/bin/python ] && echo venv/bin/python || echo python3)

# TUI starten
tui:
	@echo "🖼️  Starte TUI..."
	$(PY) -m tui

# Tests ausführen
test:
	@echo "🧪 Starte pytest..."
	$(PY) -m pytest tests/ -v

# Beide Abrechnungen ausführen
run: bank-run paper-run
	@echo "✅ Beide Abrechnungen abgeschlossen!"

# Requirements.txt erstellen
freeze:
	@echo "📋 Erstelle requirements.txt..."
	pip freeze > requirements.txt

# Aus requirements.txt installieren
install-deps:
	@echo "📥 Installiere aus requirements.txt..."
	pip install -r requirements.txt

# Bank targets
bank-setup:
	@echo "📋 Bank-Setup..."
	@mkdir -p input/bank output/bank/archiv config
	@[ ! -f "config_bank.yaml" ] && echo "⚠️  config_bank.yaml fehlt - bitte erstellen!" || echo "✓ config_bank.yaml gefunden"
	@echo "✅ Bank-Verzeichnisse bereit!"

bank-run:
	@echo "🏦 Starte Bank-Abrechnung..."
	python3 bank.py

bank-clean:
	@echo "🧹 Lösche Bank-Archiv..."
	@rm -rf output/bank/archiv/* 2>/dev/null || true
	@echo "✅ Bank-Archiv geleert"

bank-archive:
	@echo "📦 Archiviere Bank-Dateien..."
	@mkdir -p output/bank/archiv
	@find output/bank -maxdepth 2 -name "monatsabrechnung_*.txt" -exec mv {} output/bank/archiv/ \; 2>/dev/null || true
	@find output/bank -maxdepth 2 -name "monatsabrechnung_*.csv" -exec mv {} output/bank/archiv/ \; 2>/dev/null || true
	@echo "✅ Dateien archiviert"

# Paper targets
paper-setup:
	@echo "📋 Paper-Setup..."
	@mkdir -p input/paper output/paper/archiv config
	@[ ! -f "config_paper.yaml" ] && echo "⚠️  config_paper.yaml fehlt - bitte erstellen!" || echo "✓ config_paper.yaml gefunden"
	@echo "✅ Paper-Verzeichnisse bereit!"

paper-run:
	@echo "💰 Starte Paper-Abrechnung..."
	python3 paper.py

paper-clean:
	@echo "🧹 Lösche Paper-Archiv..."
	@rm -rf output/paper/archiv/* 2>/dev/null || true
	@echo "✅ Paper-Archiv geleert"
