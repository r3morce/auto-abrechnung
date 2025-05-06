#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hauptdatei für die Kontoauszug-Auswertung
"""

import os
from datetime import datetime
import glob
import csv
from modules.config import load_blocklist, setup_locale
from modules.utils import betrag_to_float, format_euro
from modules.reporting import write_reports

def main():
    """
    Hauptfunktion zur Verarbeitung der Kontoauszüge
    """
    # Setze Locale für deutsche Zahlenformatierung
    setup_locale()
    
    # Debug-Log-Datei
    debug_file = "./output/debug_log.txt"
    
    # Suche nach CSV-Dateien im input-Ordner
    csv_files = glob.glob('./input/*.csv')
    
    if not csv_files:
        print("Keine CSV-Dateien im Ordner './input/' gefunden.")
        return
    
    # Erstelle output-Ordner, falls nicht vorhanden
    os.makedirs('./output', exist_ok=True)
    
    # Aktuelles Datum für den Ausgabedateinamen
    current_date = datetime.now().strftime("%Y%m%d")
    output_file = f"./output/kontoauszug_auswertung_{current_date}.txt"
    summary_file = f"./output/empfaenger_uebersicht_{current_date}.txt"
    
    # Lösche vorherige Debug-Datei, falls vorhanden
    if os.path.exists(debug_file):
        os.remove(debug_file)
    
    # Lade die Blocklist
    blocklist = load_blocklist()
    
    # Debug-Ausgabe initialisieren
    with open(debug_file, 'w', encoding='utf-8') as debug:
        debug.write("DEBUG-LOG FÜR KONTOAUSZUG-AUSWERTUNG\n")
        debug.write("====================================\n\n")
        debug.write(f"Verarbeite Datei: {csv_files[0]}\n")
        debug.write(f"Geladene Blocklist: {blocklist}\n\n")
    
    ausgehende_umsaetze = []
    blockierte_umsaetze = []
    summe_ausgehend = 0.0
    
    # Dictionary für Empfänger-Summen
    empfaenger_summen = {}
    
    # Verarbeite die erste gefundene CSV-Datei
    with open(csv_files[0], 'r', encoding='utf-8-sig') as csvfile:
        # Lese die Datei mit Semikolon als Trennzeichen
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        
        # Überspringe Header-Zeilen
        for i in range(4):
            header_row = next(reader)
            with open(debug_file, 'a', encoding='utf-8') as debug:
                debug.write(f"Überspringe Header-Zeile {i+1}: {header_row}\n")
        
        # Lese Header-Zeile für die Spaltennamen
        header = next(reader)
        with open(debug_file, 'a', encoding='utf-8') as debug:
            debug.write(f"Spalten-Header: {header}\n\n")
        
        # Identifiziere die Indizes der benötigten Spalten
        try:
            betrag_idx = header.index("Betrag (€)")
            empfaenger_idx = header.index("Zahlungsempfänger*in")
            verwendungszweck_idx = header.index("Verwendungszweck")
            umsatztyp_idx = header.index("Umsatztyp")
            
            with open(debug_file, 'a', encoding='utf-8') as debug:
                debug.write(f"Indizes: Betrag={betrag_idx}, Empfänger={empfaenger_idx}, Verwendungszweck={verwendungszweck_idx}, Umsatztyp={umsatztyp_idx}\n\n")
                debug.write("VERARBEITUNG DER TRANSAKTIONEN\n")
                debug.write("=============================\n\n")
        except ValueError as e:
            print(f"Fehler: Erforderliche Spalte nicht gefunden - {e}")
            return
        
        # Verarbeite die Transaktionen
        zeilennummer = 0
        for row in reader:
            zeilennummer += 1
            
            if len(row) <= 1:  # Überspringe leere Zeilen
                with open(debug_file, 'a', encoding='utf-8') as debug:
                    debug.write(f"Zeile {zeilennummer}: Leere Zeile übersprungen\n")
                continue
            
            # Debug-Ausgabe für jede Zeile
            with open(debug_file, 'a', encoding='utf-8') as debug:
                debug.write(f"Zeile {zeilennummer}: {row}\n")
                
            if len(row) > betrag_idx:
                # Debug: Prüfe den Umsatztyp
                with open(debug_file, 'a', encoding='utf-8') as debug:
                    debug.write(f"  Umsatztyp: '{row[umsatztyp_idx]}'\n")
                
                # Nur ausgehende Umsätze verarbeiten
                if row[umsatztyp_idx] == "Ausgang":
                    empfaenger = row[empfaenger_idx]
                    
                    # Prüfe, ob der Empfänger auf der Blocklist steht
                    if empfaenger in blocklist:
                        with open(debug_file, 'a', encoding='utf-8') as debug:
                            debug.write(f"  Empfänger '{empfaenger}' steht auf der Blocklist - übersprungen\n\n")
                        
                        # Speichere blockierten Umsatz für Debug-Zwecke
                        betrag = betrag_to_float(row[betrag_idx])
                        blockierte_umsaetze.append({
                            'empfaenger': empfaenger,
                            'verwendungszweck': row[verwendungszweck_idx],
                            'betrag': abs(betrag)
                        })
                        continue
                    
                    original_betrag_str = row[betrag_idx]
                    betrag = betrag_to_float(original_betrag_str)
                    betrag_abs = abs(betrag)
                    
                    # Debug-Ausgabe für Beträge
                    with open(debug_file, 'a', encoding='utf-8') as debug:
                        debug.write(f"  Original Betrag String: '{original_betrag_str}'\n")
                        debug.write(f"  Konvertierter Betrag (float): {betrag}\n")
                        debug.write(f"  Absolutwert: {betrag_abs}\n")
                        debug.write(f"  Summe vor Addition: {summe_ausgehend}\n")
                    
                    # Berechnung der Summe - EINFACH DEN ABSOLUTWERT ADDIEREN
                    summe_ausgehend += betrag_abs
                    
                    # Erfasse den Betrag pro Empfänger
                    if empfaenger in empfaenger_summen:
                        empfaenger_summen[empfaenger] += betrag_abs
                    else:
                        empfaenger_summen[empfaenger] = betrag_abs
                    
                    # Debug nach der Addition
                    with open(debug_file, 'a', encoding='utf-8') as debug:
                        debug.write(f"  Summe nach Addition: {summe_ausgehend}\n")
                        debug.write(f"  Empfänger: {empfaenger}\n")
                        debug.write(f"  Verwendungszweck: {row[verwendungszweck_idx]}\n\n")
                    
                    # Speichere die Transaktion
                    ausgehende_umsaetze.append({
                        'empfaenger': empfaenger,
                        'verwendungszweck': row[verwendungszweck_idx],
                        'betrag': betrag_abs
                    })
                else:
                    with open(debug_file, 'a', encoding='utf-8') as debug:
                        debug.write(f"  Kein Ausgang - übersprungen\n\n")
            else:
                with open(debug_file, 'a', encoding='utf-8') as debug:
                    debug.write(f"  Zeile hat zu wenige Spalten - übersprungen\n\n")
    
    # Berechne die Hälfte der Gesamtsumme
    summe_geteilt = summe_ausgehend / 2
    
    # Debug-Ausgabe vor der Ausgabedatei
    with open(debug_file, 'a', encoding='utf-8') as debug:
        debug.write("\nZUSAMMENFASSUNG\n")
        debug.write("==============\n")
        debug.write(f"Anzahl ausgehender Umsätze: {len(ausgehende_umsaetze)}\n")
        debug.write(f"Anzahl blockierter Umsätze: {len(blockierte_umsaetze)}\n")
        debug.write(f"Gesamtsumme ausgehender Umsätze: {summe_ausgehend} € (unformatiert)\n")
        debug.write(f"Gesamtsumme formatiert: {format_euro(summe_ausgehend)}\n")
        debug.write(f"Hälfte der Summe: {format_euro(summe_geteilt)}\n\n")
        
        debug.write("EMPFÄNGER-SUMMEN\n")
        for empfaenger, betrag in empfaenger_summen.items():
            debug.write(f"  {empfaenger}: {format_euro(betrag)}\n")
        debug.write("\n")
        
        debug.write("DETAILLIERTE AUFLISTUNG ALLER AUSGEHENDEN UMSÄTZE\n")
        for idx, umsatz in enumerate(ausgehende_umsaetze, 1):
            debug.write(f"Umsatz #{idx}:\n")
            debug.write(f"  Empfänger: {umsatz['empfaenger']}\n")
            debug.write(f"  Verwendungszweck: {umsatz['verwendungszweck']}\n")
            debug.write(f"  Betrag: {format_euro(umsatz['betrag'])}\n\n")
        
        if blockierte_umsaetze:
            debug.write("BLOCKIERTE UMSÄTZE (NICHT IN DER SUMME ENTHALTEN)\n")
            for idx, umsatz in enumerate(blockierte_umsaetze, 1):
                debug.write(f"Blockierter Umsatz #{idx}:\n")
                debug.write(f"  Empfänger: {umsatz['empfaenger']}\n")
                debug.write(f"  Verwendungszweck: {umsatz['verwendungszweck']}\n")
                debug.write(f"  Betrag: {format_euro(umsatz['betrag'])}\n\n")
    
    # Schreibe die Berichte
    data = {
        'ausgehende_umsaetze': ausgehende_umsaetze,
        'blockierte_umsaetze': blockierte_umsaetze,
        'summe_ausgehend': summe_ausgehend,
        'summe_geteilt': summe_geteilt,
        'empfaenger_summen': empfaenger_summen
    }
    
    write_reports(data, output_file, summary_file)
    
    print(f"Auswertung wurde in die Datei '{output_file}' geschrieben.")
    print(f"Empfänger-Übersicht wurde in die Datei '{summary_file}' geschrieben.")
    print(f"Debug-Informationen wurden in '{debug_file}' geschrieben.")

if __name__ == "__main__":
    main()