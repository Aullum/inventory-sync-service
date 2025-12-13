from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from app.domain.marketplace import Listing, ListingQuantityUpdate


class MarketplacePort(Protocol):
    """Port for interacting with a single marketplace account."""

    async def fetch_listings(self) -> list[Listing]:
        """Returns current marketplace listings snapshot."""
        ...

    async def update_inventory(
        self,
        updates: Iterable[ListingQuantityUpdate],
    ) -> None:
        """Applies quantity updates for marketplace listings."""
        ...
