@echo off
REM Setup-Script für Windows

echo 🔧 Auto-Abrechnung Setup für Windows
echo =====================================

REM Prüfe ob Makefile.windows existiert
if not exist "Makefile.windows" (
    echo ❌ Makefile.windows nicht gefunden!
    pause
    exit /b 1
)

REM Lösche Linux-Makefile falls vorhanden
if exist "Makefile.linux" (
    echo 🗑️  Lösche Makefile.linux
    del Makefile.linux
)

REM Benenne Windows-Makefile um
echo 📝 Benenne Makefile.windows zu Makefile um
ren Makefile.windows Makefile

echo ✅ OS-spezifisches Setup abgeschlossen!
echo 📋 Führe 'make setup' aus um das Projekt zu initialisieren
pause