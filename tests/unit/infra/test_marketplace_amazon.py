import pytest

from app.infrastructure.marketplaces.amazon_client import AmazonUserCredentials


class TestInfraAmazonCredentials:
    @staticmethod
    @pytest.mark.parametrize(
        "field,value",
        [
            ("seller_partner_id", ""),
            ("lwa_client_id", ""),
            ("lwa_client_secret", ""),
            ("refresh_token", ""),
        ],
    )
    def test_amazon_credentials_empty_fields_raise(field, value):
        kwargs = {
            "seller_partner_id": "x",
            "lwa_client_id": "x",
            "lwa_client_secret": "x",
            "refresh_token": "x",
        }
        kwargs[field] = value

        with pytest.raises(ValueError):
            AmazonUserCredentials(**kwargs)

    @staticmethod
    def test_amazon_credentials_ok():
        creds = AmazonUserCredentials(
            seller_partner_id="seller",
            lwa_client_id="client",
            lwa_client_secret="secret",
            refresh_token="refresh",
        )
        assert creds.seller_partner_id == "seller"
