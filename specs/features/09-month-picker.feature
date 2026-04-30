Feature: Phase 9 — Month picker for paper settlement
  As a user who has entered expenses for multiple months
  I want to choose which month to settle when starting an Ausgaben-Abrechnung
  So that I am not forced to always settle the latest file

  Background:
    Given the main menu is shown
    And at least one paper CSV exists in "input/paper"

  # --- T9.1  list_paper_inputs API ---

  Scenario: list_paper_inputs returns available files newest first
    Given "input/paper" contains "25-11.csv", "25-12.csv", "26-01.csv"
    Then list_paper_inputs returns them ordered newest first
    And each entry is an absolute Path

  Scenario: list_paper_inputs returns empty list when folder is empty
    Given "input/paper" contains no CSV files
    Then list_paper_inputs returns an empty list

  # --- T9.2  preview_paper and run_paper_settlement accept explicit file ---

  Scenario: preview_paper uses the provided file instead of latest
    Given "input/paper" contains "25-11.csv" and "26-03.csv"
    When preview_paper is called with input_file pointing to "25-11.csv"
    Then the preview reflects "25-11.csv", not "26-03.csv"

  Scenario: run_paper_settlement settles the provided file instead of latest
    Given "input/paper" contains "25-11.csv" and "26-03.csv"
    When run_paper_settlement is called with input_file pointing to "25-11.csv"
    Then the output report is written for year 2025 month 11

  # --- T9.3  Month picker TUI screen (paper only) ---

  Scenario: Selecting Ausgaben-Abrechnung shows a month picker when multiple files exist
    When I select "Ausgaben-Abrechnung"
    Then a month picker screen is shown listing all available paper CSVs
    And the files are shown newest first
    And each entry shows the filename and its modification date

  Scenario: Selecting Ausgaben-Abrechnung skips the picker when only one file exists
    Given "input/paper" contains exactly one CSV file
    When I select "Ausgaben-Abrechnung"
    Then the preview screen is shown directly without a picker

  Scenario: Selecting Ausgaben-Abrechnung with no input shows the preview with an error
    Given "input/paper" contains no CSV files
    When I select "Ausgaben-Abrechnung"
    Then the preview screen is shown with status ERROR and "Starten" disabled

  Scenario: User picks a specific month and proceeds to preview
    Given the month picker is shown with "25-11.csv" and "26-01.csv"
    When I select "25-11.csv"
    Then the preview screen shows that file as the input

  Scenario: Pressing Escape on the month picker returns to the main menu
    Given the month picker is shown
    When I press Escape
    Then the main menu is shown

  # --- T9.4  Back navigation consistency ---

  Scenario: Zurück from result lands on main menu regardless of whether picker was shown
    Given a paper settlement has completed via the month picker
    When I press "Zurueck"
    Then the main menu is shown
    And no intermediate screens remain on the stack
