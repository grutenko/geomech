import wx

from ui.icon import get_icon
from ui.validators import TextValidator


class PmSampleDialog(wx.Dialog):
    def __init__(self, parent, pm_sample_set=None, o=None):
        super().__init__(parent, title="Добавить образец", size=wx.Size(300, 400))
        self.SetIcon(wx.Icon(get_icon("logo")))
        self.CenterOnScreen()
        self.pm_sample_set = pm_sample_set

        sz = wx.BoxSizer(wx.VERTICAL)
        main_sz = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Название")
        main_sz.Add(label, 0)
        self.field_name = wx.TextCtrl(self, size=wx.Size(250, -1))
        self.field_name.SetValidator(TextValidator(lenMin=1, lenMax=256))
        main_sz.Add(self.field_name, 0, wx.EXPAND | wx.BOTTOM, border=10)
        sz.Add(main_sz, 1, wx.EXPAND | wx.ALL, border=10)

        line = wx.StaticLine(self)
        main_sz.Add(line, 0, wx.EXPAND | wx.TOP, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        self.btn_save = wx.Button(self, label="Создать")
        self.btn_save.Bind(wx.EVT_BUTTON, self.on_save)
        self.btn_save.SetDefault()
        btn_sizer.Add(self.btn_save, 0)
        sz.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, border=10)
        self.SetSizer(sz)
        self.Layout()

    def on_save(self, event): ...
