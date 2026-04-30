Feature: UX Phase A — language consistency, menu descriptions, prominent result
  As a user of the TUI
  I want a consistent German interface with clear labels and an obvious settlement result
  So that I can understand the app at a glance without guessing

  Background:
    Given the main menu is shown

  # --- T7.1  Consistent German labels ---

  Scenario: All main menu items use German labels
    Then the menu contains the item "Neue Abrechnung"
    And the menu contains the item "Ausgaben erfassen"
    And the menu contains the item "Einrichtung"
    And the menu contains the item "Systemprüfung"
    And the menu contains the item "Einstellungen"
    And the menu does not contain any item labelled "Initial Setup"
    And the menu does not contain any item labelled "Sanity Check"
    And the menu does not contain any item labelled "Configuration"
    And the menu does not contain any item labelled "Paper Erfassung"

  Scenario: Mode select screen uses German labels
    When I select "Neue Abrechnung"
    Then the mode selection screen shows "Bank-Abrechnung"
    And the mode selection screen shows "Ausgaben-Abrechnung"
    And neither option is labelled "Bank" alone or "Paper"

  # --- T7.2  Menu item subtitles ---

  Scenario: Each menu item shows a one-line description
    Then the item "Neue Abrechnung"   has subtitle "Monatsabrechnung aus Kontoauszug oder manuellen Ausgaben starten"
    And the item "Ausgaben erfassen"  has subtitle "Manuelle Ausgaben für einen Monat eingeben und speichern"
    And the item "Einrichtung"        has subtitle "Verzeichnisse und Beispielkonfigurationen anlegen"
    And the item "Systemprüfung"      has subtitle "Konfiguration und Eingabedateien auf Vollständigkeit prüfen"
    And the item "Einstellungen"      has subtitle "Aktuelle Konfigurationsdateien und Filterlisten anzeigen"

  # --- T7.3  Prominent settlement summary ---

  Scenario: Bank result screen shows the per-person amount prominently
    Given a bank settlement has just run successfully
    Then a summary line above the detail table shows "Pro Person: <amount>"
    And the summary line is visually distinct from the table rows

  Scenario: Paper result screen with reimbursement shows the payment direction prominently
    Given a paper settlement has just run successfully
    And person A owes person M money
    Then a summary line above the detail table shows "A zahlt an M: <amount>"
    And the summary line is visually distinct from the table rows

  Scenario: Paper result screen with no reimbursement says so prominently
    Given a paper settlement has just run successfully
    And both persons spent the same amount
    Then a summary line above the detail table shows "Ausgeglichen"
