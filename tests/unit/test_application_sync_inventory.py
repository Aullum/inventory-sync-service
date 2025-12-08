from collections.abc import Sequence

import pytest

from app.application.dto.inventory import InventorySnapshotDTO, ItemIventoryDTO
from app.application.ports.marketplaces import MarketplaceInventoryPort
from app.application.service.sync_inventory import SyncInventoryService
from app.domain.inventory import InventoryItem, InventoryKey


class FakeMarketplace(MarketplaceInventoryPort):
    """
    Fake implementation of MarketplaceInventoryPort
    for unit testing purposes.
    """

    def __init__(self) -> None:
        self.received_items: list[InventoryItem] | None = None
        self.call_count: int = 0

    async def sync_inventory(self, items: Sequence[InventoryItem]) -> None:
        self.call_count += 1
        self.received_items = list(items)


def make_snapshot_dto() -> InventorySnapshotDTO:
    return InventorySnapshotDTO(
        source="test_source",
        items=[
            ItemIventoryDTO(product_id="SKU1", condition="NE", quantity=5),
            ItemIventoryDTO(product_id="SKU1", condition="NE", quantity=3),
            ItemIventoryDTO(product_id="SKU2", condition="UE", quantity=2),
            ItemIventoryDTO(product_id="SKU3", condition="NE", quantity=10),
        ],
    )


@pytest.mark.asyncio
async def test_sync_aggregates_and_calls_marketplace() -> None:
    service = SyncInventoryService()
    marketplace = FakeMarketplace()
    snapshot = make_snapshot_dto()

    await service.sync(marketplace=marketplace, snapshot=snapshot)

    assert marketplace.call_count == 1
    assert marketplace.received_items is not None

    items = marketplace.received_items

    assert len(items) == 3

    by_key: dict[InventoryKey, InventoryItem] = {item.key: item for item in items}

    assert by_key[InventoryKey(product_id="SKU1", condition="NE")].quantity == 8
    assert by_key[InventoryKey(product_id="SKU2", condition="UE")].quantity == 2
    assert by_key[InventoryKey(product_id="SKU3", condition="NE")].quantity == 10


@pytest.mark.asyncio
async def test_sync_does_not_call_marketplace_on_empty_snapshot() -> None:
    service = SyncInventoryService()
    marketplace = FakeMarketplace()
    snapshot = InventorySnapshotDTO(source="test_source", items=[])

    await service.sync(snapshot=snapshot, marketplace=marketplace)

    assert marketplace.call_count == 0
    assert marketplace.received_items is None
