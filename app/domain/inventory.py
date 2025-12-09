from __future__ import annotations

from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True)
class InventoryKey:
    condition_id: str

    def __post_init__(self) -> None:
        if len(self.condition_id) == 0:
            raise ValueError("condition_id must not be empty")


@dataclass(slots=True)
class InventoryItem:
    _key: InventoryKey
    _quantity: int

    @property
    def key(self) -> InventoryKey:
        return self._key

    @property
    def condition_id(self) -> str:
        return self._key.condition_id

    @property
    def quantity(self) -> int:
        return self._quantity

    @classmethod
    def create(cls, condition_id: str, quantity: int) -> InventoryItem:
        return cls(
            _key=InventoryKey(condition_id=condition_id),
            _quantity=quantity,
        )

    def __post_init__(self) -> None:
        if self._quantity < 0:
            raise ValueError("quantity must be >= 0")

    def increase(self, amount: int) -> None:
        if amount < 0:
            raise ValueError("amount must be >= 0")
        self._quantity += amount
