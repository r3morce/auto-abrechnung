#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konfigurationsmodul für die Kontoauszug-Auswertung
"""

import os
import locale
import yaml

def setup_locale():
    """
    Setzt die Locale für deutsche Zahlenformatierung.
    """
    try:
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
    except:
        # Fallback falls de_DE.UTF-8 nicht verfügbar ist
        try:
            locale.setlocale(locale.LC_ALL, 'de_DE')
        except:
            print("Warnung: Konnte deutsche Lokalisierung nicht setzen.")

def load_blocklist(yaml_file='./config/blocklist.yml'):
    """
    Lädt die Blocklist aus einer YAML-Datei.
    
    Args:
        yaml_file (str): Pfad zur YAML-Datei mit der Blocklist
        
    Returns:
        list: Liste mit zu blockierenden Empfängern
    """
    # Standardwert: leere Blocklist
    blocklist = []
    
    # Prüfe, ob die Datei existiert
    if os.path.exists(yaml_file):
        try:
            with open(yaml_file, 'r', encoding='utf-8') as file:
                data = yaml.safe_load(file)
                # Prüfe, ob 'blocklist' im YAML vorhanden ist und eine Liste ist
                if data and 'blocklist' in data and isinstance(data['blocklist'], list):
                    blocklist = data['blocklist']
                    print(f"Blocklist mit {len(blocklist)} Einträgen geladen.")
                else:
                    print("Warnung: Ungültiges Format der Blocklist. Verwende leere Blocklist.")
        except Exception as e:
            print(f"Fehler beim Laden der Blocklist: {e}")
    else:
        print(f"Blocklist-Datei {yaml_file} nicht gefunden. Erstelle Beispieldatei.")
        # Erstelle Beispiel-Blocklist, wenn keine existiert
        example_blocklist = {'blocklist': ['Beispiel GmbH', 'Unerwünschter Empfänger']}
        os.makedirs(os.path.dirname(yaml_file), exist_ok=True)
        try:
            with open(yaml_file, 'w', encoding='utf-8') as file:
                yaml.dump(example_blocklist, file, default_flow_style=False)
            print(f"Beispiel-Blocklist erstellt unter {yaml_file}")
        except Exception as e:
            print(f"Fehler beim Erstellen der Beispiel-Blocklist: {e}")
    
    return blocklist