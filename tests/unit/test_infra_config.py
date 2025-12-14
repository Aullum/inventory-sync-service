import pytest

from app.infrastructure.config import load_config


class TestInfraConfig:
    @staticmethod
    def test_load_config_missing_ebay_client_id(monkeypatch):
        monkeypatch.delenv("EBAY_CLIENT_ID", raising=False)
        monkeypatch.setenv("EBAY_CLIENT_SECRET", "secret")

        with pytest.raises(ValueError):
            load_config()

    @staticmethod
    def test_load_config_missing_ebay_client_secret(monkeypatch):
        monkeypatch.setenv("EBAY_CLIENT_ID", "id")
        monkeypatch.delenv("EBAY_CLIENT_SECRET", raising=False)

        with pytest.raises(ValueError):
            load_config()

    @staticmethod
    def test_load_config_happy_path(monkeypatch):
        monkeypatch.setenv("EBAY_CLIENT_ID", "id")
        monkeypatch.setenv("EBAY_CLIENT_SECRET", "secret")

        cfg = load_config(
            ebay_base_url="ebay_base_url", amazon_base_url="amazon_base_url"
        )

        assert cfg.ebay_dev_creds.client_id == "id"
        assert cfg.ebay_dev_creds.client_secret == "secret"
        assert cfg.ebay_base_url == "ebay_base_url"
        assert cfg.amazon_base_url == "amazon_base_url"
