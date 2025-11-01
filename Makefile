# Makefile für Monatsabrechnung

.PHONY: help setup install run clean archive

# Standard target
help:
	@echo "Verfügbare Commands:"
	@echo "  setup     - Projekt komplett einrichten (venv + deps + dirs)"
	@echo "  install   - Dependencies installieren"
	@echo "  run       - Monatsabrechnung ausführen"
	@echo "  clean     - Temporäre Dateien löschen"
	@echo "  archive   - Output manuell archivieren"

# Projekt einrichten
setup: venv install dirs config
	@echo "✅ Projekt ist bereit!"
	@echo "Führe 'make run' aus um die Abrechnung zu starten"

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