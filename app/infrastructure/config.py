import os
from dataclasses import dataclass


def _get_str(name: str) -> str:
    value = os.getenv(name, "")

    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


@dataclass(frozen=True, slots=True)
class EbayDeveloperCredentials:
    """
    Static (process-level) credentials for eBay developer account.
    Names depend on the auth flow you use
    """

    client_id: str
    client_secret: str

    def __post_init__(self):
        if not self.client_id:
            raise ValueError("EBAY_CLIENT_ID must not be empty")
        if not self.client_secret:
            raise ValueError("EBAY_CLIENT_SECRET must not be empty")


@dataclass(frozen=True, slots=True)
class AppConfig:
    ebay_dev_creds: EbayDeveloperCredentials
    ebay_base_url: str
    amazon_base_url: str

    def __post_init__(self):
        if not self.ebay_base_url:
            raise ValueError("ebay_base_url must not be empty")
        if not self.amazon_base_url:
            raise ValueError("amazon_base_url must not be empty")


def load_config(
    ebay_base_url: str = "https://api.ebay.com",
    amazon_base_url: str = "https://sellingpartnerapi-na.amazon.com",
) -> AppConfig:
    ebay_dev_creds = EbayDeveloperCredentials(
        client_id=_get_str("EBAY_CLIENT_ID"),
        client_secret=_get_str("EBAY_CLIENT_SECRET"),
    )

    return AppConfig(
        ebay_dev_creds=ebay_dev_creds,
        ebay_base_url=ebay_base_url,
        amazon_base_url=amazon_base_url,
    )
