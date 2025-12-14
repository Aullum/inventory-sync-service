from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import httpx

from app.domain.marketplace import Listing, ListingQuantityUpdate


class EbayMapper:
    @staticmethod
    def map_listings(payload) -> list[Listing]:
        return []


@dataclass(frozen=True, slots=True)
class EbayConfig:
    token: str

    def __post_init__(self) -> None:
        if not self.token:
            raise ValueError("token must not be empty")


@dataclass(slots=True)
class EbayAdapter:
    """
    Infrastructure adapter for Ebay marketplace.
    Implements MarketplacePort via structural typing.
    """

    http: httpx.AsyncClient
    credentials: EbayConfig
    mapper: EbayMapper

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
