import wx
from ui import UI_xTreeView
from typing import (
    Type,
    TypeVar,
    Generic,
    List
)
from database import (
    Base,
    get_session
)

_T = TypeVar('_T', bound=Base)

class xTreeView(UI_xTreeView, Generic[_T]):
    _table_class: Type[_T]
    _level_field: str
    _childs_field: str
    _entities: List[_T]
    _items: List[int]

    _root: int

    def __init__(self, table_class: Type[_T], level_field: str = 'Level', chils_field: str = 'childrens', *args, **kwds):
        super().__init__(*args, **kwds)
        self._table_class = table_class
        self._level_field = level_field
        self._childs_field = chils_field

        self.refresh()

    def refresh(self):
        self._entities = []
        self._items = []
        items = get_session().query(self._table_class).filter((getattr(self._table_class, self._level_field) == 0)).all()
        for item in items:
            self._entities.append(item)
        self.__render()

    def __render(self):
        self.tree.DeleteAllItems()

        self._root = self.tree.AddRoot('Объекты')
        def _insert_r(parent, parent_item):
            for e in (getattr(parent, self._childs_field) if not parent is None else self._entities):
                i = self.tree.AppendItem(parent_item, e.Name, data=e.RID)
                _insert_r(e, i)

        _insert_r(None, self._root)

    def select(self, e: _T):
        child, cookie = self.tree.GetFirstChild()
        while child.IsOk():
            entity_id = self.tree.GetItemData(child)
            if e.RID == entity_id:
                self.tree.SelectItem(child)
                return
            (child, cookie) = self.tree.GetNextChild(child, cookie)