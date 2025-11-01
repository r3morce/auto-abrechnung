# Auto-Abrechnung Project

This is a Python tool for automatically splitting monthly expenses between two people based on bank statements.

## Project Structure

- `main.py` - Entry point that orchestrates the settlement calculation
- `modules/` - Core business logic modules
  - `csv_reader.py` - Reads and parses bank statement CSV files
  - `transaction_filter.py` - Filters transactions based on allowlist/blocklist
  - `settlement_calculator.py` - Calculates 50/50 settlement amounts
  - `report_generator.py` - Generates text reports
  - `csv_exporter.py` - Exports data for Excel import
- `config/` - Configuration management
  - `settings.py` - Settings class that loads YAML configs
  - `allowlist.yaml` - Income sources to include (user-created)
  - `blocklist.yaml` - Expense recipients to exclude (user-created)
- `input/` - Bank statement CSV files (not versioned)
- `output/` - Generated reports and exports (not versioned)

## Development Commands

Use `make` for development tasks:
- `make setup` - Complete project setup
- `make run` - Execute the settlement calculation
- `make test` - Run tests with pytest
- `make lint` - Code quality check with flake8
- `make format` - Format code with black
- `make clean` - Clean temporary files

## Code Style

- Use Black for code formatting (line length: 100)
- Use flake8 for linting
- Follow PEP 8 conventions
- Use type hints where possible
- German language for user-facing messages and comments

## Testing

- Uses pytest for testing
- Test files should be in `tests/` directory
- Focus on edge cases in transaction parsing and filtering

## Dependencies

- PyYAML for configuration file parsing
- Standard library modules: csv, datetime, decimal, os, sys, glob

## Key Patterns

- Transaction class represents individual financial transactions
- Settings class loads and manages configuration
- Modular design with clear separation of concerns
- Error handling with user-friendly German messages
- Decimal for precise monetary calculations