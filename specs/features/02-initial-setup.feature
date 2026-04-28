Feature: Initial setup
  As a new user
  I want the TUI to create the required folder structure and example configs
  So that I can start without manually following the README

  Background:
    Given the main menu is shown

  Scenario: Setup in an empty project
    Given none of the required folders or config files exist
    When I select "Initial Setup"
    Then the folders "input/bank", "input/paper", "output/bank/archiv",
         "output/paper/archiv", "config" are created
    And example files "config_bank.yaml", "config_paper.yaml",
         "config/allowlist.yaml", "config/blocklist.yaml" are created
         from their example templates if available
    And every created item is shown in a result list with status "created"
    And the action ends with an overall status "ok"

  Scenario: Setup is idempotent
    Given all required folders and config files already exist
    When I select "Initial Setup"
    Then no file or folder is overwritten
    And every item is shown with status "skipped (already exists)"
    And the action ends with an overall status "ok"

  Scenario: Setup with partial state
    Given some folders exist but "config_paper.yaml" is missing
    When I select "Initial Setup"
    Then existing items are reported as "skipped"
    And missing items are reported as "created"
    And the action ends with an overall status "ok"

  Scenario: Setup fails on permission error
    Given the working directory is not writable
    When I select "Initial Setup"
    Then the failing item is shown with status "error" and a reason
    And the action ends with an overall status "error"
