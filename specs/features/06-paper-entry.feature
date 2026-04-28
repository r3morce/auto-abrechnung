Feature: Manual paper-expense entry
  As a user adding paper expenses over the course of a month
  I want to enter expenses directly in the TUI
  So that I do not have to edit CSV files by hand

  Background:
    Given the main menu is shown

  Scenario: Open editor with today's month preselected
    When I select "Paper Erfassung"
    Then the editor screen opens
    And the year input shows the current year (4-digit)
    And the month input shows the current month (1-12)
    And the rows table is empty if no CSV exists for that year and month

  Scenario: Existing month is loaded automatically
    Given a file "input/paper/25-11.csv" exists with two valid rows
    When I open the editor and set year to 2025 and month to 11
    Then the rows table shows both existing rows
    And the source file path is shown somewhere on the screen

  Scenario: Add a new row
    Given the editor is open with an empty table
    And valid_persons is "a, b, m"
    When I enter person "a", amount "12,50", comment "Apotheke"
    And I press "Hinzufuegen"
    Then a new row appears in the table with those values
    And the input fields are cleared

  Scenario: Reject invalid row
    Given the editor is open
    When I enter person "x" (not in valid_persons)
    And I press "Hinzufuegen"
    Then no row is added
    And an inline error message is shown

  Scenario: Reject negative amount
    Given the editor is open
    When I enter person "a", amount "-5,00"
    And I press "Hinzufuegen"
    Then no row is added
    And an inline error message about the amount is shown

  Scenario: Delete a row
    Given the editor has at least one row
    And the cursor is on that row
    When I press "Entfernen"
    Then the row is removed from the table

  Scenario: Save overwrites the file with a backup
    Given the editor has 3 rows for year 2026, month 4
    And "input/paper/26-04.csv" already exists with different content
    When I press "Speichern"
    Then "input/paper/26-04.csv.bak" contains the previous content
    And "input/paper/26-04.csv" contains exactly the 3 rows from the table
    And a confirmation message is shown

  Scenario: Save creates a new file when none existed
    Given the editor has 2 rows for year 2026, month 5
    And no "input/paper/26-05.csv" exists
    When I press "Speichern"
    Then "input/paper/26-05.csv" is created with the 2 rows
    And no .bak file is created

  Scenario: Save and run settlement
    Given the editor has at least one valid row
    When I press "Speichern & Abrechnen"
    Then the CSV is written
    And the wizard result screen for "paper" is shown with the totals

  Scenario: Cancel without saving
    Given the editor has unsaved changes
    When I press Escape
    Then I am returned to the main menu
    And the file on disk is unchanged
