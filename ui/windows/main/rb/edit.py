import wx

from ui.icon import get_icon

class EditRockBurst(wx.Dialog):
    def __init__(self, parent, o):
        super().__init__(parent, title="Изменить", size=wx.Size(400, 600))
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()