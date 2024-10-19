import wx

from ui.icon import get_icon


class MethodAddDialog(wx.Dialog):
    def __init__(self, parent, pm_test_series):
        super().__init__(parent, title="Добавить испытания по методу", size=wx.Size(400, 200))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnScreen()
