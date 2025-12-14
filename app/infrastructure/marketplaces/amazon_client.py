from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import httpx

from app.domain.marketplace import Listing, ListingQuantityUpdate


class AmazonMapper:
    @staticmethod
    def map_listings(payload) -> list[Listing]:
        return []


@dataclass(slots=True, frozen=True)
class AmazonCredentials:
    seller_partner_id: str
    lwa_client_id: str
    lwa_client_secret: str
    refresh_token: str

    def __post_init__(self) -> None:
        if not self.seller_partner_id:
            raise ValueError("seller_partner_id must not be empty")

        if not self.lwa_client_id:
            raise ValueError("lwa_client_id must not be empty")

        if not self.lwa_client_secret:
            raise ValueError("lwa_client_secret must not be empty")

        if not self.refresh_token:
            raise ValueError("refresh_token must not be empty")


@dataclass(slots=True)
class AmazonAdapter:
    """
    Infrastructure adapter for Amazon marketplace.
    Implements MarketplacePort via structural typing.
    """

    http: httpx.AsyncClient
    credentials: AmazonCredentials
    mapper: AmazonMapper

    async def fetch_listings(self) -> list[Listing]:
        """
        Returns current marketplace listings snapshot.

        Stub implementation.
        """

        return []

    async def update_inventory(
        self,
        updates: Iterable[ListingQuantityUpdate],
    ) -> None:
        """
        Applies quantity updates for marketplace listings.

        Stub implementation.
        """

        return None
