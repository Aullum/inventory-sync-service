from collections.abc import Callable

import pytest

from app.domain.marketplace import (
    Listing,
    ListingQuantityUpdate,
    MarketplaceConfig,
    MarketplacePolicy,
)


class TestMarketplaceConfig:
    @staticmethod
    def test_valid_config_created() -> None:
        config = MarketplaceConfig(
            marketplace="Ebay",
            account="Test_Acc",
            refresh_token="Token",
            client_id="client_id",
            client_secret="client_secret",
            seller_id="seller_id",
        )

        assert config.marketplace == "Ebay"
        assert config.account == "Test_Acc"
        assert config.refresh_token == "Token"
        assert config.client_id == "client_id"
        assert config.client_secret == "client_secret"
        assert config.seller_id == "seller_id"
        assert config.limit_qty_for_sync_in_marketplace == 9999
        assert config.limit_qty_for_sync_in_warehouse == 9999
        assert config.limit_qty_difference_for_sync == 0
        assert config.limit_qty_for_marketplace == 9999

    @pytest.mark.parametrize(
        "marketplace, account, refresh_token",
        [
            ("", "acc", "token"),
            ("market", "", "token"),
            ("market", "acc", ""),
        ],
    )
    @staticmethod
    def test_empty_required_strings_raise_value_error(
        marketplace: str,
        account: str,
        refresh_token: str,
    ) -> None:
        with pytest.raises(ValueError):
            MarketplaceConfig(
                marketplace=marketplace,
                account=account,
                refresh_token=refresh_token,
            )

    @pytest.mark.parametrize(
        "factory",
        [
            lambda: MarketplaceConfig(
                marketplace="market",
                account="acc",
                refresh_token="token",
                limit_qty_for_sync_in_marketplace=-1,
            ),
            lambda: MarketplaceConfig(
                marketplace="market",
                account="acc",
                refresh_token="token",
                limit_qty_for_sync_in_warehouse=-1,
            ),
            lambda: MarketplaceConfig(
                marketplace="market",
                account="acc",
                refresh_token="token",
                limit_qty_difference_for_sync=-1,
            ),
            lambda: MarketplaceConfig(
                marketplace="market",
                account="acc",
                refresh_token="token",
                limit_qty_for_marketplace=-1,
            ),
        ],
    )
    def test_negative_limits_raise_value_error(
        self,
        factory: Callable[[], MarketplaceConfig],
    ) -> None:
        with pytest.raises(ValueError):
            factory()


class TestListing:
    @staticmethod
    def test_valid_listing_created() -> None:
        listing = Listing(
            sku="SKU-1",
            condition_id="NEW",
            marketplace_qty=10,
            listing_id="123",
            price=9.99,
        )

        assert listing.sku == "SKU-1"
        assert listing.condition_id == "NEW"
        assert listing.marketplace_qty == 10
        assert listing.listing_id == "123"
        assert listing.price == 9.99

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"sku": "", "condition_id": "NEW", "marketplace_qty": 1},
            {"sku": "SKU-1", "condition_id": "", "marketplace_qty": 1},
        ],
    )
    @staticmethod
    def test_empty_required_fields_raise_value_error(kwargs: dict) -> None:
        with pytest.raises(ValueError):
            Listing(**kwargs)

    @staticmethod
    def test_negative_marketplace_qty_raises_value_error() -> None:
        with pytest.raises(ValueError):
            Listing(
                sku="sku",
                condition_id="condition_id",
                marketplace_qty=-1,
            )


class TestListingQuantityUpdate:
    @staticmethod
    def test_listing_quantity_update_created() -> None:
        update = ListingQuantityUpdate(
            sku="sku",
            listing_id="listing_id",
            qty=15,
        )

        assert update.sku == "sku"
        assert update.listing_id == "listing_id"
        assert update.qty == 15


class TestMarketplacePolicy:
    @staticmethod
    def _make_policy(
        marketplace: str = "Ebay",
        account: str = "Test_Acc",
        refresh_token: str = "Token",
        limit_qty_for_sync_in_marketplace: int = 100,
        limit_qty_for_sync_in_warehouse: int = 100,
        limit_qty_difference_for_sync: int = 1,
        limit_qty_for_marketplace: int = 50,
    ) -> MarketplacePolicy:
        config = MarketplaceConfig(
            marketplace=marketplace,
            account=account,
            refresh_token=refresh_token,
            limit_qty_for_sync_in_marketplace=limit_qty_for_sync_in_marketplace,
            limit_qty_for_sync_in_warehouse=limit_qty_for_sync_in_warehouse,
            limit_qty_difference_for_sync=limit_qty_difference_for_sync,
            limit_qty_for_marketplace=limit_qty_for_marketplace,
        )
        return MarketplacePolicy(config=config)

    def test_should_sync_false_when_warehouse_qty_negative(self) -> None:
        policy = self._make_policy()
        listing = Listing(
            sku="sku",
            condition_id="listing_id",
            marketplace_qty=10,
        )

        assert policy.should_sync(listing=listing, warehouse_qty=-1) is False

    @pytest.mark.parametrize(
        "warehouse_qty,limit_warehouse,expected",
        [
            (100, 100, True),
            (101, 100, False),
        ],
    )
    def test_warehouse_limit_is_applied(
        self,
        warehouse_qty: int,
        limit_warehouse: int,
        expected: bool,
    ) -> None:
        policy = self._make_policy(limit_qty_for_sync_in_warehouse=limit_warehouse)
        listing = Listing(
            sku="SKU-1",
            condition_id="NEW",
            marketplace_qty=10,
        )

        assert policy.should_sync(listing, warehouse_qty=warehouse_qty) is expected

    @pytest.mark.parametrize(
        "marketplace_qty,limit_marketplace,expected",
        [
            (100, 100, True),
            (101, 100, False),
        ],
    )
    def test_marketplace_limit_is_applied(
        self,
        marketplace_qty: int,
        limit_marketplace: int,
        expected: bool,
    ) -> None:
        policy = self._make_policy(
            limit_qty_for_sync_in_marketplace=limit_marketplace,
        )
        listing = Listing(
            sku="SKU-1",
            condition_id="NEW",
            marketplace_qty=marketplace_qty,
        )

        assert policy.should_sync(listing, warehouse_qty=10) is expected

    @pytest.mark.parametrize(
        "threshold,warehouse_qty,expected",
        [
            (5, 13, False),
            (5, 15, True),
            (0, 11, True),
        ],
    )
    def test_difference_threshold_is_applied(
        self,
        threshold: int,
        warehouse_qty: int,
        expected: bool,
    ) -> None:
        policy = self._make_policy(limit_qty_difference_for_sync=threshold)
        listing = Listing(
            sku="SKU-1",
            condition_id="NEW",
            marketplace_qty=10,
        )

        assert policy.should_sync(listing, warehouse_qty=warehouse_qty) is expected

    @pytest.mark.parametrize(
        "warehouse_qty,limit_marketplace,expected",
        [
            (10, 50, 10),
            (100, 50, 50),
        ],
    )
    def test_calc_target_qty(
        self,
        warehouse_qty: int,
        limit_marketplace: int,
        expected: int,
    ) -> None:
        policy = self._make_policy(limit_qty_for_marketplace=limit_marketplace)

        assert policy.calc_target_qty(warehouse_qty=warehouse_qty) == expected
