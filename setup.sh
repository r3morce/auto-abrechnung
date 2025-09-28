#!/bin/bash
# Setup-Script für Linux/macOS

echo "🔧 Auto-Abrechnung Setup für Linux/macOS"
echo "========================================"

# Prüfe ob Makefile.linux existiert
if [ ! -f "Makefile.linux" ]; then
    echo "❌ Makefile.linux nicht gefunden!"
    exit 1
fi

# Lösche Windows-Makefile falls vorhanden
if [ -f "Makefile.windows" ]; then
    echo "🗑️  Lösche Makefile.windows"
    rm Makefile.windows
fi

# Benenne Linux-Makefile um
echo "📝 Benenne Makefile.linux zu Makefile um"
mv Makefile.linux Makefile

echo "✅ OS-spezifisches Setup abgeschlossen!"
echo "📋 Führe 'make setup' aus um das Projekt zu initialisieren"