import wx

from ui.windows.main.pm.create import DialogCreatePmSeries
from ui.icon import get_icon
from pony.orm import db_session, select
from database import PMTestSeries
from ui.delete_object import delete_object

class PmTestSeriesManage(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Договоры", size=wx.Size(500, 300))
        self.CenterOnScreen()
        sz = wx.BoxSizer(wx.VERTICAL)
        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_HORZ_TEXT)
        self.toolbar.AddTool(wx.ID_ADD, "Добавить", get_icon("file-add"))
        self.toolbar.AddTool(wx.ID_EDIT, "Изменить", get_icon("edit"))
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        self.toolbar.EnableTool(wx.ID_EDIT, False)
        self.toolbar.EnableTool(wx.ID_DELETE, False)
        self.toolbar.Realize()
        sz.Add(self.toolbar, 0, wx.EXPAND)
        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.list.AppendColumn("Название", width=150)
        self.list.AppendColumn("Документ №", width=100)
        self.list.AppendColumn("Кол.во проб", width=80)
        sz.Add(self.list, 1, wx.EXPAND)
        self.SetSizer(sz)
        self.Layout()
        self.items = []
        self.bind_all()
        self.load()

    def bind_all(self):
        self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selection_changed)
        self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_selection_changed)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_add, id=wx.ID_ADD)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_delete, id=wx.ID_DELETE)

    def on_delete(self, event):
        o = self.items[self.list.GetFirstSelected()]
        if delete_object(o, ["pm_sample_sets"]):
            self.load()
            self.update_controls_state()

    def on_selection_changed(self, event):
        self.update_controls_state()

    @db_session
    def load(self):
        self.list.DeleteAllItems()
        self.items = []
        for index, o in enumerate(select(o for o in PMTestSeries)):
            self.list.InsertItem(index, o.Name)
            self.list.SetItem(index, 1, o.foundation_document.Name)
            self.list.SetItem(index, 2, str(len(o.pm_sample_sets)))
            self.items.append(o)

    def on_add(self, event):
        dlg = DialogCreatePmSeries(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.load()
            self.update_controls_state()

    def update_controls_state(self):
        self.toolbar.EnableTool(wx.ID_EDIT, self.list.GetSelectedItemCount() > 0)
        self.toolbar.EnableTool(wx.ID_DELETE, self.list.GetSelectedItemCount() > 0)
