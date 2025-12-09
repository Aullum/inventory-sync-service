import pytest

from app.domain.inventory import InventoryItem, InventoryKey


def test_inventory_key_is_valid() -> None:
    key = InventoryKey(condition_id="UEG2050")

    assert key.condition_id == "UEG2050"


def test_inventory_key_invalid_empty_condition_id() -> None:
    with pytest.raises(ValueError):
        InventoryKey(condition_id="")


def test_inventory_item_valid_direct_init() -> None:
    key = InventoryKey(condition_id="UEG2050")
    item = InventoryItem(_key=key, _quantity=10)

    assert item.condition_id == "UEG2050"
    assert item.quantity == 10


def test_inventory_item_invalid_negative_quantity() -> None:
    key = InventoryKey(condition_id="UEG2050")

    with pytest.raises(ValueError):
        InventoryItem(_key=key, _quantity=-1)


def test_inventory_item_create_factory() -> None:
    item = InventoryItem.create(condition_id="UEG2050", quantity=10)

    assert item.condition_id == "UEG2050"
    assert item.quantity == 10


def test_inventory_item_increase_valid() -> None:
    item = InventoryItem.create(condition_id="UEG2050", quantity=10)

    item.increase(5)

    assert item.quantity == 15


def test_inventory_item_increase_negative_amount_raises() -> None:
    item = InventoryItem.create(condition_id="UEG2050", quantity=10)

    with pytest.raises(ValueError):
        item.increase(-5)
