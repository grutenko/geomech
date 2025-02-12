import wx


class PreventActionDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.SetTitle("Добавить типовое мероприятие")

        sz = wx.BoxSizer(wx.VERTICAL)
        main_sz = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Название")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_name = wx.TextCtrl(self)
        main_sz.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)
        label = wx.StaticText(self, label="Комментарий")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_comment = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        main_sz.Add(self.field_comment, 0, wx.EXPAND)
        sz.Add(main_sz, 1, wx.EXPAND | wx.ALL, border=10)

        line = wx.StaticLine(self)
        sz.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        self.btn_save = wx.Button(self, label="Добавить")
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        sz.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, border=10)

        self.SetSizer(sz)
        self.Layout()

    def on_save(self, event): ...
