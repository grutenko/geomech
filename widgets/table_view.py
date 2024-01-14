# _*_ coding: UTF8 _*_

import wx
import wx.propgrid
import typing
import database
import query_dsl
import logging
import authority
import wizards.table_export
from column import Column
from . import event

_T = typing.TypeVar('_T', bound=database.Base)

class Ui_displayColsSelector(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((382, 373))
        self.SetTitle(u"Столбцы таблицы")

        sizer_1 = wx.FlexGridSizer(2, 1, 0, 0)

        self.cols_selector = wx.CheckListBox(self, wx.ID_ANY, choices=[], style=wx.LB_MULTIPLE)
        sizer_1.Add(self.cols_selector, 0, wx.EXPAND, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        sizer_1.AddGrowableRow(0)
        sizer_1.AddGrowableCol(0)
        self.SetSizer(sizer_1)

        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()
        self.Centre()

class _displayColsSelector(Ui_displayColsSelector):
    __cols: typing.List[Column]

    def __init__(self, cols: typing.List[Column], selected_cols: typing.List[int] = [], *args, **kw):
        super().__init__(*args, **kw)
        self.__cols = cols
        self.__set_cols(selected_cols)

    def __set_cols(self, selected_cols: typing.List[int]):
        self.cols_selector.InsertItems(list(map(lambda col: col.label if not col.label is None else col.name, self.__cols)), 0)
        self.cols_selector.SetCheckedItems(selected_cols)

    def get_selected_cols(self):
        return list(map(lambda index: self.__cols[index], self.cols_selector.GetCheckedItems()))
    
class Ui_orderBySelector(wx.Dialog):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetSize((500, 300))
        self.SetTitle(u"Сортировка таблицы")

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.fields = wx.propgrid.PropertyGridManager(self, wx.ID_ANY, style=wx.propgrid.PG_HIDE_CATEGORIES | wx.propgrid.PG_TOOLBAR)
        sizer_1.Add(self.fields, 1, wx.EXPAND, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self, wx.ID_OK, "")
        self.button_OK.SetDefault()
        sizer_2.AddButton(self.button_OK)

        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, "")
        sizer_2.AddButton(self.button_CANCEL)

        sizer_2.Realize()

        self.SetSizer(sizer_1)

        self.SetAffirmativeId(self.button_OK.GetId())
        self.SetEscapeId(self.button_CANCEL.GetId())

        self.Layout()
        self.Centre()
    
class _orderBySelector(Ui_orderBySelector):
    __order_by: query_dsl.OrderBy
    __cols: typing.List[Column]
    __props: typing.List[wx.propgrid.PGProperty]

    def __init__(self, cols: typing.List[Column], order_by: query_dsl.OrderBy = query_dsl.OrderBy(), *args, **kwds):
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
    
class Ui_xControlTableView(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)

        sizer_1 = wx.FlexGridSizer(2, 1, 0, 0)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Управление"), wx.HORIZONTAL)
        sizer_1.Add(sizer_3, 1, wx.EXPAND | wx.TOP, 10)

        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(sizer_2, 1, wx.ALL | wx.EXPAND, 5)

        self.btn_Add = wx.Button(self, wx.ID_ANY, u"Добавить")
        sizer_2.Add(self.btn_Add, 0, wx.RIGHT, 5)

        self.btn_Edit = wx.Button(self, wx.ID_ANY, u"Редактировать")
        self.btn_Edit.Enable(False)
        sizer_2.Add(self.btn_Edit, 0, wx.RIGHT, 5)

        self.btn_Delete = wx.Button(self, wx.ID_ANY, u"Удалить")
        self.btn_Delete.Enable(False)
        sizer_2.Add(self.btn_Delete, 0, 0, 0)

        self.sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(self.sizer_4, 1, wx.ALIGN_CENTER_VERTICAL, 0)

        self.btn_order_by = wx.Button(self, wx.ID_ANY, u"Сортировка")
        self.sizer_4.Add(self.btn_order_by, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.btn_filter_by = wx.Button(self, wx.ID_ANY, u"Фильтр")
        self.sizer_4.Add(self.btn_filter_by, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.btn_settings = wx.Button(self, wx.ID_ANY, u"…")
        self.btn_settings.SetMinSize((30, -1))
        sizer_3.Add(self.btn_settings, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
        sizer_1.Add(self.list, 1, wx.EXPAND, 0)

        sizer_1.AddGrowableRow(1)
        sizer_1.AddGrowableCol(0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)

        self.Layout()

class TableView(Ui_xControlTableView, typing.Generic[_T]):
    _table_class: typing.Type[_T] = None
    _available_cols: typing.List[Column] = []
    _cols: typing.List[Column] = []

    _order_by: query_dsl.OrderBy = query_dsl.OrderBy()
    _filter_by: query_dsl.FilterBy = query_dsl.FilterBy()

    _entities: typing.List[_T] = []
    _selected_entities: typing.Set[_T] = set()

    _flags: int = authority.CAN_ALL

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.__bind()

    def set_table_class(self, table_class: typing.Type[_T]):
        if not issubclass(table_class, database.Base):
            raise Exception(table_class.__name__ + " is not a database entity.")
        self._table_class = table_class

    def set_available_cols(self, available_cols: typing.List[Column]):
        for col in available_cols:
            if not col.name in self._table_class.__table__.columns:
                raise Exception("Column " + col.name + " not found in entity " + self.table_class.__name__ + ".")
        self._available_cols = available_cols

    def set_flags(self, flags):
        self._flags = flags

    def __bind(self):
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.__on_item_selected)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.__on_item_deselected)
        self.btn_Add.Bind(wx.EVT_BUTTON, self.__on_add_click)
        self.btn_Edit.Bind(wx.EVT_BUTTON, self.__on_edit_click)
        self.btn_Delete.Bind(wx.EVT_BUTTON, self.__on_delete_click)
        self.btn_settings.Bind(wx.EVT_BUTTON, self.__on_settings)
        self.btn_order_by.Bind(wx.EVT_BUTTON, self.__on_order_by_click)
        self.btn_filter_by.Bind(wx.EVT_BUTTON, self.__on_open_filter_click)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.__on_dbclick, self.list)

    def __on_dbclick(self, evt):
        entity = self._entities[self.list.GetFirstSelected()]
        e = event.xEntityManageEvent(type=event.ManageTypes.NEED_SHOW_DETAIL, entity=entity)
        wx.PostEvent(self, e)

    def __on_item_selected(self, event: wx.ListEvent):
        self._selected_entities.add(self._entities[event.GetIndex()])
        self.__update_controls_state()

    def __on_item_deselected(self, event: wx.ListEvent):
        self._selected_entities.remove(self._entities[event.GetIndex()])
        self.__update_controls_state()

    def __find_col(self, col_name):
        for col in self._available_cols:
            if col_name == col.name:
                return col
        return None

    def __on_add_click(self, evt):
        e = event.xEntityManageEvent(type=event.ManageTypes.NEED_CREATE)
        wx.PostEvent(self, e)
    
    def __on_edit_click(self, evt):
        e = event.xEntityManageEvent(type=event.ManageTypes.NEED_EDIT, entity=list(self._selected_entities)[0])
        wx.PostEvent(self, e)

    def __on_delete_click(self, evt):
        e = event.xEntityManageEvent(type=event.ManageTypes.NEED_DELETE, entities=list(self._selected_entities))
        wx.PostEvent(self, e)

    def __on_settings(self, evt: wx.CommandEvent):
        menu = wx.Menu()
        item = menu.Append(wx.MenuItem(menu, wx.NewId(), "Настроить столбцы"))
        self.Bind(wx.EVT_MENU, self.__on_edit_cols_click, item)
        export_menu = wx.Menu()
        item = export_menu.Append(wx.MenuItem(export_menu, wx.NewId(), "XLS"))
        self.Bind(wx.EVT_MENU, self.__on_export_xls, item)
        item = export_menu.Append(wx.MenuItem(export_menu, wx.NewId(), "CSV"))
        self.Bind(wx.EVT_MENU, self.__on_export_csv, item)
        item = menu.Append(wx.MenuItem(menu, wx.NewId(), "Экспортировать как", subMenu=export_menu))
        export_menu = wx.Menu()
        item = export_menu.Append(wx.MenuItem(export_menu, wx.NewId(), "XLS"))
        self.Bind(wx.EVT_MENU, self.__on_export_selected_xls, item)
        item = export_menu.Append(wx.MenuItem(export_menu, wx.NewId(), "CSV"))
        self.Bind(wx.EVT_MENU, self.__on_export_selected_csv, item)
        export_selected = wx.MenuItem(menu, wx.NewId(), "Экспортировать выделеное как", subMenu=export_menu)
        item = menu.Append(export_selected)
        if len(self._selected_entities) == 0:
            export_selected.Enable(False)
        x, y = self.btn_settings.GetPosition()
        sx, sy = self.btn_settings.GetSize()
        self.PopupMenu(menu, (x, y + sy))

    def __open_export_wizard(self, entities, format):
        w = wizards.table_export.TableExport(
            available_cols=self._available_cols,
            cols=self._cols,
            entities=entities,
            parent=self.GetParent())
        w.Show()

    def __on_export_xls(self, event):
        self.__open_export_wizard(self._entities, 'xls')

    def __on_export_csv(self, event):
        self.__open_export_wizard(self._entities, 'csv')

    def __on_export_selected_xls(self, event):
        self.__open_export_wizard(self._selected_entities, 'xls')

    def __on_export_selected_csv(self, event):
        self.__open_export_wizard(self._selected_entities, 'csv')

    def __on_order_by_click(self, evt):
        w = _orderBySelector(self._available_cols, self._order_by, parent=self.GetParent())
        ret = w.ShowModal()
        if ret == wx.ID_OK:
            self._order_by = w.get_order_by()
            self.reload()
        w.Destroy()

    def __on_open_filter_click(self, evt):
        e = event.xEntityManageEvent(type=event.ManageTypes.NEED_FILTER)
        wx.PostEvent(self, e)

    def get_filter_by(self):
        return self._filter_by

    def set_filter_by(self, filter_by: query_dsl.FilterBy, do_reload = True):
        self._filter_by = filter_by
        if do_reload:
            self.reload()

    def __on_edit_cols_click(self, event):
        selected_cols = []
        for col in list(self._cols):
            selected_cols.append(self._available_cols.index(col))
        w = _displayColsSelector(self._available_cols, selected_cols, parent=self.GetParent())
        ret = w.ShowModal()
        if ret == wx.ID_OK:
            self._cols = w.get_selected_cols()
            self.repaint()
        w.Destroy()

    def set_order_by(self, order_by: query_dsl.OrderBy, do_reload = True):
        for clause in order_by.clauses:
            if self.__find_col(clause.field) == None:
                logging.warning("Column " + clause.field + " not found in available cols and cannot use for ordering.")
                del order_by.clauses[order_by.clauses.index(clause)]
        self._order_by = order_by
        if do_reload:
            self.reload()

    def set_display_cols(self, cols: typing.List[str], do_repaint):
        self._cols = []
        for col_name in cols:
            col = self.__find_col(col_name)
            if col != None:
                self._cols.append(col)
            else:
                logging.warning("Column " + col_name + " not found in available cols and cannot display.")
        if do_repaint:
            self.repaint()

    def get_entities(self) -> typing.List[_T]:
        return self._entities
    
    def get_selected_entities(self) -> typing.List[_T]:
        return self._selected_entities
    
    def __update_controls_state(self):
        self.sizer_4.Layout()
        self.btn_order_by.Update()
        self.btn_Delete.Enable(len(self._selected_entities) >= 1)
        self.btn_Edit.Enable(len(self._selected_entities) == 1)
        self.btn_order_by.Enable(self._flags & authority.CAN_SORT > 0)
        self.btn_filter_by.Enable(self._flags & authority.CAN_FILTER > 0)
    
    def repaint(self):
        self.list.DeleteAllItems()
        self.list.DeleteAllColumns()
        for col in self._cols:
            colIndx = self.list.AppendColumn(
                col.label if not col.label is None else col.name,
                wx.LIST_FORMAT_LEFT, col.size)
        if len(self._cols) == 0:
            return
        
        def _set_col(e, row_index, col_index, col, value):
            value = col.modifier(e, value) if not col.modifier is None else str(value)
            self.list.SetItem(row_index, col_index, value)

        for row_index, e in enumerate(self._entities):
            self.list.InsertItem(row_index, "")
            for col_index, col in enumerate(self._cols):
                _set_col(e, row_index, col_index, col, e.__dict__[col.name])

        for e in list(self._selected_entities):
            if e in self._entities:
                self.list.Select(self._entities.index(e))

    def reload(self):
        if self._table_class == None:
            raise Exception("TableView dont initialized correctly. use set_table_class(), set_flags(), set_available_cols() for correct configure this widget.")

        q = query_dsl.build_query(self._table_class, self._order_by, self._filter_by)
        self._entities = q.all()
        self._selected_entities = set()
        self.repaint()

    def clear_filter(self, do_reload = True):
        self._filter_by = query_dsl.FilterBy()
        if do_reload:
            self.reload()

    def select(self, entities: typing.List[_T]):
        for e in entities:
            if not e in self._entities:
                logging.warning("Entity " + e.__class__.__name__ + "#" + e.RID + " not found in curent table set and cannot be selected.")
            else:
                self.list.Select(self._entities.index(e))
