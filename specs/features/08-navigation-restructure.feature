Feature: Phase 8 — Navigation restructuring
  As a user running a monthly settlement
  I want to reach the preview screen in one step from the main menu
  So that I am not stopped by an intermediate screen with only two options

  Background:
    Given the main menu is shown

  # --- T8.1  Two direct settlement entries instead of one + mode-select ---

  Scenario: Main menu has six entries in two logical groups
    Then the menu contains exactly 6 items
    And the first group contains:
      | Bank-Abrechnung    |
      | Ausgaben-Abrechnung|
      | Ausgaben erfassen  |
    And the second group contains:
      | Einrichtung   |
      | Systemprüfung |
      | Einstellungen |

  Scenario: Selecting Bank-Abrechnung goes directly to the preview screen
    When I select "Bank-Abrechnung"
    Then the preview screen for mode "bank" is shown immediately
    And no intermediate mode-selection screen appears

  Scenario: Selecting Ausgaben-Abrechnung goes directly to the preview screen
    When I select "Ausgaben-Abrechnung"
    Then the preview screen for mode "paper" is shown immediately
    And no intermediate mode-selection screen appears

  # --- T8.2  Back navigation depth fixed ---

  Scenario: Zurück from result screen lands on main menu
    Given the result screen is shown after a successful settlement
    When I press "Zurueck" or Escape
    Then the main menu is shown
    And no intermediate screens remain on the stack

  Scenario: Zurück from preview screen lands on main menu
    Given the preview screen is shown
    When I press "Abbrechen" or Escape
    Then the main menu is shown

  # --- T8.3  Visual divider between workflow and admin sections ---

  Scenario: A visual separator is rendered between the two menu groups
    Then a divider is visible between "Ausgaben erfassen" and "Einrichtung"
