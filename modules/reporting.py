#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Berichterstattungsfunktionen für die Kontoauszug-Auswertung
"""

from modules.utils import format_euro

def write_reports(data, output_file, summary_file):
    """
    Schreibt die Berichte für die Kontoauszug-Auswertung.
    
    Args:
        data (dict): Dictionary mit allen nötigen Daten
        output_file (str): Pfad zur Ausgabedatei
        summary_file (str): Pfad zur Übersichtsdatei
    """
    write_main_report(data, output_file)
    write_summary_report(data, summary_file)

def write_main_report(data, output_file):
    """
    Schreibt den Hauptbericht mit allen Transaktionsdetails.
    
    Args:
        data (dict): Dictionary mit allen nötigen Daten
        output_file (str): Pfad zur Ausgabedatei
    """
    ausgehende_umsaetze = data['ausgehende_umsaetze']
    blockierte_umsaetze = data['blockierte_umsaetze']
    summe_ausgehend = data['summe_ausgehend']
    summe_geteilt = data['summe_geteilt']
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("Auswertung Kontoauszug\n")
        outfile.write("======================\n\n")
        
        outfile.write("Ausgehende Umsätze:\n")
        outfile.write("-----------------\n")
        
        for umsatz in ausgehende_umsaetze:
            outfile.write(f"Empfänger: {umsatz['empfaenger']}\n")
            outfile.write(f"Verwendungszweck: {umsatz['verwendungszweck']}\n")
            outfile.write(f"Betrag: {format_euro(umsatz['betrag'])}\n")
            outfile.write("-----------------\n")
        
        outfile.write(f"\nSumme aller ausgehenden Umsätze: {format_euro(summe_ausgehend)}\n")
        outfile.write(f"Die Hälfte der Summe: {format_euro(summe_geteilt)}\n")
        
        if blockierte_umsaetze:
            outfile.write(f"\nHinweis: Es wurden {len(blockierte_umsaetze)} Umsätze aufgrund der Blocklist ignoriert.\n")

def write_summary_report(data, summary_file):
    """
    Schreibt die Übersicht der Ausgaben nach Empfängern.
    
    Args:
        data (dict): Dictionary mit allen nötigen Daten
        summary_file (str): Pfad zur Übersichtsdatei
    """
    empfaenger_summen = data['empfaenger_summen']
    summe_ausgehend = data['summe_ausgehend']
    summe_geteilt = data['summe_geteilt']
    
    with open(summary_file, 'w', encoding='utf-8') as summary:
        summary.write("Übersicht der Ausgaben nach Empfängern\n")
        summary.write("=====================================\n\n")
        
        # Sortiere Empfänger nach Betrag (absteigend)
        sorted_empfaenger = sorted(empfaenger_summen.items(), key=lambda x: x[1], reverse=True)
        
        # Schreibe die Tabelle
        summary.write("Empfänger                                   | Betrag     | Prozentanteil\n")
        summary.write("-------------------------------------------|------------|---------------\n")
        
        for empfaenger, betrag in sorted_empfaenger:
            prozent = (betrag / summe_ausgehend) * 100 if summe_ausgehend > 0 else 0
            summary.write(f"{empfaenger[:43]:<43} | {format_euro(betrag):<10} | {prozent:.2f}%\n")
        
        summary.write("\n")
        summary.write(f"Gesamtsumme: {format_euro(summe_ausgehend)}\n")
        summary.write(f"Die Hälfte der Summe: {format_euro(summe_geteilt)}\n")