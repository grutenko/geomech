import wx

from ui.icon import get_icon
from .types_dialog import TypesDialog
from pony.orm import db_session, select
from database import RBType
from ui.delete_object import delete_object


class TypesPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self.items = []
        sz = wx.BoxSizer(wx.VERTICAL)
        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_HORZ_TEXT)
        self.toolbar.AddTool(wx.ID_ADD, "Добавить тип", get_icon("file-add"))
        self.toolbar.Bind(wx.EVT_TOOL, self.on_create, id=wx.ID_ADD)
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(wx.ID_EDIT, "Изменить", get_icon("edit"))
        self.toolbar.Bind(wx.EVT_TOOL, self.on_edit, id=wx.ID_EDIT)
        self.toolbar.EnableTool(wx.ID_EDIT, False)
        self.toolbar.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        self.toolbar.Bind(wx.EVT_TOOL, self.on_delete, id=wx.ID_DELETE)
        self.toolbar.EnableTool(wx.ID_DELETE, False)
        sz.Add(self.toolbar, 0, wx.EXPAND)
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.list.AppendColumn("Название", width=150)
        self.list.AppendColumn("Комментарий", width=250)
        sz.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(sz)
        self.Layout()
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selection_changed)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_selection_changed)
        self.load()

    def on_create(self, event):
        dlg = TypesDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.load()

    def on_edit(self, event):
        dlg = TypesDialog(self)
        dlg.ShowModal()

    def on_delete(self, event):
        o = self.items[self.list.GetFirstSelected()]
        if delete_object(o, ["rock_bursts"]):
            self.load()

    @db_session
    def load(self):
        self.list.DeleteAllItems()
        self.items = []
        for index, o in enumerate(select(o for o in RBType)):
            self.items.append(o)
            self.list.InsertItem(index, o.Name)
            self.list.SetItem(index, 1, o.Comment if o.Comment != None else "")

    def on_selection_changed(self, event):
        self.update_controls_state()

    def update_controls_state(self):
        self.toolbar.EnableTool(wx.ID_EDIT, self.list.GetSelectedItemCount() > 0)
        self.toolbar.EnableTool(wx.ID_DELETE, self.list.GetSelectedItemCount() > 0)
