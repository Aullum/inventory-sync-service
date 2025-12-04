import pytest

from app.domain.inventory import InventoryItem, InventoryKey


def test_inventory_key_is_valid() -> None:
    key = InventoryKey(product_id="Test_G_1200", condition="UE")

    assert key.product_id == "Test_G_1200"
    assert key.condition == "UE"


def test_inventory_key_invalid_empty_product_id() -> None:
    with pytest.raises(ValueError):
        InventoryKey(product_id="", condition="NE")


def test_inventory_item_valid() -> None:
    key = InventoryKey(product_id="Test_A_1000", condition="NE")
    item = InventoryItem(key=key, quantity=10)

    assert item.product_id == "Test_A_1000"
    assert item.condition == "NE"
    assert item.quantity == 10


def test_inventory_item_invalid_negative_quantity() -> None:
    key = InventoryKey(product_id="Test_G_500", condition="WE")

    with pytest.raises(ValueError):
        InventoryItem(key=key, quantity=-1)
