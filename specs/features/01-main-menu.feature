Feature: Main menu
  As a user launching the TUI
  I want a clear entry screen
  So that I can pick an action without reading docs

  Scenario: Launching the TUI shows the main menu
    Given the TUI is not running
    When I run the launch command
    Then a main menu is shown
    And it lists at least the actions "Initial Setup" and "Sanity Check"
    And the focus is on the first action

  Scenario: Navigating with the keyboard
    Given the main menu is shown
    When I press the down arrow key
    Then the focus moves to the next action
    When I press Enter
    Then the focused action is started

  Scenario: Quitting the TUI
    Given the main menu is shown
    When I press "q"
    Then the TUI exits with status code 0
