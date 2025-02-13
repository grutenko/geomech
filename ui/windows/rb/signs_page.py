import wx

from ui.icon import get_icon
from .sign_dialog import SignDialog
from database import RBTypicalSign
from pony.orm import select, db_session
from pubsub.pub import sendMessage
from ui.delete_object import delete_object


class SignsPage(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        sz = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_HORZ_TEXT)
        self.toolbar.AddTool(wx.ID_ADD, "Добавить признак", get_icon("file-add"))
        self.toolbar.Bind(wx.EVT_TOOL, self.on_add, id=wx.ID_ADD)
        self.toolbar.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        self.toolbar.Bind(wx.EVT_TOOL, self.on_delete, id=wx.ID_DELETE)
        self.toolbar.EnableTool(wx.ID_DELETE, False)
        self.toolbar.Realize()
        sz.Add(self.toolbar, 0, wx.EXPAND)
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.list.AppendColumn("Название", width=200)
        self.list.AppendColumn("Комментарий", width=500)
        self.list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_item_menu)
        self.list.Bind(wx.EVT_RIGHT_DOWN, self.on_whitespace_right_click)
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selection_changed)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_selection_changed)
        sz.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(sz)
        self.Layout()
        self.load()

    @db_session
    def load(self):
        self.list.DeleteAllItems()
        self.signs = []
        for index, sign in enumerate(select(o for o in RBTypicalSign)):
            self.signs.append(sign)
            self.list.InsertItem(index, sign.Name)
            self.list.SetItem(index, 1, sign.Comment)

    def on_selection_changed(self, event):
        self.update_controls_state()

    def on_add(self, event):
        dlg = SignDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.load()
            self.update_controls_state()
            sendMessage("object.added", o=dlg.o)

    def on_delete(self, event):
        o = self.signs[self.list.GetFirstSelected()]
        if delete_object(o, ["rb_signs"]):
            self.load()
            self.update_controls_state()

    def on_item_menu(self, event): ...

    def on_whitespace_right_click(self, event):
        m = wx.Menu()
        i = m.Append(wx.ID_ADD, "Добавить")
        m.Bind(wx.EVT_MENU, self.on_add, i)
        i.SetBitmap(get_icon("file-add"))
        self.PopupMenu(m, event.GetPosition())

    def update_controls_state(self):
        self.toolbar.EnableTool(wx.ID_DELETE, self.list.GetSelectedItemCount() > 0)
