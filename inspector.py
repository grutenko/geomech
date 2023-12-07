# _*_ coding: UTF8 _*_

from typing import (
    Generic,
    TypeVar,
    Type
)
from database import Base

_T = TypeVar('_T', bound=Base)

''' TODO: Написать окна детального просмотра для всех сущностей'''

class Inspector:
    pass

def get_inspector_for(table_class: Type[_T]) -> Type[Inspector]:
    pass