# Inventory Sync Service

Async service that pushes warehouse stock levels to marketplace listings (Amazon, eBay), built on FastAPI with a
hexagonal (ports and adapters) architecture.

> **Status:** architecture skeleton. The domain model, sync policy, orchestration and API are implemented and covered
> by tests. The Amazon and eBay adapters are stubs: they return no listings and send no updates.

## How a sync works

1. `POST /v1/marketplaces/{marketplace}/inventory/sync` receives the account credentials, the policy limits and the
   warehouse inventory keyed by `condition_id`.
2. The marketplace adapter fetches the account's current listings.
3. `MarketplacePolicy` decides for each listing whether it needs an update and calculates the target quantity.
4. The adapter sends all updates in one call, and the response lists them.

The policy:

- skips a listing whose marketplace quantity exceeds `limit_qty_for_sync_in_marketplace`, or whose warehouse quantity
  exceeds `limit_qty_for_sync_in_warehouse`;
- skips a listing whose quantities are equal or differ by less than `limit_qty_difference_for_sync`;
- caps the quantity sent to the marketplace at `limit_qty_for_marketplace`;
- treats a condition missing from the inventory as zero stock.

## Architecture

```
app/
  domain/          InventorySnapshot, Listing, MarketplaceConfig, MarketplacePolicy (no framework imports)
  application/     SyncInventoryService and the MarketplacePort / MarketplacePortFactory protocols
  infrastructure/  Amazon and eBay adapters, the adapter factory, the shared httpx client, env config
  api/             FastAPI router, request and response schemas, service wiring
main.py            app lifespan: config, shared httpx client, adapter factory
```

The application layer depends only on the ports, and the adapters satisfy them structurally (`typing.Protocol`).
A new marketplace is a new adapter registered in `MarketplaceAdapterFactory`.

## Example request

```bash
curl -X POST http://127.0.0.1:8000/v1/marketplaces/ebay/inventory/sync \
  -H 'Content-Type: application/json' \
  -d '{
        "account": "demo",
        "refresh_token": "<token>",
        "limit_qty_difference_for_sync": 2,
        "inventory": [{"condition_id": "1000", "quantity": 5}]
      }'
```

The response lists the updates sent: `{"updates": [{"sku": "...", "listing_id": "...", "qty": 5}]}`. With the
current stub adapters it is `{"updates": []}`. Amazon also needs `seller_id`, `client_id` and `client_secret`.

## Running locally

Requires Python 3.12 and Poetry.

```bash
poetry install
export EBAY_CLIENT_ID=<client id> EBAY_CLIENT_SECRET=<client secret>
poetry run uvicorn main:app --reload
```

OpenAPI docs are served at http://127.0.0.1:8000/docs.

## Tests and quality

```bash
poetry run pytest --cov=app
poetry run ruff check . && poetry run ruff format --check .
poetry run mypy app
```

CI runs ruff, the ruff format check, mypy and the tests on every branch push, and the tests with coverage plus
`poetry check` on every pull request to `main`. pre-commit runs the basic hygiene hooks and ruff.

## License

MIT
