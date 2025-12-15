from __future__ import annotations

from dataclasses import dataclass

from app.application.ports.marketplaces import MarketplacePortFactory
from app.domain.inventory import InventoryKey, InventorySnapshot
from app.domain.marketplace import (
    ListingQuantityUpdate,
    MarketplaceConfig,
    MarketplacePolicy,
)


@dataclass
class SyncInventoryService:
    """Application service that orchestrates inventory synchronization."""

    marketplace_factory: MarketplacePortFactory
    config: MarketplaceConfig
    policy: MarketplacePolicy

    async def sync(
        self,
        inventory: InventorySnapshot,
    ) -> list[ListingQuantityUpdate]:
        """
        Synchronizes warehouse inventory to marketplace.

        Returns a list of updates that were sent to the marketplace.
        """

        marketplace = self.marketplace_factory.build(self.config)

        listings = await marketplace.fetch_listings()

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
            await marketplace.update_inventory(updates=updates)

        return updates
