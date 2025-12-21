from fastapi import APIRouter, Request

from app.api.deps import build_sync_service
from app.api.schemas.inventory import (
    ListingQuantityUpdateOut,
    SyncInventoryRequest,
    SyncInventoryResponse,
)
from app.domain.inventory import InventoryItem, InventoryKey, InventorySnapshot

router = APIRouter(prefix="/v1/marketplaces", tags=["inventory"])


def to_domain_snapshot(body: SyncInventoryRequest) -> InventorySnapshot:
    items = {}
    for i in body.inventory:
        key = InventoryKey(condition_id=i.condition_id)
        item = InventoryItem.create(condition_id=i.condition_id, quantity=i.quantity)
        items[key] = item
    return InventorySnapshot.from_items(items)


@router.post("/{marketplace}/inventory/sync", response_model=SyncInventoryResponse)
async def sync_inventory(
    marketplace: str,
    body: SyncInventoryRequest,
    request: Request,
) -> SyncInventoryResponse:
    service = build_sync_service(request=request, marketplace=marketplace, body=body)
    inventory = to_domain_snapshot(body)

    updates = await service.sync(inventory=inventory)

    return SyncInventoryResponse(
        updates=[
            ListingQuantityUpdateOut(sku=u.sku, listing_id=u.listing_id, qty=u.qty)
            for u in updates
        ]
    )
