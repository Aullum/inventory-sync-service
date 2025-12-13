from __future__ import annotations

from dataclasses import dataclass

from app.application.ports.marketplaces import MarketplacePort
from app.domain.inventory import InventoryKey, InventorySnapshot
from app.domain.marketplace import ListingQuantityUpdate, MarketplacePolicy


@dataclass
class SyncInventoryService:
    """Application service that orchestrates inventory synchronization."""

    marketplace_port: MarketplacePort
    policy: MarketplacePolicy

    async def sync(
        self,
        inventory: InventorySnapshot,
    ) -> list[ListingQuantityUpdate]:
        """
        Synchronizes warehouse inventory to marketplace.

        Returns a list of updates that were sent to the marketplace.
        """

        listings = await self.marketplace_port.fetch_listings()

        updates: list[ListingQuantityUpdate] = []

        for listing in listings:
            key = InventoryKey(condition_id=listing.condition_id)
            warehouse_qty = inventory.get_qty(key)

            if not self.policy.should_sync(
                listing=listing,
                warehouse_qty=warehouse_qty,
            ):
                continue

            target_qty = self.policy.calc_target_qty(warehouse_qty=warehouse_qty)

            updates.append(
                ListingQuantityUpdate(
                    sku=listing.sku,
                    listing_id=listing.listing_id,
                    qty=target_qty,
                )
            )

        if updates:
            await self.marketplace_port.update_inventory(updates=updates)

        return updates
