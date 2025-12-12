import pytest

from app.domain.inventory import (
    InventoryItem,
    InventoryKey,
    InventorySnapshot,
)


class TestInventoryKey:
    def test_inventory_key_valid(self) -> None:
        key = InventoryKey(condition_id="NETestInventoryKey")
        assert key.condition_id == "NETestInventoryKey"

    def test_inventory_key_empty_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            InventoryKey(condition_id="")


class TestInventoryItem:
    def test_create_sets_key_and_quantity(self) -> None:
        item = InventoryItem.create(
            condition_id="UEtest_create_sets_key_and_quantity", quantity=10
        )

        assert isinstance(item.key, InventoryKey)
        assert item.key.condition_id == "UEtest_create_sets_key_and_quantity"
        assert item.condition_id == "UEtest_create_sets_key_and_quantity"
        assert item.quantity == 10

    def test_negative_quantity_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            InventoryItem.create(
                condition_id="UEtest_negative_quantity_raises_value_error", quantity=-1
            )

    def test_increase_with_positive_amount(self) -> None:
        item = InventoryItem.create(
            condition_id="UEtest_increase_with_positive_amount", quantity=5
        )

        item.increase(3)

        assert item.quantity == 8

    def test_increase_with_negative_amount_raises_value_error(self) -> None:
        item = InventoryItem.create(
            condition_id="UEtest_increase_with_negative_amount_raises_value_error",
            quantity=5,
        )

        with pytest.raises(ValueError):
            item.increase(-1)


class TestInventorySnapshot:
    def test_from_items_creates_snapshot_and_get_qty_returns_quantity(self) -> None:
        key = InventoryKey(
            condition_id="NEtest_from_items_creates_snapshot_and_get_qty_returns_quantity"
        )
        item = InventoryItem.create(
            condition_id="NEtest_from_items_creates_snapshot_and_get_qty_returns_quantity",
            quantity=15,
        )
        items = {key: item}

        snapshot = InventorySnapshot.from_items(items)

        assert snapshot.get_qty(key) == 15

    def test_get_qty_returns_none_for_missing_key(self) -> None:
        existing_key = InventoryKey(
            condition_id="NEtest_get_qty_returns_none_for_missing_key"
        )
        missing_key = InventoryKey(
            condition_id="UEtest_get_qty_returns_none_for_missing_key"
        )

        item = InventoryItem.create(
            condition_id="NEtest_get_qty_returns_none_for_missing_key", quantity=10
        )
        items = {existing_key: item}

        snapshot = InventorySnapshot.from_items(items)

        assert snapshot.get_qty(missing_key) == 0

    def test_snapshot_does_not_expose_internal_mapping_for_mutation(self) -> None:
        key1 = InventoryKey(
            condition_id="NEtest_snapshot_does_not_expose_internal_mapping_for_mutation"
        )
        key2 = InventoryKey(
            condition_id="UEtest_snapshot_does_not_expose_internal_mapping_for_mutation"
        )

        item1 = InventoryItem.create(
            condition_id="NEtest_snapshot_does_not_expose_internal_mapping_for_mutation",
            quantity=10,
        )

        items: dict[InventoryKey, InventoryItem] = {key1: item1}

        snapshot = InventorySnapshot.from_items(items)

        items[key2] = InventoryItem.create(
            condition_id="UEtest_snapshot_does_not_expose_internal_mapping_for_mutation",
            quantity=5,
        )

        assert snapshot.get_qty(key1) == 10
        assert snapshot.get_qty(key2) == 0

    def test_items_returns_items_view_and_is_iterable(self) -> None:
        key1 = InventoryKey(
            condition_id="NEtest_items_returns_items_view_and_is_iterable"
        )
        key2 = InventoryKey(
            condition_id="UEtest_items_returns_items_view_and_is_iterable"
        )

        item1 = InventoryItem.create(
            condition_id="NEtest_items_returns_items_view_and_is_iterable", quantity=10
        )
        item2 = InventoryItem.create(
            condition_id="UEtest_items_returns_items_view_and_is_iterable", quantity=5
        )

        items = {key1: item1, key2: item2}

        snapshot = InventorySnapshot.from_items(items)

        items_view = snapshot.items()

        assert len(list(items_view)) == 2

        collected = {k.condition_id: v.quantity for k, v in items_view}
        assert collected == {
            "NEtest_items_returns_items_view_and_is_iterable": 10,
            "UEtest_items_returns_items_view_and_is_iterable": 5,
        }
