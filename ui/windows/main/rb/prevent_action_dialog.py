import wx

from ui.validators import DateValidator


class PreventActionDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Добавить мероприятие")
        self.SetSize(300, 250)
        self.CenterOnParent()

        sz = wx.BoxSizer(wx.VERTICAL)
        main_sz = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Типовое мероприятие")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_action = wx.Choice(self)
        main_sz.Add(self.field_action, 0, wx.EXPAND | wx.BOTTOM, border=10)
        label = wx.StaticText(self, label="Дата проведения")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_date = wx.TextCtrl(self)
        self.field_date.SetValidator(DateValidator())
        main_sz.Add(self.field_date, 0, wx.EXPAND | wx.BOTTOM, border=10)
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
