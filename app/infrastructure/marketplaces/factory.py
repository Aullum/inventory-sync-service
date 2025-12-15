from dataclasses import dataclass

import httpx

from app.application.ports.marketplaces import MarketplacePort
from app.domain.marketplace import MarketplaceConfig
from app.infrastructure.config import AppConfig
from app.infrastructure.marketplaces.amazon_client import (
    AmazonAdapter,
    AmazonUserCredentials,
)
from app.infrastructure.marketplaces.ebay_client import EbayAdapter, EbayUserCredentials


@dataclass(slots=True)
class MarketplaceAdapterFactory:
    http: httpx.AsyncClient
    app_config: AppConfig

    def build(self, config: MarketplaceConfig) -> MarketplacePort:
        market = config.marketplace

        match market:
            case "ebay":
                ebay_creds = EbayUserCredentials(token=config.refresh_token)
                return EbayAdapter(
                    http=self.http,
                    credentials=ebay_creds,
                    dev_creds=self.app_config.ebay_dev_creds,
                    base_url=self.app_config.ebay_base_url,
                )
            case "amazon":
                amazon_creds = AmazonUserCredentials(
                    seller_partner_id=config.seller_id or "",
                    lwa_client_id=config.client_id or "",
                    lwa_client_secret=config.client_secret or "",
                    refresh_token=config.refresh_token,
                )
                return AmazonAdapter(
                    http=self.http,
                    credentials=amazon_creds,
                    base_url=self.app_config.amazon_base_url,
                )

        raise ValueError(f"Unsupported marketplace: {config.marketplace}")
