import pytest

from app.domain.inventory import InventoryItem, InventoryKey


def test_inventory_key_is_valid() -> None:
    key = InventoryKey(product_id="test_inventory_key_is_valid", condition="UE")

    assert key.product_id == "test_inventory_key_is_valid"
    assert key.condition == "UE"


def test_inventory_key_invalid_empty_product_id() -> None:
    with pytest.raises(ValueError):
        InventoryKey(product_id="", condition="NE")


def test_inventory_item_valid() -> None:
    key = InventoryKey(product_id="test_inventory_item_valid", condition="NE")
    item = InventoryItem(key=key, quantity=10)

    assert item.product_id == "test_inventory_item_valid"
    assert item.condition == "NE"
    assert item.quantity == 10


def test_inventory_item_invalid_negative_quantity() -> None:
    key = InventoryKey(
        product_id="test_inventory_item_invalid_negative_quantity", condition="WE"
    )

    with pytest.raises(ValueError):
        InventoryItem(key=key, quantity=-1)


def test_inventory_item_increase_valid() -> None:
    key = InventoryKey(product_id="test_inventory_item_increase_valid", condition="NE")
    item = InventoryItem(key=key, quantity=10)
    item.increase(10)

    assert item.quantity == 20


def test_inventory_item_increase_negative_quantity() -> None:
    key = InventoryKey(
        product_id="test_inventory_item_increase_negative_quantity", condition="NE"
    )
    item = InventoryItem(key=key, quantity=10)

    with pytest.raises(ValueError):
        item.increase(-10)


def test_inventory_item_decrease_valid() -> None:
    key = InventoryKey(product_id="test_inventory_item_decrease_valid", condition="NE")
    item = InventoryItem(key=key, quantity=10)

    item.decrease(5)

    assert item.quantity == 5


@pytest.mark.parametrize("value", [-10, 20])
def test_inventory_item_decrease_negative_quantity(value: int) -> None:
    key = InventoryKey(
        product_id="test_inventory_item_decrease_negative_quantity", condition="NE"
    )
    item = InventoryItem(key=key, quantity=10)

    with pytest.raises(ValueError):
        item.decrease(value)
