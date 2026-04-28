Feature: Guided new settlement (wizard)
  As a user starting a new monthly settlement
  I want a guided flow that shows me input, config, result, and where it is saved
  So that I can run a settlement without leaving the TUI

  Background:
    Given the main menu is shown

  Scenario: Choose mode
    When I select "Neue Abrechnung"
    Then a mode selection screen is shown
    And it lists at least the modes "Bank" and "Paper"

  Scenario: Bank preview shows config and input
    Given a valid bank CSV exists in "input/bank"
    And "config_bank.yaml" is parseable
    When I select "Neue Abrechnung" and choose "Bank"
    Then a preview screen shows:
      | section            | content                                   |
      | Konfiguration      | input_folder, output_folder, csv_delimiter |
      | Eingabedatei       | filename, modification time, size         |
      | Vorschau           | first up to 10 CSV rows                   |
      | Filterregeln       | allowlist count, blocklist count          |
    And the screen offers a "Starten" and a "Abbrechen" action

  Scenario: Paper preview shows config and input
    Given a valid paper CSV exists in "input/paper"
    And "config_paper.yaml" is parseable
    When I select "Neue Abrechnung" and choose "Paper"
    Then a preview screen shows:
      | section            | content                                   |
      | Konfiguration      | input_folder, output_folder, valid_persons |
      | Eingabedatei       | filename, modification time, size         |
      | Vorschau           | first up to 10 CSV rows                   |
    And the screen offers a "Starten" and a "Abbrechen" action

  Scenario: Cancel from preview
    Given the preview screen is shown
    When I press "Abbrechen" or Escape
    Then I am returned to the main menu
    And no files were written

  Scenario: Run bank settlement and show result
    Given the preview screen for "Bank" is shown
    When I press "Starten"
    Then a loading indicator appears while the settlement runs
    And afterwards a result screen shows:
      | section            | content                                |
      | Beträge            | Gesamtausgaben, Gesamteinnahmen,       |
      |                    | Nettoausgaben, Pro Person              |
      | Ausgabedateien     | absolute paths to TXT and CSV          |
    And the result screen offers an "Ordner oeffnen" action
    And the action launches `xdg-open` on the output folder
    And the result screen offers a "Zurueck" action

  Scenario: Run paper settlement and show result
    Given the preview screen for "Paper" is shown
    When I press "Starten"
    Then a loading indicator appears while the settlement runs
    And afterwards a result screen shows:
      | section            | content                                |
      | Beträge            | Person-A, Person-M, Gesamt, Pro Person |
      | Ausgleichszahlung  | payer, recipient, amount or "keine"    |
      | Ausgabedateien     | absolute paths to TXT and CSV          |
    And the result screen offers an "Ordner oeffnen" action
    And the result screen offers a "Zurueck" action

  Scenario: Input file missing
    Given "input/bank" contains no CSV files
    When I select "Neue Abrechnung" and choose "Bank"
    Then the preview screen shows the section "Eingabedatei" with status
         "FEHLT" and a reason
    And the "Starten" action is disabled

  Scenario: Settlement raises an error
    Given the preview screen for "Bank" is shown
    And reading the CSV will fail (e.g. malformed file)
    When I press "Starten"
    Then the result screen shows status "FEHLER" with the error reason
    And no further actions besides "Zurueck" are offered
