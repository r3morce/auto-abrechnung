Feature: Phase 11 — Calculation preview before saving
  As a user running a settlement
  I want to see the calculated result before any files are written
  So that I can verify the numbers and decide whether to save

  Background:
    Given the preview screen for a mode is shown and "Starten" is pressed

  # --- T11.1  Headless calculation API ---

  Scenario: calculate_bank returns totals without writing files
    Given a valid bank CSV and config exist
    When calculate_bank is called
    Then a BankCalculation with totals and amount_per_person is returned
    And no files are written to the output folder

  Scenario: calculate_paper returns totals without writing files
    Given a valid paper CSV and config exist
    When calculate_paper is called
    Then a PaperCalculation with person totals and reimbursement info is returned
    And no files are written to the output folder

  Scenario: calculate_paper accepts an explicit input_file
    Given two paper CSVs exist
    When calculate_paper is called with the older file explicitly
    Then the result reflects that file, not the latest one

  # --- T11.2  CalculationScreen TUI ---

  Scenario: Pressing Starten opens the calculation screen with a loading indicator
    When "Starten" is pressed on the preview screen
    Then a calculation screen is shown with a loading indicator
    And the "Speichern" button is disabled while loading

  Scenario: Calculation screen shows the summary prominently after loading
    Given the calculation has completed successfully
    Then the summary line shows the key result (e.g. "Pro Person: 234,50 €")
    And the detail table shows all individual amounts
    And the "Speichern" button becomes enabled
    And the "Abbrechen" button is visible

  Scenario: Calculation screen shows an error if calculation fails
    Given the input CSV is malformed
    Then the calculation screen shows an error message
    And the "Speichern" button remains disabled

  # --- T11.3  Save step ---

  Scenario: Pressing Speichern writes files and updates the screen
    Given the calculation screen shows a successful result
    When I press "Speichern"
    Then a loading indicator appears while files are written
    And afterwards the screen shows the output file paths
    And an "Ordner öffnen" action becomes available
    And "Abbrechen" is replaced by "Schließen"

  Scenario: Pressing Abbrechen before saving returns to the main menu
    Given the calculation screen shows a successful result
    And "Speichern" has not been pressed
    When I press "Abbrechen" or Escape
    Then the main menu is shown
    And no files have been written

  Scenario: Pressing Abbrechen after saving is not possible
    Given "Speichern" has already been pressed
    Then Escape and "Abbrechen" do nothing (files are already written)
