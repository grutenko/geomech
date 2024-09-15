from .column import Column

from typing import List, Tuple
from dataclasses import dataclass, field

@dataclass
class CellError:
    column: Column
    row: int
    message: str
    related: List[Tuple[Column, int]] = field(default_factory=lambda: [])