import wx

from ui.icon import get_icon
from .prevent_action_dialog import PreventActionDialog
from pony.orm import db_session, select
from database import RBTypicalPreventAction
from ui.delete_object import delete_object


class PreventActionsPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        sz = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_HORZ_TEXT)
        self.toolbar.AddTool(wx.ID_ADD, "Добавить мероприятие", get_icon("file-add"))
        self.toolbar.Bind(wx.EVT_TOOL, self.on_add, id=wx.ID_ADD)
        self.toolbar.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        self.toolbar.EnableTool(wx.ID_DELETE, False)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_delete, id=wx.ID_DELETE)
        self.toolbar.Realize()
        sz.Add(self.toolbar, 0, wx.EXPAND)
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.list.AppendColumn("Название", width=200)
        self.list.AppendColumn("Комментарий", width=500)
        self.list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_item_menu)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selection_changed)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_selection_changed)
        self.list.Bind(wx.EVT_RIGHT_DOWN, self.on_whitespace_right_click)
        sz.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(sz)
        self.Layout()
        self.load()

    def on_add(self, event):
        dlg = PreventActionDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.load()
            self.update_controls_state()

    def on_selection_changed(self, event):
        self.update_controls_state()

    @db_session
    def load(self):
        self.list.DeleteAllItems()
        self.items = []
        for index, o in enumerate(select(o for o in RBTypicalPreventAction)):
            self.items.append(o)
            self.list.InsertItem(index, o.Name)
            self.list.SetItem(index, 1, o.Comment)

    def update_controls_state(self):
        self.toolbar.EnableTool(wx.ID_DELETE, self.list.GetSelectedItemCount() > 0)

    def on_delete(self, event):
        o = self.items[self.list.GetFirstSelected()]
        if delete_object(o, ["rb_prevent_actions"]):
            self.load()
            self.update_controls_state()

    def on_item_menu(self, event): ...

    def on_whitespace_right_click(self, event):
        m = wx.Menu()
        i = m.Append(wx.ID_ADD, "Добавить")
        m.Bind(wx.EVT_MENU, self.on_add, i)
        i.SetBitmap(get_icon("file-add"))
        self.PopupMenu(m, event.GetPosition())
