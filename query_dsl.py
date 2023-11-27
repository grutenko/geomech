from dataclasses import (dataclass, field as dataclass_field)
from database import Base
from database import get_session
from database import init
from sqlalchemy.orm import Query
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import and_
from typing import (Type, TypeVar, Union, Callable, List, Any)
from enum import Enum
import operator

@dataclass
class FilterClause:
    field: str
    cmp: Callable[[Any, Any], Any]
    value: Any
    name: str = dataclass_field(default=None)

@dataclass
class FilterBy:
    clauses: List[FilterClause] = dataclass_field(default_factory=list)
    
    def find(self, field: str) -> FilterClause:
        for o in self.clauses:
            if o.field == field:
                return o
        return None
    
    def find_by_name(self, name: str) -> FilterClause:
        if name is None:
            return None
        for o in self.clauses:
            if o.name == name:
                return o
        return None

class Direction(Enum):
    ASC = 1
    DESC = 2

@dataclass
class OrderClause:
    field: str
    direction: Direction = dataclass_field(default=Direction.ASC)

@dataclass
class OrderBy:
    clauses: List[OrderClause] = dataclass_field(default_factory=list)

    def find_clause(self, field: str) -> FilterClause:
        for o in self.clauses:
            if type(o) == OrderClause and o.field == field:
                return o
        return None

_T = TypeVar('_T', bound=Base)

def build_query(table_class: Type[_T], order_by: OrderBy, filter_by: FilterBy) -> Query[_T]:
    q = get_session().query(table_class)

    def _make_order_clause(o: OrderClause):
        return asc(getattr(table_class, o.field)) if o.direction == Direction.ASC else desc(getattr(table_class, o.field))
    q = q.order_by(*list(map(_make_order_clause, order_by.clauses)))

    def _make_filter_clause(o: FilterClause):
        return (o.cmp(getattr(table_class, o.field), o.value))

    _filter_by_query = []
    for o in filter_by.clauses:
        _filter_by_query.append(_make_filter_clause(o))
    q = q.filter(and_(*_filter_by_query))

    return q