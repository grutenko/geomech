# _*_ coding: UTF8 _*_

from dataclasses import dataclass
import dataclasses
from typing import Callable
from typing import Any

@dataclass
class Column:
    name: str
    label: str = None
    size: int = -1
    modifier: Callable[[Any], str] = None