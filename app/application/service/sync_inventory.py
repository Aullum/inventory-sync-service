# import for the ruff(PEP 585 collection)
from __future__ import annotations

from app.application.dto.inventory import InventorySnapshotDTO
from app.application.ports.marketplaces import MarketplaceInventoryPort
from app.domain.inventory import InventoryItem, InventoryKey


class SyncInventoryService:
    """
    A service for processing inventory snapshots.
    The decision on where to send them (which marketplace/account) is made externally.
    """

    async def sync(
        self,
        snapshot: InventorySnapshotDTO,
        marketplace: MarketplaceInventoryPort,
    ):
        """
        One call = one snapshot = one marketplace (one account).
        """

        items = self._aggregate_snapshot(snapshot=snapshot)

        if not items:
            return

        await marketplace.sync_inventory(items=items)

    def _aggregate_snapshot(
        self,
        snapshot: InventorySnapshotDTO,
    ) -> list[InventoryItem]:
        aggregated: dict[InventoryKey, InventoryItem] = {}

        for dto_item in snapshot.items:
            key = InventoryKey(
                product_id=dto_item.product_id,
                condition=dto_item.condition,
            )

            if key not in aggregated:
                aggregated[key] = InventoryItem(key=key, quantity=0)

            aggregated[key].increase(dto_item.quantity)

        return list(aggregated.values())
