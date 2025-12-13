from __future__ import annotations

from collections.abc import Iterable

import pytest

from app.application.ports.marketplaces import MarketplacePort
from app.application.service.sync_inventory import SyncInventoryService
from app.domain.inventory import InventoryItem, InventoryKey, InventorySnapshot
from app.domain.marketplace import (
    Listing,
    ListingQuantityUpdate,
    MarketplaceConfig,
    MarketplacePolicy,
)


class FakeMarketplacePort(MarketplacePort):
    """In-memory fake implementation of MarketplacePort for testing."""

    listings: list[Listing]
    updates: list[ListingQuantityUpdate]

    def __init__(self, listings: list[Listing]) -> None:
        self._listings = listings
        self.updates: list[ListingQuantityUpdate] = []

    async def fetch_listings(self) -> list[Listing]:
        return self._listings

    async def update_inventory(self, updates: Iterable[ListingQuantityUpdate]) -> None:
        self.updates.extend(updates)


class TestSyncInventoryService:
    @staticmethod
    def _make_policy() -> MarketplacePolicy:
        config = MarketplaceConfig(
            marketplace="Ebay",
            account="Test_Acc",
            refresh_token="Token",
            limit_qty_for_sync_in_marketplace=100,
            limit_qty_for_sync_in_warehouse=100,
            limit_qty_difference_for_sync=0,
            limit_qty_for_marketplace=50,
        )

        return MarketplacePolicy(config=config)

    @staticmethod
    def _make_inventory_for_condition_id(
        condition_id: str,
        quantity: int,
    ) -> InventorySnapshot:
        key = InventoryKey(condition_id=condition_id)
        item = InventoryItem.create(condition_id=condition_id, quantity=quantity)

        return InventorySnapshot.from_items({key: item})

    @pytest.mark.asyncio
    async def test_no_listings_produces_no_updates(self) -> None:
        inventory = self._make_inventory_for_condition_id("UEG2000", 10)
        port = FakeMarketplacePort(listings=[])
        service = SyncInventoryService(
            marketplace_port=port,
            policy=self._make_policy(),
        )

        updates = await service.sync(inventory=inventory)

        assert updates == []
        assert port.updates == []

    @pytest.mark.asyncio
    async def test_no_update_when_target_qty_equals_marketplace_qty(self) -> None:
        inventory = self._make_inventory_for_condition_id("NEW", 10)
        listing = Listing(
            sku="SKU-1",
            condition_id="NEW",
            marketplace_qty=10,
            listing_id="L1",
        )
        port = FakeMarketplacePort(listings=[listing])
        service = SyncInventoryService(
            marketplace_port=port,
            policy=self._make_policy(),
        )

        updates = await service.sync(inventory)

        assert updates == []
        assert port.updates == []

    @pytest.mark.asyncio
    async def test_update_is_generated_when_diff_exists(self) -> None:
        inventory = self._make_inventory_for_condition_id("NEW", 20)
        listing = Listing(
            sku="SKU-1",
            condition_id="NEW",
            marketplace_qty=5,
            listing_id="L1",
        )
        port = FakeMarketplacePort(listings=[listing])
        service = SyncInventoryService(
            marketplace_port=port,
            policy=self._make_policy(),
        )

        updates = await service.sync(inventory)

        assert len(updates) == 1
        update = updates[0]

        assert update.listing_id == "L1"
        assert update.qty == 20

        # ensure port got the same updates
        assert port.updates == updates

    @pytest.mark.asyncio
    async def test_target_qty_is_capped_by_marketplace_limit(self) -> None:
        inventory = self._make_inventory_for_condition_id("NEW", 80)
        listing = Listing(
            sku="SKU-1",
            condition_id="NEW",
            marketplace_qty=0,
            listing_id="L1",
        )
        port = FakeMarketplacePort(listings=[listing])
        policy = self._make_policy()
        service = SyncInventoryService(
            marketplace_port=port,
            policy=policy,
        )

        updates = await service.sync(inventory)

        assert len(updates) == 1
        assert updates[0].qty == policy.config.limit_qty_for_marketplace
