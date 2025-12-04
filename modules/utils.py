import os
import glob
import yaml


def find_latest_file(folder: str, pattern: str = "*.csv") -> str:
    """Find the most recently created file matching the pattern in the folder.

    Args:
        folder: Directory to search in
        pattern: Glob pattern for file matching (default: "*.csv")

    Returns:
        Path to the most recent file

    Raises:
        FileNotFoundError: If no files matching pattern are found
    """
    file_pattern = os.path.join(folder, pattern)
    files = glob.glob(file_pattern)

    if not files:
        raise FileNotFoundError(
            f"Keine Dateien mit Muster '{pattern}' im Ordner {folder} gefunden"
        )

    latest_file = max(files, key=os.path.getctime)
    return latest_file


def read_config(file_path: str) -> dict:
    """Read and parse a YAML configuration file.

    Args:
        file_path: Path to the YAML configuration file

    Returns:
        Dictionary containing the configuration

    Raises:
        FileNotFoundError: If the configuration file doesn't exist
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Konfigurationsdatei {file_path} nicht gefunden.\\n"
            f"Erstelle die Datei mit den erforderlichen Einstellungen."
        )

    with open(file_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config


def create_directories(*paths: str) -> None:
    """Create multiple directories if they don't exist.

    Args:
        *paths: Variable number of directory paths to create
    """
    for path in paths:
        os.makedirs(path, exist_ok=True)


def format_currency(amount: float, decimal_places: int = 2) -> str:
    """Format amount as German currency string with comma as decimal separator.

    Args:
        amount: The amount to format
        decimal_places: Number of decimal places (default: 2)

    Returns:
        Formatted currency string (e.g., "123,45")
    """
    formatted = f"{amount:.{decimal_places}f}"
    # Replace dot with comma for German formatting
    formatted = formatted.replace(".", ",")
    return formatted
