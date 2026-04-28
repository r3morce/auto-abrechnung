Feature: Sanity check
  As a user about to run a settlement
  I want to verify that configs and inputs are present and valid
  So that I do not start a run that will fail mid-way

  Background:
    Given the main menu is shown

  Scenario: All good
    Given all required configs exist and are parseable
    And both "input/bank" and "input/paper" contain at least one CSV
    And every CSV is readable with the configured delimiter and encoding
    When I select "Sanity Check"
    Then every check item is shown with status "ok"
    And the overall status is "ok"

  Scenario: Missing config file
    Given "config_bank.yaml" does not exist
    When I select "Sanity Check"
    Then the item "config_bank.yaml" is shown with status "error"
         and reason "file not found"
    And the overall status is "error"

  Scenario: Unparseable YAML
    Given "config/allowlist.yaml" exists but contains invalid YAML
    When I select "Sanity Check"
    Then the item "config/allowlist.yaml" is shown with status "error"
         and a reason mentioning the parse problem
    And the overall status is "error"

  Scenario: No input files
    Given "input/bank" exists but contains no CSV files
    When I select "Sanity Check"
    Then the item "input/bank" is shown with status "warning"
         and reason "no CSV files found"
    And the overall status is "warning" if no other errors are present

  Scenario: Unreadable CSV
    Given "input/paper" contains a CSV that cannot be decoded with the
          configured encoding
    When I select "Sanity Check"
    Then the item for that file is shown with status "error"
         and a reason mentioning the encoding problem
    And the overall status is "error"

  Scenario: Re-running after fixing a problem
    Given the previous sanity check ended with status "error"
    And the user fixed the underlying issue
    When I select "Sanity Check" again
    Then the previously failing item is now shown with status "ok"
