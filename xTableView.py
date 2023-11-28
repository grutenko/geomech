import wx
import wx.propgrid
from typing import (
    Type,
    List,
    Tuple,
    Callable,
    TypeVar,
    Generic,
    Set,
    Any
)
from enum import Enum

from database import (
    Base,
    get_session
)
from ui import Ui_xControlTableView
from ui import Ui_displayColsSelector
from ui import Ui_orderBySelector

from sqlalchemy.orm import Query
from sqlalchemy import (
    desc, asc
)
from dataclasses import dataclass
import query_dsl

@dataclass
class Column:
    name: str
    label: str = None
    size: int = -1
    modifier: Callable[[Any], str] = None

CAN_CREATE = 0b00001
CAN_EDIT = 0b00010
CAN_DELETE = 0b00100
CAN_SORT = 0b01000
CAN_FILTER = 0b10000
CAN_ALL = CAN_EDIT | CAN_DELETE | CAN_CREATE | CAN_SORT | CAN_FILTER

_T = TypeVar('_T', bound=Base)

class _displayColsSelector(Ui_displayColsSelector):

    __cols: List[Column]

    def __init__(self, cols: List[Column], selected_cols: List[int] = [], *args, **kw):
        super().__init__(*args, **kw)
        self.__cols = cols
        self.__set_cols(selected_cols)

    def __set_cols(self, selected_cols: List[int]):
        self.cols_selector.InsertItems(list(map(lambda col: col.label if not col.label is None else col.name, self.__cols)), 0)
        self.cols_selector.SetCheckedItems(selected_cols)

    def get_selected_cols(self):
        return list(map(lambda index: self.__cols[index], self.cols_selector.GetCheckedItems()))
    
class _orderBySelector(Ui_orderBySelector):
    __order_by: query_dsl.OrderBy
    __cols: List[Column]
    __props: List[wx.propgrid.PGProperty]

    def __init__(self, cols: List[Column], order_by: query_dsl.OrderBy = query_dsl.OrderBy(), *args, **kwds):
        super().__init__(*args, **kwds)
        self.__order_by = order_by
        self.__cols = cols
        self.__props = []
        for index, col in enumerate(self.__cols):
            choices = [
                '--- ---',
                'По возрастанию',
                'По убыванию'
            ]
            self.__props.append(self.fields.Append(wx.propgrid.EnumProperty(col.label if not col.label is None else col.name, col.name, choices)))
            for o in self.__order_by.clauses:
                if o.field == col.name:
                    self.fields.SetPropertyValue(self.__props[index], 1 if o.direction == query_dsl.Direction.ASC else 2)
                    break

    def get_order_by(self) -> query_dsl.OrderBy:
        order_by = []
        for index, col in enumerate(self.__cols):
            v = self.__props[index].GetValue()
            if v > 0:
                order_by.append(query_dsl.OrderClause(col.name, query_dsl.Direction.ASC if v == 1 else query_dsl.Direction.DESC))
        return query_dsl.OrderBy(order_by)


