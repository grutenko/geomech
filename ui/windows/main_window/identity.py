from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@runtime_checkable
class Eq(Protocol):
    def __eq__(self, o: object) -> bool: ...


@dataclass
class Identity:
    o: Eq
    rel_data_o: Eq
    rel_data_target: Eq = None

    def __post_init__(self):
        if (
            not isinstance(self.o, Eq)
            or not isinstance(self.rel_data_o, Eq)
            or not isinstance(self.rel_data_target, Eq)
        ):
            raise ValueError("Identity must be equable objects.")

    def __eq__(self, o):
        return (
            isinstance(o, Identity)
            and o.o == self.o
            and o.rel_data_o == self.rel_data_o
            and o.rel_data_target == self.rel_data_target
        )
