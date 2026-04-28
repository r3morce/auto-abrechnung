Feature: Configuration overview
  As a user about to run a settlement
  I want to inspect the current configuration values
  So that I can verify paths and settings without opening editor and YAML files

  Background:
    Given the main menu is shown

  Scenario: Show parsed config values
    Given all four config files exist and are parseable
    When I select "Configuration"
    Then a screen lists every config file as a section
    And for each file every top-level key is shown with its value
    And list values (e.g. "valid_persons") are rendered as comma-separated text
    And paths "input_folder" and "output_folder" are shown for both bank and paper

  Scenario: Missing config file
    Given "config_paper.yaml" does not exist
    When I select "Configuration"
    Then "config_paper.yaml" is shown with status "missing"
    And the other config files are still rendered with their values

  Scenario: Unparseable config file
    Given "config/allowlist.yaml" exists but contains invalid YAML
    When I select "Configuration"
    Then "config/allowlist.yaml" is shown with status "error"
         and a reason mentioning the parse problem
    And the other config files are still rendered with their values

  Scenario: Empty list values
    Given "config/allowlist.yaml" parses to an empty "income_senders" list
    When I select "Configuration"
    Then the entry for "income_senders" is shown with value "(leer)"
