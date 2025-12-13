from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MarketplaceConfig:
    """Immutable configuration and sync policy limits for a marketplace account."""

    marketplace: str
    account: str
    refresh_token: str
    seller_id: str | None = None
    client_id: str | None = None
    client_secret: str | None = None

    # Sync policy thresholds (qty caps and min-diff to trigger sync)
    limit_qty_for_sync_in_marketplace: int = 9999
    limit_qty_for_sync_in_warehouse: int = 9999
    limit_qty_difference_for_sync: int = 0
    limit_qty_for_marketplace: int = 9999

    def __post_init__(self) -> None:
        if len(self.marketplace) == 0:
            raise ValueError("marketplace must not be empty")

        if len(self.account) == 0:
            raise ValueError("account must not be empty")

        if len(self.refresh_token) == 0:
            raise ValueError("refresh_token must not be empty")

        if self.limit_qty_for_sync_in_marketplace < 0:
            raise ValueError("limit_qty_for_sync_in_marketplace must be >= 0")

        if self.limit_qty_for_sync_in_warehouse < 0:
            raise ValueError("limit_qty_for_sync_in_warehouse must be >= 0")

        if self.limit_qty_difference_for_sync < 0:
            raise ValueError("limit_qty_difference_for_sync must be >= 0")

        if self.limit_qty_for_marketplace < 0:
            raise ValueError("limit_qty_for_marketplace must be >= 0")


@dataclass(frozen=True, slots=True)
class Listing:
    """Immutable representation of a marketplace listing used for sync decisions."""

    sku: str
    condition_id: str
    marketplace_qty: int
    listing_id: str | None = None
    price: float | None = None

    def __post_init__(self) -> None:
        if len(self.sku) == 0:
            raise ValueError("sku must not be empty")

        if len(self.condition_id) == 0:
            raise ValueError("condition_id must not be empty")

        if self.marketplace_qty < 0:
            raise ValueError("marketplace_qty must be >= 0")


@dataclass(frozen=True, slots=True)
class ListingQuantityUpdate:
    """Command to update a listing quantity on the marketplace."""

    sku: str
    qty: int
    listing_id: str | None = None


@dataclass
class MarketplacePolicy:
    """
    Domain service responsible for evaluating sync decisions
    and calculating target quantities.
    """

    config: MarketplaceConfig

    def should_sync(self, listing: Listing, warehouse_qty: int) -> bool:
        """
        Determines whether a listing should be synchronized.

        A synchronization is skipped if:
        - warehouse quantity is negative,
        - quantities exceed configured thresholds,
        - the difference between warehouse and marketplace quantities
          is below the configured minimum (including exact equality).
        """

        if listing.marketplace_qty > self.config.limit_qty_for_sync_in_marketplace:
            return False

        if warehouse_qty > self.config.limit_qty_for_sync_in_warehouse:
            return False

        if listing.marketplace_qty == warehouse_qty:
            return False

        diff = abs(warehouse_qty - listing.marketplace_qty)
        if diff < self.config.limit_qty_difference_for_sync:
            return False

        return True

    def calc_target_qty(self, warehouse_qty: int) -> int:
        """
        Calculates final quantity to be pushed to marketplace
        after applying marketplace limits.
        """
        if warehouse_qty > self.config.limit_qty_for_marketplace:
            return self.config.limit_qty_for_marketplace

        return warehouse_qty
