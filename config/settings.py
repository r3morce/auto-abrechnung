import yaml
import os


class Settings:
    def __init__(self):
        self.config_directory = "config"
        self.income_allow_list = self._load_allowlist()
        self.expense_block_list = self._load_blocklist()

    def _load_allowlist(self):
        allowlist_file = os.path.join(self.config_directory, "allowlist.yaml")
        try:
            with open(allowlist_file, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                return data.get("income_senders", [])
        except FileNotFoundError:
            print(f"Warnung: {allowlist_file} nicht gefunden. Verwende Standard-Liste.")
            return self._get_default_allowlist()
        except yaml.YAMLError as error:
            print(f"Fehler beim Laden von {allowlist_file}: {error}")
            return self._get_default_allowlist()

    def _load_blocklist(self):
        blocklist_file = os.path.join(self.config_directory, "blocklist.yaml")
        try:
            with open(blocklist_file, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                return data.get("expense_recipients", [])
        except FileNotFoundError:
            print(f"Warnung: {blocklist_file} nicht gefunden. Verwende Standard-Liste.")
            return self._get_default_blocklist()
        except yaml.YAMLError as error:
            print(f"Fehler beim Laden von {blocklist_file}: {error}")
            return self._get_default_blocklist()

    def _get_default_allowlist(self):
        return []

    def _get_default_blocklist(self):
        return []
