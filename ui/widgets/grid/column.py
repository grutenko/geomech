from .cell_type_proto import CellType

from dataclasses import dataclass
from typing import Optional


@dataclass
class Column:
    id: any
    cell_type: CellType
    name_short: str
    name_long: Optional[str]
    init_width: int = -1

    def __eq__(self, value: object) -> bool:
        return type(value) == Column and value.id == self.id