# Makefile für Monatsabrechnung

.PHONY: help setup install run clean archive test lint format check

# Standard target
help:
	@echo "Verfügbare Commands:"
	@echo "  setup     - Projekt komplett einrichten (venv + deps + dirs)"
	@echo "  install   - Dependencies installieren"
	@echo "  run       - Monatsabrechnung ausführen"
	@echo "  clean     - Temporäre Dateien löschen"
	@echo "  archive   - Output manuell archivieren"
	@echo "  test      - Tests ausführen"
	@echo "  lint      - Code-Qualität prüfen"
	@echo "  format    - Code formatieren"
	@echo "  check     - Vollständige Code-Prüfung"

# Projekt einrichten
setup: venv install dirs config
	@echo "✅ Projekt ist bereit!"
	@echo "Führe 'make run' aus um die Abrechnung zu starten"

# Virtual Environment erstellen
venv:
	@echo "📦 Erstelle Virtual Environment..."
	python -m venv venv
	@echo "Aktiviere mit: venv\\Scripts\\activate (Windows) oder source venv/bin/activate (Linux/Mac)"

# Dependencies installieren
install:
	@echo "📥 Installiere Dependencies..."
	pip install pyyaml
	pip install flake8 black pytest

# Verzeichnisse erstellen
dirs:
	@echo "📁 Erstelle Verzeichnisse..."
	@if not exist "input" mkdir input
	@if not exist "output" mkdir output
	@if not exist "output\\archiv" mkdir output\\archiv
	@if not exist "config" mkdir config
	@if not exist "modules" mkdir modules

# Beispiel-Konfiguration erstellen
config:
	@echo "⚙️ Erstelle Beispiel-Konfiguration..."
	@if not exist "config\\allowlist.yaml" (echo # Beispiel allowlist.yaml > config\\allowlist.yaml && echo income_senders: >> config\\allowlist.yaml && echo   - "Beispiel Arbeitgeber" >> config\\allowlist.yaml)
	@if not exist "config\\blocklist.yaml" (echo # Beispiel blocklist.yaml > config\\blocklist.yaml && echo expense_recipients: >> config\\blocklist.yaml && echo   - "Beispiel Bank" >> config\\blocklist.yaml)
	@echo "✏️ Passe config\\allowlist.yaml und config\\blocklist.yaml an!"

# Hauptprogramm ausführen
run:
	@echo "🚀 Starte Monatsabrechnung..."
	python main.py

# Temporäre Dateien löschen
clean:
	@echo "🧹 Lösche temporäre Dateien..."
	@if exist "__pycache__" rmdir /s /q __pycache__
	@if exist "modules\\__pycache__" rmdir /s /q modules\\__pycache__
	@if exist "config\\__pycache__" rmdir /s /q config\\__pycache__
	@for /f %%i in ('dir /b /s *.pyc 2^>nul') do del "%%i"
	@echo "✅ Aufräumen abgeschlossen"

# Output manuell archivieren
archive:
	@echo "📦 Archiviere Output-Dateien..."
	@if not exist "output\\archiv" mkdir output\\archiv
	@for %%f in (output\\monatsabrechnung_*.txt) do move "%%f" "output\\archiv\\"
	@for %%f in (output\\abrechnung_import_*.csv) do move "%%f" "output\\archiv\\"
	@echo "✅ Dateien archiviert"

# Tests ausführen
test:
	@echo "🧪 Führe Tests aus..."
	python -m pytest tests/ -v

# Code-Qualität prüfen
lint:
	@echo "🔍 Prüfe Code-Qualität..."
	flake8 main.py modules/ config/ --max-line-length=100

# Code formatieren
format:
	@echo "✨ Formatiere Code..."
	black main.py modules/ config/ --line-length=100

# Vollständige Prüfung
check: lint test
	@echo "✅ Code-Prüfung abgeschlossen"

# Development setup (mit dev dependencies)
dev-setup: setup
	@echo "👨‍💻 Installiere Development Tools..."
	pip install pytest black flake8 mypy

# Requirements.txt erstellen
freeze:
	@echo "📋 Erstelle requirements.txt..."
	pip freeze > requirements.txt

# Aus requirements.txt installieren
install-deps:
	@echo "📥 Installiere aus requirements.txt..."
	pip install -r requirements.txt