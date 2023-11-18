import wx
import wx.propgrid
from typing import (
    Type,
    List,
    Tuple,
    Callable,
    TypeVar,
    Generic,
    Set
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

CAN_CREATE = 0b00001
CAN_EDIT = 0b00010
CAN_DELETE = 0b00100
CAN_ALL = CAN_EDIT | CAN_DELETE | CAN_CREATE

_T = TypeVar('_T', bound=Base)
'''
Создает SqlAlchemy запрос из структур:
1. order_by: [(<field>, <direction>), ...]
2. filter_by: [(<field>, <eq>, <value>), ...]
'''
def _build_query(table_class: Type[_T], order_by: List[Tuple], filter_by: List[Tuple]) -> Query[_T]:
    q = get_session().query(table_class)

    def _make_order_clause(o):
        return asc(table_class.__dict__[o[0]]) if o[1] == 'asc' else desc(table_class.__dict__[o[0]])
    q = q.order_by(*list(map(_make_order_clause, order_by)))

    return q
        

class _displayColsSelector(Ui_displayColsSelector):

    __cols: List[Tuple]

    def __init__(self, cols: List[Tuple], selected_cols: List[int] = [], *args, **kw):
        super().__init__(*args, **kw)
        self.__cols = cols
        self.__set_cols(selected_cols)

    def __set_cols(self, selected_cols: List[int]):
        self.cols_selector.InsertItems(list(map(lambda col: col[1], self.__cols)), 0)
        self.cols_selector.SetCheckedItems(selected_cols)

    def get_selected_cols(self):
        return list(map(lambda index: self.__cols[index], self.cols_selector.GetCheckedItems()))
    
class _orderBySelector(Ui_orderBySelector):
    __order_by: List[Tuple]
    __cols: List[Tuple]
    __props: List[wx.propgrid.PGProperty]

    def __init__(self, cols: List[Tuple], order_by: List[Tuple] = [], *args, **kwds):
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
            self.__props.append(self.fields.Append(wx.propgrid.EnumProperty(col[1], col[0], choices)))
            for field, direction in self.__order_by:
                if field == col[0]:
                    self.fields.SetPropVal(self.__props[index], 1 if direction == 'asc' else 2)
                    break

    def get_order_by(self) -> List[Tuple]:
        order_by = []
        for index, col in enumerate(self.__cols):
            v = self.__props[index].GetValue()
            if v > 0:
                order_by.append((col[0], 'asc' if v == 1 else 'desc'))
        return order_by


class xControlTableView(Ui_xControlTableView, Generic[_T]):
    class State(Enum):
        INIT = 1
        LOADING = 2
        COMMON = 3

    _table_class: Type[_T]
    _available_cols: List[Tuple]
    _cols: List[Tuple]
    _initial_order_by: List[Tuple]
    _order_by: List[Tuple]
    _initial_filter_by: List[Tuple]
    _filter_by: List[Tuple]
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
                 available_cols: List[Tuple] = [],
                 cols: List[Tuple] = None,
                 initial_order_by: List[Tuple] = [],
                 initial_filter_by: List[Tuple] = [],
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
        self._cols = available_cols if cols == None else cols
        self._initial_order_by = self._order_by = initial_order_by
        self._initial_filter_by = self._filter_by = initial_filter_by
        self._flags = flags
        self._on_create = on_create
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._on_dbclick = on_dbclick
        self._on_deselect = on_deselect

        self.__init_columns()
        self.__bind()
        self.__state = self.State.INIT
        self.refresh()

    def __bind(self):
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__on_item_selected)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.__on_item_deselected)
        self.btn_Add.Bind(wx.EVT_BUTTON, self.__on_add_click)
        self.btn_Edit.Bind(wx.EVT_BUTTON, self.__on_edit_click)
        self.btn_Delete.Bind(wx.EVT_BUTTON, self.__on_delete_click)
        self.list.Bind(wx.EVT_LEFT_DCLICK, self.__on_double_click)
        self.btn_edit_cols.Bind(wx.EVT_BUTTON, self.__on_edit_cols_click)
        self.btn_order_by.Bind(wx.EVT_BUTTON, self.__on_order_by_click)

    def __on_order_by_click(self, event):
        w = _orderBySelector(self._available_cols, self._order_by, parent=self.GetParent())
        ret = w.ShowModal()
        if ret == wx.ID_OK:
            self._order_by = w.get_order_by()
            self.refresh()
            self.__update_controls_state()
        w.Destroy()


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
        def _eq_orders():
            _eq = True
            _eq = _eq and len(self._order_by) == len(self._initial_order_by)
            for index, clause in enumerate(self._order_by):
                _eq = _eq and all(x == y for x, y in zip(clause, self._initial_order_by[index]))
            return _eq
        self.btn_order_by.SetLabel("Сортировка [+]" if not _eq_orders() else "Сортировка")
        self.sizer_4.Layout()
        self.btn_order_by.Update()
        self.btn_Delete.Enable(len(self._selected_entities) >= 1)
        self.btn_Edit.Enable(len(self._selected_entities) == 1)

    def __init_columns(self):
        for col in self._cols:
            if len(col) > 3 or len(col) < 2:
                raise Exception('Неверный формат описния столбцов.'
                                + ' Должен быть: (<field> [, <label> [, <size>]])')
            colIndx = 0
            if len(col) == 2:
                colIndx = self.list.AppendColumn(col[1])
            elif len(col) == 3:
                colIndx = self.list.AppendColumn(col[1], wx.LIST_FORMAT_LEFT, col[2])
            self.list.SetColumnWidth(colIndx, wx.COL_WIDTH_AUTOSIZE)

    def __set_state(self, state: State):
        if state == self.State.LOADING:
            self.list.Enable(False)
        elif state == self.State.COMMON:
            self.list.Enable(True)

    def __render(self):
        self.list.DeleteAllItems()

        def _set_col(row_index, index, value):
            self.list.SetItem(row_index, col_index, str(value))

        if len(self._cols) == 0:
            return
        
        for row_index, e in enumerate(self._entities):
            self.list.InsertItem(row_index, "")
            for col_index, col in enumerate(self._cols):
                _set_col(row_index, col_index, e.__dict__[col[0]])

        for e in list(self._selected_entities):
            if e in self._entities:
                self.list.Select(self._entities.index(e))

    def refresh(self):
        self.__set_state(self.State.LOADING)
        ''' TODO: Сделать фильтрацию '''
        self._entities = _build_query(self._table_class, self._order_by, self._filter_by).all()
        self._selected_entities = set()

        self.__render()
        self.__update_controls_state()
        self.__set_state(self.State.COMMON)

    def select(self, e: _T):
        if e in self._entities:
            self.list.Select(self._entities.index(e))

    
