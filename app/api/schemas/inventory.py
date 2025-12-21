from __future__ import annotations

from pydantic import BaseModel


class InventoryItemIn(BaseModel):
    condition_id: str
    quantity: int


class SyncInventoryRequest(BaseModel):
    account: str
    refresh_token: str

    # amazon-only
    seller_id: str | None = None
    client_id: str | None = None
    client_secret: str | None = None

    # policy limits
    limit_qty_for_sync_in_marketplace: int = 9999
    limit_qty_for_sync_in_warehouse: int = 9999
    limit_qty_difference_for_sync: int = 0
    limit_qty_for_marketplace: int = 9999

    inventory: list[InventoryItemIn]


class ListingQuantityUpdateOut(BaseModel):
    sku: str
    listing_id: str | None = None
    qty: int


class SyncInventoryResponse(BaseModel):
    updates: list[ListingQuantityUpdateOut]
