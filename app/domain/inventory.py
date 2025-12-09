from __future__ import annotations

from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True)
class InventoryKey:
    product_id: str
    condition: str

    def __post_init__(self) -> None:
        if len(self.product_id) == 0:
            raise ValueError("product_id must not be empty")

        if len(self.condition) == 0:
            raise ValueError("condition must not be empty")


@final
@dataclass(slots=True)
class InventoryItem:
    key: InventoryKey
    quantity: int

    @property
    def product_id(self):
        return self.key.product_id

    @property
    def condition(self):
        return self.key.condition

    @classmethod
    def create_invemtory_item(
        cls, product_id: str, condition: str, quantity: int
    ) -> InventoryItem:
        return InventoryItem(
            key=InventoryKey(product_id=product_id, condition=condition),
            quantity=quantity,
        )

    def __post_init__(self) -> None:
        if self.quantity < 0:
            raise ValueError("quantity must be >= 0")

    def increase(self, amount) -> None:
        if amount < 0:
            raise ValueError("amount must be >= 0")
        self.quantity += amount
