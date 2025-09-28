import pytest
import tempfile
import os
import shutil
import yaml

from config.settings import Settings


class TestSettings:
    @pytest.fixture
    def temp_config_dir(self):
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_settings_initialization_defaults(self):
        settings = Settings()
        # Just test that it initializes without error
        assert hasattr(settings, "income_allow_list")
        assert hasattr(settings, "expense_block_list")
        assert hasattr(settings, "config_directory")

    def test_default_allowlist(self):
        settings = Settings()
        default_allowlist = settings._get_default_allowlist()
        assert default_allowlist == []

    def test_default_blocklist(self):
        settings = Settings()
        default_blocklist = settings._get_default_blocklist()
        assert default_blocklist == []

    def test_config_directory_path(self):
        settings = Settings()
        assert settings.config_directory == "config"

    def test_load_allowlist_with_missing_file(self, temp_config_dir):
        settings = Settings()
        # Directly test the method with our temp directory
        settings.config_directory = temp_config_dir
        allowlist = settings._load_allowlist()

        # Should return default empty list when file doesn't exist
        assert allowlist == []

    def test_load_blocklist_with_missing_file(self, temp_config_dir):
        settings = Settings()
        settings.config_directory = temp_config_dir
        blocklist = settings._load_blocklist()

        # Should return default empty list when file doesn't exist
        assert blocklist == []

    def test_load_allowlist_with_valid_file(self, temp_config_dir, test_allowlist_config):
        # Create allowlist.yaml file
        allowlist_path = os.path.join(temp_config_dir, "allowlist.yaml")
        with open(allowlist_path, "w", encoding="utf-8") as f:
            yaml.dump(test_allowlist_config, f)

        settings = Settings()
        settings.config_directory = temp_config_dir
        allowlist = settings._load_allowlist()

        expected_senders = test_allowlist_config["income_senders"]
        assert allowlist == expected_senders
        assert "Arbeitgeber GmbH" in allowlist
        assert "Krankenkasse" in allowlist
        assert "Steueramt" in allowlist

    def test_load_blocklist_with_valid_file(self, temp_config_dir, test_blocklist_config):
        # Create blocklist.yaml file
        blocklist_path = os.path.join(temp_config_dir, "blocklist.yaml")
        with open(blocklist_path, "w", encoding="utf-8") as f:
            yaml.dump(test_blocklist_config, f)

        settings = Settings()
        settings.config_directory = temp_config_dir
        blocklist = settings._load_blocklist()

        expected_recipients = test_blocklist_config["expense_recipients"]
        assert blocklist == expected_recipients
        assert "Bank Gebühren" in blocklist
        assert "Hausverwaltung" in blocklist
        assert "Stadtwerke" in blocklist

    def test_load_allowlist_with_invalid_yaml(self, temp_config_dir):
        # Create invalid YAML file
        allowlist_path = os.path.join(temp_config_dir, "allowlist.yaml")
        with open(allowlist_path, "w", encoding="utf-8") as f:
            f.write("invalid: yaml: content: [")  # Invalid YAML

        settings = Settings()
        settings.config_directory = temp_config_dir
        allowlist = settings._load_allowlist()

        # Should fall back to default empty list
        assert allowlist == []

    def test_load_allowlist_with_missing_key(self, temp_config_dir):
        # Create YAML file without expected keys
        allowlist_path = os.path.join(temp_config_dir, "allowlist.yaml")
        with open(allowlist_path, "w", encoding="utf-8") as f:
            yaml.dump({"wrong_key": ["value1", "value2"]}, f)

        settings = Settings()
        settings.config_directory = temp_config_dir
        allowlist = settings._load_allowlist()

        # Should return empty list when key is missing
        assert allowlist == []

    def test_load_allowlist_with_empty_file(self, temp_config_dir):
        # Create empty YAML file
        allowlist_path = os.path.join(temp_config_dir, "allowlist.yaml")
        with open(allowlist_path, "w", encoding="utf-8") as f:
            f.write("")  # Empty file

        settings = Settings()
        settings.config_directory = temp_config_dir
        allowlist = settings._load_allowlist()

        # Should handle None result from yaml.safe_load
        assert allowlist == []