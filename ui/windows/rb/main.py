import wx

from ui.icon import get_icon


class RockBursrsProperties(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        self.SetSize(800, 350)
        self.SetMinSize(wx.Size(400, 200))
        self.SetTitle("Параметры горных ударов")
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()

        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _on_close(self, event):
        self.Hide()
