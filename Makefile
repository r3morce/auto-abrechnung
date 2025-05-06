# Makefile für Kontoauszug-Auswertung

# Variablen
PYTHON = python
PIP = pip3
VENV = venv
VENV_ACTIVATE = $(VENV)/bin/activate
VENV_ACTIVATE_WIN = $(VENV)\Scripts\activate

# Standard-Ziel
.PHONY: all
all: help

# Hilfe anzeigen
.PHONY: help
help:
	@echo "Verfügbare Befehle:"
	@echo "  make setup       - Virtuelle Umgebung erstellen und Abhängigkeiten installieren"
	@echo "  make setup-win   - Virtuelle Umgebung unter Windows erstellen"
	@echo "  make run         - Kontoauszug-Auswertung ausführen"
	@echo "  make clean       - Bereinigte temporäre Dateien und Output-Verzeichnis"
	@echo "  make clean-all   - Wie clean, entfernt zudem die virtuelle Umgebung"
	@echo "  make update-deps - Abhängigkeiten in der virtuellen Umgebung aktualisieren"

# Virtuelle Umgebung erstellen (Linux/macOS)
.PHONY: setup
setup: $(VENV_ACTIVATE)

$(VENV_ACTIVATE):
	@echo "Erstelle virtuelle Python-Umgebung..."
	$(PYTHON) -m venv $(VENV)
	@echo "Installiere Abhängigkeiten..."
	. $(VENV_ACTIVATE) && $(PIP) install -r requirements.txt
	@echo "Setup abgeschlossen. Aktiviere die Umgebung mit 'source $(VENV_ACTIVATE)'"

# Virtuelle Umgebung erstellen (Windows)
.PHONY: setup-win
setup-win:
	@echo "Erstelle virtuelle Python-Umgebung für Windows..."
	$(PYTHON) -m venv $(VENV)
	@echo "Installiere Abhängigkeiten..."
	$(VENV)\Scripts\pip install -r requirements.txt
	@echo "Setup abgeschlossen. Aktiviere die Umgebung mit '$(VENV_ACTIVATE_WIN)'"

# Abhängigkeiten aktualisieren
.PHONY: update-deps
update-deps:
	@echo "Aktualisiere Abhängigkeiten..."
	. $(VENV_ACTIVATE) && $(PIP) install --upgrade -r requirements.txt
	@echo "Abhängigkeiten aktualisiert."

# Kontoauszug-Auswertung ausführen
.PHONY: run
run:
	@echo "Führe Kontoauszug-Auswertung aus..."
	. $(VENV_ACTIVATE) && $(PYTHON) main.py
	@echo "Auswertung abgeschlossen. Ergebnisse im Verzeichnis 'output/'."

# Unter Windows ausführen
.PHONY: run-win
run-win:
	@echo "Führe Kontoauszug-Auswertung aus (Windows)..."
	$(VENV)\Scripts\python main.py
	@echo "Auswertung abgeschlossen. Ergebnisse im Verzeichnis 'output/'."


# Aufräumen - Entfernt temporäre Dateien und Output-Verzeichnis
.PHONY: clean
clean:
	@echo "Entferne temporäre Dateien und Output-Verzeichnis..."
	rm -rf output/*
	rm -rf __pycache__/
	rm -rf *.pyc
	@echo "Bereinigung abgeschlossen."

# Vollständiges Aufräumen - Entfernt auch die virtuelle Umgebung
.PHONY: clean-all
clean-all: clean
	@echo "Entferne virtuelle Umgebung..."
	rm -rf $(VENV)
	@echo "Vollständige Bereinigung abgeschlossen."