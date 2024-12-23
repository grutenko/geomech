import wx

from ui.icon import get_icon


class RecordEditor(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Добавить свойство", size=wx.Size(300, 200))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()
        self.Layout()

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(sizer)
        self.Layout()


class GridSamplePropertiesDialog(wx.Dialog):
    def __init__(self, parent, initial_records, on_prop_add, on_prop_remove):
        super().__init__(parent, title="Настроить свойства", size=wx.Size(400, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()

        self._initial_records = initial_records
        self._h_on_prop_add = on_prop_add
        self._h_on_prop_remove = on_prop_remove

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_HORZ_TEXT)
        item = self.toolbar.AddTool(wx.ID_ADD, "Добавить", get_icon("file-add"))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_create, id=wx.ID_ADD)
        self.toolbar.AddSeparator()
        item = self.toolbar.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        item.Enable(False)
        self.toolbar.Realize()
        sizer.Add(self.toolbar, 0, wx.EXPAND)

        self.list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self.list.AppendColumn("Название", width=150)
        self.list.AppendColumn("Метод испытаний", width=200)
        self.list.AppendColumn("Оборудование", width=200)
        sizer.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(sizer)

        self.Layout()

    def _on_create(self, event):
        dlg = RecordEditor(self)
        dlg.ShowModal()

    def _on_delete(self, event): ...
