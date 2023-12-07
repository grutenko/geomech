# _*_ coding: UTF8 _*_

import wx
from ui import UI_xTreeView
from typing import (
    Type,
    TypeVar,
    Generic,
    Callable,
    List,
    Union
)
from database import (
    Base,
    get_session
)
import authority

_T = TypeVar('_T', bound=Base)

class xTreeView(UI_xTreeView, Generic[_T]):
    _table_class: Type[_T]
    _level_field: str
    _childs_field: str
    _entities: List[_T]
    _selected_entities: List[_T] = []
    _items: List[int]

    _root: int

    _on_create: Callable[[], None]
    _on_edit: Callable[[_T], None]
    _on_delete: Callable[[List[_T]], None]

    _flags: int

    def __init__(self, 
                 table_class: Type[_T], 
                 level_field: str = 'Level', 
                 childs_field: str = 'childrens',
                 on_create: Callable[[Union[_T, None]], None] = None,
                 on_edit: Callable[[_T], None] = None,
                 on_delete: Callable[[List[_T]], None] = None,
                 flags = authority.CAN_ALL,
                 *args, **kwds):
        super().__init__(*args, **kwds)
        self._table_class = table_class
        self._level_field = level_field
        self._childs_field = childs_field
        self._on_create = on_create
        self._on_edit = on_edit
        self._on_delete = on_delete

        self._flags = flags

        self.__bind()
        self.__update_controls_state()

        self.refresh()

    def __bind(self):
        self.btn_Add.Bind(wx.EVT_BUTTON, self.__on_add_click)
        self.btn_Edit.Bind(wx.EVT_BUTTON, self.__on_edit_click)
        self.btn_Delete.Bind(wx.EVT_BUTTON, self.__on_delete_click)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.__on_select)

    def __on_select(self, event):
        rid = self.tree.GetItemData(event.GetItem())
        def _find_selection_r(parent):
            entities = self._entities if parent == None else parent.__dict__[self._childs_field];
            for e in entities:
                if e.RID == rid:
                    return e
                else:
                    child_e = _find_selection_r(e)
                    if child_e != None:
                        return child_e
            return None
        
        e = _find_selection_r(None)
        self._selected_entities = [e] if e != None else []
        self.__update_controls_state()

    def __on_add_click(self, event):
        if self._on_create is not None:
            self._on_create(self._selected_entities[0] if len(self._selected_entities) > 0 else None)

    def __on_edit_click(self, event):
        if self._on_edit is not None:
            self._on_edit(self._selected_entities[0])

    def __on_delete_click(self, event):
        if self._on_delete is not None:
            self._on_delete(self._selected_entities)

    def __update_controls_state(self):
        self.btn_Add.Enable(self._flags & authority.CAN_CREATE > 0)
        self.btn_Edit.Enable(len(self._selected_entities) == 1 and self._flags & authority.CAN_EDIT > 0)
        self.btn_Delete.Enable(len(self._selected_entities) >= 1 and self._flags & authority.CAN_DELETE > 0)

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