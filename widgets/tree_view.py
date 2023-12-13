# _*_ coding: UTF8 _*_

import wx
import typing
import authority
import database
import widgets.event
from . import event

class UI_xTreeView(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)

        grid_sizer_1 = wx.FlexGridSizer(2, 1, 0, 0)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, u"Управление"), wx.HORIZONTAL)
        grid_sizer_1.Add(sizer_3, 1, wx.EXPAND | wx.TOP, 10)

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

        sizer_3.Add((0, 0), 0, 0, 0)

        self.btn_edit_cols = wx.Button(self, wx.ID_ANY, u"…")
        self.btn_edit_cols.SetMinSize((30, -1))
        sizer_3.Add(self.btn_edit_cols, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        self.tree = wx.TreeCtrl(self, wx.ID_ANY, style=wx.BORDER_SUNKEN | wx.TR_HAS_BUTTONS | wx.TR_NO_BUTTONS | wx.TR_SINGLE)
        grid_sizer_1.Add(self.tree, 0, wx.EXPAND, 0)

        grid_sizer_1.AddGrowableRow(1)
        grid_sizer_1.AddGrowableCol(0)
        self.SetSizer(grid_sizer_1)
        grid_sizer_1.Fit(self)

        self.Layout()

_T = typing.TypeVar('_T', bound=database.Base)

class TreeView(UI_xTreeView, typing.Generic[_T]):
    _table_class: typing.Type[_T] = None
    _childs_field: str = None
    _level_field: str = None
    _items: typing.List[int]

    _flags: int = authority.CAN_ALL

    _entities: typing.List[_T] = []
    _selected_entities: typing.List[_T] = []

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.__bind()

    def __bind(self):
        self.btn_Add.Bind(wx.EVT_BUTTON, self.__on_add_click)
        self.btn_Edit.Bind(wx.EVT_BUTTON, self.__on_edit_click)
        self.btn_Delete.Bind(wx.EVT_BUTTON, self.__on_delete_click)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.__on_select)
        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.__on_dbclick, self.tree)

    def __on_dbclick(self, event):
        e = widgets.event.xEntityManageEvent(type=widgets.event.ManageTypes.NEED_SHOW_DETAIL, entity=self._selected_entities[0])
        wx.PostEvent(self, e)

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

    def __on_add_click(self, evt):
        e = widgets.event.xEntityManageEvent(type=widgets.event.ManageTypes.NEED_CREATE)
        wx.PostEvent(self, e)
    
    def __on_edit_click(self, evt):
        e = widgets.event.xEntityManageEvent(type=widgets.event.ManageTypes.NEED_EDIT, entity=self._selected_entities[0])
        wx.PostEvent(self, e)

    def __on_delete_click(self, evt):
        e = widgets.event.xEntityManageEvent(type=widgets.event.ManageTypes.NEED_DELETE, entities=list(self._selected_entities))
        wx.PostEvent(self, e)

    def set_table_class(self, table_class: typing.Type[_T]):
        if not issubclass(table_class, database.Base):
            raise Exception("{0} is not a database entity.".format(table_class.__name__))
        self._table_class = table_class

    def set_child_field(self, childs_field: str):
        self._childs_field = childs_field

    def set_level_field(self, level_field: str):
        if self._table_class == None:
            raise Exception("Database table class dont provided. Use set_table_class() for provide.")
        if not level_field in self._table_class.__table__.columns:
            raise Exception("{0} is not a column of {1} database entity.".format(level_field, self._table_class.__name__))
        self._level_field = level_field

    def set_flags(self, flags: int):
        self._flags = flags
        self.__update_controls_state()

    def __update_controls_state(self):
        self.btn_Add.Enable(self._flags & authority.CAN_CREATE > 0)
        self.btn_Edit.Enable(len(self._selected_entities) == 1 and self._flags & authority.CAN_EDIT > 0)
        self.btn_Delete.Enable(len(self._selected_entities) >= 1 and self._flags & authority.CAN_DELETE > 0)

    def reload(self):
        self._entities = []
        self._items = []
        items = database.get_session().query(self._table_class).filter((getattr(self._table_class, self._level_field) == 0)).all()
        for item in items:
            self._entities.append(item)
        
        self.tree.DeleteAllItems()

        self._root = self.tree.AddRoot('Объекты')
        def _insert_r(parent, parent_item):
            for e in (getattr(parent, self._childs_field) if not parent is None else self._entities):
                i = self.tree.AppendItem(parent_item, e.Name, data=e.RID)
                _insert_r(e, i)

        _insert_r(None, self._root)
        self.tree.ExpandAll()

    def __get_tree_item_by_entity(self, e: _T, parent = None):
        child, cookie = self.tree.GetFirstChild(self._root if parent == None else parent)
        while child.IsOk():
            entity_id = self.tree.GetItemData(child)
            print(entity_id, e.RID)
            if e.RID == entity_id:
                return child
            finded_item = self.__get_tree_item_by_entity(e, child)
            if finded_item != None:
                return finded_item
            child = self.tree.GetNextSibling(child)
        return None

    def select(self, e: _T):
        tree_item = self.__get_tree_item_by_entity(e)
        print(tree_item)
        if tree_item != None:
            self.tree.SelectItem(tree_item, True)