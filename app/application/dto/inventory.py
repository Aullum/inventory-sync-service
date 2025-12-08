from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ItemIventoryDTO:
    """
    A single inventory record received from an external system (warehouse, etc.).
    This isn't yet a domain entity, just normalized data.
    """

    product_id: str
    condition: str
    quantity: int


@dataclass(frozen=True, slots=True)
class InventorySnapshotDTO:
    """
    Inventory snapshot with a single API call.
    """

    source: str
    items: Sequence[ItemIventoryDTO]
