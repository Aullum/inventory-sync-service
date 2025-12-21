from fastapi import FastAPI
from starlette.requests import Request

from app.api.deps import build_sync_service
from app.api.schemas.inventory import InventoryItemIn, SyncInventoryRequest


def _make_request_with_factory(factory_obj: object) -> Request:
    app = FastAPI()
    app.state.marketplace_factory = factory_obj

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "method": "POST",
        "path": "/",
        "headers": [],
        "app": app,
    }
    return Request(scope)


def test_build_sync_service_wires_policy_config_and_factory():
    factory = object()
    request = _make_request_with_factory(factory)

    body = SyncInventoryRequest(
        account="acc-1",
        refresh_token="token-1",
        seller_id="seller",
        client_id="client",
        client_secret="secret",
        limit_qty_for_sync_in_marketplace=100,
        limit_qty_for_sync_in_warehouse=200,
        limit_qty_difference_for_sync=0,
        limit_qty_for_marketplace=50,
        inventory=[InventoryItemIn(condition_id="NEW", quantity=10)],
    )

    service = build_sync_service(
        request=request,
        marketplace="EBAY",
        body=body,
    )

    assert service.marketplace_factory is factory

    assert service.config.marketplace == "ebay"
    assert service.config.account == "acc-1"
    assert service.config.refresh_token == "token-1"
    assert service.config.seller_id == "seller"
    assert service.config.client_id == "client"
    assert service.config.client_secret == "secret"
    assert service.config.limit_qty_for_marketplace == 50

    assert service.policy.config is service.config
