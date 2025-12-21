from fastapi import Request

from app.api.schemas.inventory import SyncInventoryRequest
from app.application.service.sync_inventory import SyncInventoryService
from app.domain.marketplace import MarketplaceConfig, MarketplacePolicy


def build_sync_service(
    request: Request,
    marketplace: str,
    body: SyncInventoryRequest,
) -> SyncInventoryService:
    cfg = MarketplaceConfig(
        marketplace=marketplace.lower().strip(),
        account=body.account,
        refresh_token=body.refresh_token,
        seller_id=body.seller_id,
        client_id=body.client_id,
        client_secret=body.client_secret,
        limit_qty_for_sync_in_marketplace=body.limit_qty_for_sync_in_marketplace,
        limit_qty_for_sync_in_warehouse=body.limit_qty_for_sync_in_warehouse,
        limit_qty_difference_for_sync=body.limit_qty_difference_for_sync,
        limit_qty_for_marketplace=body.limit_qty_for_marketplace,
    )

    policy = MarketplacePolicy(config=cfg)

    factory = request.app.state.marketplace_factory

    return SyncInventoryService(
        policy=policy,
        config=cfg,
        marketplace_factory=factory,
    )
