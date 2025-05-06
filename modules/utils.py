#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hilfsfunktionen für die Kontoauszug-Auswertung
"""

def betrag_to_float(betrag_str):
    """
    Konvertiert einen Betrag-String (z.B. "-5" oder "10,50 €") in einen Float.
    
    Args:
        betrag_str (str): Zu konvertierender Betrag als String
        
    Returns:
        float: Konvertierter Betrag als Float
    """
    # Entferne das Euro-Symbol und Leerzeichen
    betrag_str = betrag_str.replace('€', '').strip()
    # Ersetze Komma durch Punkt für float-Konvertierung
    betrag_str = betrag_str.replace(',', '.')
    
    try:
        return float(betrag_str)
    except ValueError:
        print(f"Fehler beim Konvertieren des Betrags: {betrag_str}")
        return 0.0

def format_euro(betrag):
    """
    Formatiert einen Float-Wert als Euro-Betrag.
    
    Args:
        betrag (float): Zu formatierender Betrag
        
    Returns:
        str: Formatierter Betrag im Format "123,45 €"
    """
    return f"{betrag:.2f} €".replace('.', ',')