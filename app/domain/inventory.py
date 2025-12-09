from __future__ import annotations

from collections.abc import ItemsView, Mapping
from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True)
class InventoryKey:
    """Represents a unique warehouse grouping key."""

    condition_id: str

    def __post_init__(self) -> None:
        if len(self.condition_id) == 0:
            raise ValueError("condition_id must not be empty")


@dataclass(slots=True)
class InventoryItem:
    """
    Represents a single warehouse item.

    Invariants:
    - quantity must be >= 0
    - condition_id must not be empty (delegated to InventoryKey)
    """

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


@dataclass(frozen=True, slots=True)
class InventorySnapshot:
    """
    Aggregated, read-only view of warehouse inventory.

    Snapshot is immutable and protects internal structure
    from external mutation.
    """

    _items: Mapping[InventoryKey, InventoryItem]

    @classmethod
    def from_items(
        cls,
        items: dict[InventoryKey, InventoryItem],
    ) -> InventorySnapshot:
        """Creates a snapshot and protects internal state from external mutation."""
        return cls(_items=dict(items))

    def get_qty(self, key: InventoryKey) -> int | None:
        item = self._items.get(key)
        if item is None:
            return None
        return item.quantity

    def items(self) -> ItemsView[InventoryKey, InventoryItem]:
        """Returns a read-only view over inventory items."""
        return self._items.items()
