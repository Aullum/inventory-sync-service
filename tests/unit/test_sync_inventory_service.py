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

    def __init__(self, listings: list[Listing]) -> None:
        self._listings = listings
        self.updates: list[ListingQuantityUpdate] = []

    async def fetch_listings(self) -> list[Listing]:
        return self._listings

    async def update_inventory(self, updates: Iterable[ListingQuantityUpdate]) -> None:
        self.updates.extend(list(updates))


class FakeMarketplacePortFactory:
    """In-memory fake implementation of MarketplacePortFactory for testing."""

    def __init__(self, port: MarketplacePort) -> None:
        self._port = port
        self.build_calls: int = 0
        self.last_config: MarketplaceConfig | None = None

    def build(self, config: MarketplaceConfig) -> MarketplacePort:
        self.build_calls += 1
        self.last_config = config
        return self._port


class TestSyncInventoryService:
    @staticmethod
    def _make_config() -> MarketplaceConfig:
        return MarketplaceConfig(
            marketplace="Ebay",
            account="Test_Acc",
            refresh_token="Token",
            limit_qty_for_sync_in_marketplace=100,
            limit_qty_for_sync_in_warehouse=100,
            limit_qty_difference_for_sync=0,
            limit_qty_for_marketplace=50,
        )

    @staticmethod
    def _make_policy(config: MarketplaceConfig) -> MarketplacePolicy:
        return MarketplacePolicy(config=config)

    @staticmethod
    def _make_inventory_for_condition_id(
        condition_id: str, quantity: int
    ) -> InventorySnapshot:
        key = InventoryKey(condition_id=condition_id)
        item = InventoryItem.create(condition_id=condition_id, quantity=quantity)
        return InventorySnapshot.from_items({key: item})

    @pytest.mark.asyncio
    async def test_no_listings_produces_no_updates(self) -> None:
        inventory = self._make_inventory_for_condition_id("UEG2000", 10)

        config = self._make_config()
        policy = self._make_policy(config)

        port = FakeMarketplacePort(listings=[])
        factory = FakeMarketplacePortFactory(port=port)

        service = SyncInventoryService(
            policy=policy,
            config=config,
            marketplace_factory=factory,
        )

        updates = await service.sync(inventory=inventory)

        assert updates == []
        assert port.updates == []
        assert factory.build_calls == 1
        assert factory.last_config == config

    @pytest.mark.asyncio
    async def test_no_update_when_target_qty_equals_marketplace_qty(self) -> None:
        inventory = self._make_inventory_for_condition_id("NEW", 10)

        listing = Listing(
            sku="SKU-1",
            condition_id="NEW",
            marketplace_qty=10,
            listing_id="L1",
        )

        config = self._make_config()
        policy = self._make_policy(config)

        port = FakeMarketplacePort(listings=[listing])
        factory = FakeMarketplacePortFactory(port=port)

        service = SyncInventoryService(
            policy=policy,
            config=config,
            marketplace_factory=factory,
        )

        updates = await service.sync(inventory)

        assert updates == []
        assert port.updates == []
        assert factory.build_calls == 1
        assert factory.last_config == config

    @pytest.mark.asyncio
    async def test_update_is_generated_when_diff_exists(self) -> None:
        inventory = self._make_inventory_for_condition_id("NEW", 20)

        listing = Listing(
            sku="SKU-1",
            condition_id="NEW",
            marketplace_qty=5,
            listing_id="L1",
        )

        config = self._make_config()
        policy = self._make_policy(config)

        port = FakeMarketplacePort(listings=[listing])
        factory = FakeMarketplacePortFactory(port=port)

        service = SyncInventoryService(
            policy=policy,
            config=config,
            marketplace_factory=factory,
        )

        updates = await service.sync(inventory)

        assert len(updates) == 1
        update = updates[0]

        assert update.listing_id == "L1"
        assert update.qty == 20

        assert port.updates == updates
        assert factory.build_calls == 1
        assert factory.last_config == config

    @pytest.mark.asyncio
    async def test_target_qty_is_capped_by_marketplace_limit(self) -> None:
        inventory = self._make_inventory_for_condition_id("NEW", 80)

        listing = Listing(
            sku="SKU-1",
            condition_id="NEW",
            marketplace_qty=0,
            listing_id="L1",
        )

        config = self._make_config()
        policy = self._make_policy(config)

        port = FakeMarketplacePort(listings=[listing])
        factory = FakeMarketplacePortFactory(port=port)

        service = SyncInventoryService(
            policy=policy,
            config=config,
            marketplace_factory=factory,
        )

        updates = await service.sync(inventory)

        assert len(updates) == 1
        assert updates[0].qty == policy.config.limit_qty_for_marketplace
        assert port.updates == updates
        assert factory.build_calls == 1
        assert factory.last_config == config
