import wx
import wx.lib.mixins.listctrl as listmix
from pony.orm import db_session, select

from database import PmProperty
from ui.delete_object import delete_object
from ui.icon import get_icon

from .property_editor import PmPropertyEditor


class Properties(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_HORZ_TEXT | wx.TB_BOTTOM)
        tool = self._toolbar.AddTool(wx.ID_ADD, "Добавить свойство", get_icon("add-row"))
        self._toolbar.Bind(wx.EVT_TOOL, self._on_create, id=wx.ID_ADD)
        tool = self._toolbar.AddTool(wx.ID_EDIT, "Редактировать свойство", get_icon("edit"))
        tool.Enable(False)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_item_activated, id=wx.ID_EDIT)
        tool = self._toolbar.AddTool(wx.ID_DELETE, "Удалить свойство", get_icon("delete"))
        tool.Enable(False)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_delete, id=wx.ID_DELETE)
        self._toolbar.Realize()
        main_sizer.Add(self._toolbar, 0, wx.EXPAND)

        self.table = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_SORT_ASCENDING)
        self.table.AppendColumn("Класс", width=200)
        self.table.AppendColumn("Название", width=400)
        self.table.AppendColumn("Комментарий", width=100)
        self.table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated)
        self.table.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selection_changed)
        self.table.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_selection_changed)
        self.table.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_item_menu)
        self.table.Bind(wx.EVT_RIGHT_DOWN, self._on_whitespace_right_click)
        listmix.ColumnSorterMixin.__init__(self, 3)
        main_sizer.Add(self.table, 1, wx.EXPAND)

        self.SetSizer(main_sizer)
        self.Layout()

        self._properties = {}
        self.itemDataMap = {}

        self._q = ""

        self.load()

    def GetListCtrl(self):
        return self.table

    def _update_controls_state(self):
        self._toolbar.EnableTool(wx.ID_EDIT, self.table.GetSelectedItemCount() > 0)
        self._toolbar.EnableTool(wx.ID_DELETE, self.table.GetSelectedItemCount() > 0)

    @db_session
    def load(self):
        self.table.DeleteAllItems()

        self._properties = {}
        self.itemDataMap = {}

        for index, o in enumerate(select(o for o in PmProperty)):
            self._properties[o.RID] = o
            item = self.table.InsertItem(index, o.pm_property_class.Name)
            self.table.SetItem(item, 1, o.Name)
            self.table.SetItem(item, 2, o.Comment if o.Comment != None else "")
            self.table.SetItemData(item, o.RID)
            self.itemDataMap[o.RID] = [o.pm_property_class.Name, o.Name, o.Comment]

        self._update_controls_state()

    def _on_selection_changed(self, event):
        self._update_controls_state()

    def _on_item_menu(self, event):
        menu = wx.Menu()
        item = menu.Append(wx.ID_EDIT, "Изменить")
        item.SetBitmap(get_icon("edit"))
        menu.Bind(wx.EVT_MENU, self._on_item_activated, item)
        item = menu.Append(wx.ID_DELETE, "Удалить")
        menu.Bind(wx.EVT_MENU, self._on_delete, item)
        item.SetBitmap(get_icon("delete"))
        self.PopupMenu(menu, event.GetPoint())

    @db_session
    def _on_delete(self, event):
        _id = self.table.GetItemData(self.table.GetFirstSelected())
        o = select(o for o in PmProperty if o.RID == _id).first()
        if o != None:
            if delete_object(o):
                self.load()

    def _on_whitespace_right_click(self, event):
        index, flags = self.table.HitTest(event.GetPosition())
        if index == -1:
            menu = wx.Menu()
            item = menu.Append(wx.ID_ADD, "Добавить свойство")
            item.SetBitmap(get_icon("file-add"))
            menu.Bind(wx.EVT_MENU, self._on_create, item)
            self.PopupMenu(menu, event.GetPosition())
        else:
            event.Skip()

    def _on_create(self, event):
        dlg = PmPropertyEditor(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.load()

    def _on_item_activated(self, event):
        index = self.table.GetFirstSelected()
        _id = self.table.GetItemData(index)

        dlg = PmPropertyEditor(self, self._properties[_id], _type="UPDATE")
        if dlg.ShowModal() == wx.ID_OK:
            self.load()