class xTableView(Ui_xControlTableView, Generic[_T]):
    class State(Enum):
        INIT = 1
        LOADING = 2
        COMMON = 3

    _table_class: Type[_T]
    _available_cols: List[Column]
    _cols: List[Column]
    _initial_order_by: query_dsl.OrderBy
    _order_by: query_dsl.OrderBy
    _initial_filter_by: query_dsl.FilterBy
    _filter_by: query_dsl.FilterBy
    _filter_editor: Type[wx.Window]
    _flags: int
    _on_create: Callable[[], None]
    _on_edit: Callable[[_T], None]
    _on_delete: Callable[[List[_T]], None]
    _on_dbclick: Callable[[_T], None]
    _on_deselect: Callable[[_T], None]

    __state: State

    _entities: List[_T] = []
    _selected_entities: Set[_T] = set()

    def __init__(self, 
                 table_class: Type[_T],
                 available_cols: List[Column] = [],
                 cols: List[str] = [],
                 initial_order_by: query_dsl.OrderBy = query_dsl.OrderBy(),
                 initial_filter_by: query_dsl.FilterBy = query_dsl.FilterBy(),
                 filter_window: Type[wx.Window] = None,
                 flags: int = CAN_ALL,
                 on_create: Callable[[], None] = None,
                 on_edit: Callable[[_T], None] = None,
                 on_delete: Callable[[List[_T]], None] = None,
                 on_dbclick: Callable[[_T], None] = None,
                 on_deselect: Callable[[_T], None] = None,
                 *args,
                 **kw):
        super().__init__(*args, **kw)

        self._table_class = table_class
        self._available_cols = available_cols
        self._cols = []
        for col in available_cols:
            if col.name in cols:
                self._cols.append(col)
        self._initial_order_by = self._order_by = initial_order_by
        self._initial_filter_by = self._filter_by = initial_filter_by
        self._flags = flags
        self._on_create = on_create
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._on_dbclick = on_dbclick
        self._on_deselect = on_deselect
        self._filter_editor = filter_window

        self.__init_columns()
        self.__bind()
        self.__state = self.State.INIT
        self.refresh()
        self.__update_controls_state()

    def __bind(self):
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__on_item_selected)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.__on_item_deselected)
        self.btn_Add.Bind(wx.EVT_BUTTON, self.__on_add_click)
        self.btn_Edit.Bind(wx.EVT_BUTTON, self.__on_edit_click)
        self.btn_Delete.Bind(wx.EVT_BUTTON, self.__on_delete_click)
        self.list.Bind(wx.EVT_LEFT_DCLICK, self.__on_double_click)
        self.btn_edit_cols.Bind(wx.EVT_BUTTON, self.__on_edit_cols_click)
        self.btn_order_by.Bind(wx.EVT_BUTTON, self.__on_order_by_click)
        self.btn_filter_by.Bind(wx.EVT_BUTTON, self.__on_open_filter_click)

    def __on_order_by_click(self, event):
        w = _orderBySelector(self._available_cols, self._order_by, parent=self.GetParent())
        ret = w.ShowModal()
        if ret == wx.ID_OK:
            self._order_by = w.get_order_by()
            self.refresh()
            self.__update_controls_state()
            print(self._order_by)
        w.Destroy()

    def __on_open_filter_click(self, event):
        if self._filter_editor is None:
            return
        w = self._filter_editor(filter_by=self._filter_by, parent=super().GetParent())
        ret = w.ShowModal()
        if ret == wx.ID_OK:
            self._filter_by = w.get_filter()
            self.refresh()

    def __on_edit_cols_click(self, event):
        selected_cols = []
        for col in list(self._cols):
            selected_cols.append(self._available_cols.index(col))
        w = _displayColsSelector(self._available_cols, selected_cols, parent=self.GetParent())
        ret = w.ShowModal()
        if ret == wx.ID_OK:
            self._cols = w.get_selected_cols()
            self.list.DeleteAllColumns()
            self.__init_columns()
            self.__render()
        w.Destroy()

    def __on_double_click(self, event):
        if len(self._selected_entities) == 0:
            return
        if not self._on_dbclick is None:
            self._on_dbclick(list(self._selected_entities)[0])

    def __on_add_click(self, event):
        if not self._on_create is None:
            self._on_create()

    def __on_edit_click(self, event):
        if not self._on_edit is None:
            self._on_edit(list(self._selected_entities)[0])

    def __on_delete_click(self, event):
        if not self._on_delete is None:
            self._on_delete(list(self._selected_entities))

    def __on_item_selected(self, event: wx.ListEvent):
        self._selected_entities.add(self._entities[event.GetIndex()])
        self.__update_controls_state()

    def __on_item_deselected(self, event: wx.ListEvent):
        self._selected_entities.remove(self._entities[event.GetIndex()])
        if not self._on_deselect is None:
            self._on_deselect(self._entities[event.GetIndex()])
        self.__update_controls_state()

    def __update_controls_state(self):
        self.sizer_4.Layout()
        self.btn_order_by.Update()
        self.btn_Delete.Enable(len(self._selected_entities) >= 1)
        self.btn_Edit.Enable(len(self._selected_entities) == 1)
        self.btn_order_by.Enable(self._flags & CAN_SORT > 0)
        self.btn_filter_by.Enable(self._flags & CAN_FILTER > 0)

    def __init_columns(self):
        for col in self._cols:
            colIndx = self.list.AppendColumn(col.label if not col.label is None else col.name, wx.LIST_FORMAT_LEFT, col.size)

    def __set_state(self, state: State):
        if state == self.State.LOADING:
            self.list.Enable(False)
        elif state == self.State.COMMON:
            self.list.Enable(True)

    def __render(self):
        self.list.DeleteAllItems()

        def _set_col(row_index, col_index, col, value):
            value = col.modifier(value) if not col.modifier is None else str(value)
            self.list.SetItem(row_index, col_index, value)

        if len(self._cols) == 0:
            return
        
        for row_index, e in enumerate(self._entities):
            self.list.InsertItem(row_index, "")
            for col_index, col in enumerate(self._cols):
                _set_col(row_index, col_index, col, e.__dict__[col.name])

        for e in list(self._selected_entities):
            if e in self._entities:
                self.list.Select(self._entities.index(e))

    def refresh(self):
        self.__set_state(self.State.LOADING)
        self._entities = query_dsl.build_query(self._table_class, self._order_by, self._filter_by).all()
        self._selected_entities = set()

        self.__render()
        self.__update_controls_state()
        self.__set_state(self.State.COMMON)

    def select(self, e: _T):
        if e in self._entities:
            self.list.Select(self._entities.index(e))
    
