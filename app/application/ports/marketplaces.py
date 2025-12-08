from collections.abc import Iterable
from typing import Protocol

from app.domain.inventory import InventoryItem


class MarketplaceInventoryPort(Protocol):
    """
    Abstraction over inventory updates on the marketplace.
    The application layer only knows about this interface, and the implementation resides in the infrastructure.
    """

    async def sync_inventory(self, items: Iterable[InventoryItem]) -> None:
        """
        Applies the passed InventoryItem set on the marketplace side.
        It is assumed that the items are already aggregated by InventoryKey.
        """
