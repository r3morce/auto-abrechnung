# Makefile für Monatsabrechnung

.PHONY: help setup install run clean archive settlement settlement-run settlement-setup settlement-clean

# Standard target
help:
	@echo "Verfügbare Commands:"
	@echo ""
	@echo "Bank Statement Processing:"
	@echo "  setup     - Projekt komplett einrichten (venv + deps + dirs)"
	@echo "  install   - Dependencies installieren"
	@echo "  run       - Monatsabrechnung ausführen"
	@echo "  clean     - Temporäre Dateien löschen"
	@echo "  archive   - Output manuell archivieren"
	@echo ""
	@echo "Personal Expense Settlement:"
	@echo "  settlement-setup  - Settlement-Verzeichnisse erstellen"
	@echo "  settlement-run    - Settlement-Abrechnung ausführen"
	@echo "  settlement-clean  - Settlement-Archiv leeren"
	@echo "  settlement        - Alias für settlement-run"

# Projekt einrichten
setup: venv install dirs config settlement-setup
	@echo "✅ Projekt ist bereit!"
	@echo "Führe 'make run' aus um die Abrechnung zu starten"
	@echo "Führe 'make settlement-run' aus um die Settlement-Abrechnung zu starten"

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
	@mkdir -p input
	@mkdir -p output
	@mkdir -p output/archiv
	@mkdir -p config
	@mkdir -p modules
	@mkdir -p input/expenses
	@mkdir -p output/settlements
	@mkdir -p output/settlements/archiv

# Beispiel-Konfiguration erstellen
config:
	@echo "⚙️ Erstelle Beispiel-Konfiguration..."
	@[ ! -f "config/allowlist.yaml" ] && (echo "# Beispiel allowlist.yaml" > config/allowlist.yaml && echo "income_senders:" >> config/allowlist.yaml && echo "  - \"Beispiel Arbeitgeber\"" >> config/allowlist.yaml) || true
	@[ ! -f "config/blocklist.yaml" ] && (echo "# Beispiel blocklist.yaml" > config/blocklist.yaml && echo "expense_recipients:" >> config/blocklist.yaml && echo "  - \"Beispiel Bank\"" >> config/blocklist.yaml) || true
	@echo "✏️ Passe config/allowlist.yaml und config/blocklist.yaml an!"

# Hauptprogramm ausführen
run:
	@echo "🚀 Starte Monatsabrechnung..."
	python3 main.py

# Temporäre Dateien löschen
clean:
	@echo "🧹 Lösche temporäre Dateien..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ Aufräumen abgeschlossen"

# Output manuell archivieren
archive:
	@echo "📦 Archiviere Output-Dateien..."
	@mkdir -p output/archiv
	@mv output/monatsabrechnung_*.txt output/archiv/ 2>/dev/null || true
	@mv output/abrechnung_import_*.csv output/archiv/ 2>/dev/null || true
	@echo "✅ Dateien archiviert"

# Requirements.txt erstellen
freeze:
	@echo "📋 Erstelle requirements.txt..."
	pip freeze > requirements.txt

# Aus requirements.txt installieren
install-deps:
	@echo "📥 Installiere aus requirements.txt..."
	pip install -r requirements.txt

# Settlement-specific targets
settlement-setup:
	@echo "📋 Einrichten Settlement-Funktionalität..."
	@mkdir -p input/expenses
	@mkdir -p output/settlements
	@mkdir -p output/settlements/archiv
	@[ ! -f "settlement_config.yaml" ] && echo "⚠️  settlement_config.yaml fehlt - bitte erstellen!" || echo "✓ settlement_config.yaml gefunden"
	@echo "✅ Settlement-Verzeichnisse bereit!"

settlement-run: settlement
settlement:
	@echo "💰 Starte Settlement-Abrechnung..."
	@python3 settlement.py

settlement-clean:
	@echo "🧹 Lösche Settlement-Archiv..."
	@rm -rf output/settlements/archiv/* 2>/dev/null || true
	@echo "✅ Settlement-Archiv geleert"