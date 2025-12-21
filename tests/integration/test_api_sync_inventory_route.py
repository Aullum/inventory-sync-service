import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

import app.api.routes.inventory as inventory_route_module
from app.api.routes.inventory import router as inventory_router
from app.domain.inventory import InventoryKey
from app.domain.marketplace import ListingQuantityUpdate


class FakeService:
    def __init__(self):
        self.seen_inventory = None

    async def sync(self, inventory):
        self.seen_inventory = inventory

        return [
            ListingQuantityUpdate(sku="SKU-1", listing_id="L1", qty=10),
            ListingQuantityUpdate(sku="SKU-2", listing_id="L2", qty=0),
        ]


@pytest.mark.asyncio
async def test_sync_inventory_route_maps_inventory_and_returns_updates(monkeypatch):
    app = FastAPI()
    app.include_router(inventory_router)

    fake_service = FakeService()

    def fake_build_sync_service(*, request, marketplace, body):
        return fake_service

    monkeypatch.setattr(
        inventory_route_module,
        "build_sync_service",
        fake_build_sync_service,
    )

    payload = {
        "account": "acc-1",
        "refresh_token": "user-token",
        "seller_id": None,
        "client_id": None,
        "client_secret": None,
        "limit_qty_for_sync_in_marketplace": 100,
        "limit_qty_for_sync_in_warehouse": 100,
        "limit_qty_difference_for_sync": 0,
        "limit_qty_for_marketplace": 50,
        "inventory": [
            {"condition_id": "NEW", "quantity": 10},
            {"condition_id": "USED", "quantity": 3},
        ],
    }

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/v1/marketplaces/ebay/inventory/sync",
            json=payload,
        )

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "updates": [
            {"sku": "SKU-1", "listing_id": "L1", "qty": 10},
            {"sku": "SKU-2", "listing_id": "L2", "qty": 0},
        ]
    }

    inv = fake_service.seen_inventory
    assert inv is not None

    assert inv.get_qty(InventoryKey(condition_id="NEW")) == 10
    assert inv.get_qty(InventoryKey(condition_id="USED")) == 3
