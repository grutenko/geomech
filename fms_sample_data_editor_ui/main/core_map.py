import wx
from wx.lib.agw.flatnotebook import FNB_X_ON_TAB, FNB_VC71, FNB_NO_NAV_BUTTONS, FNB_NO_X_BUTTON, FlatNotebook
import cairo
import math


class CoreMap(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        sz = wx.BoxSizer(wx.VERTICAL)
        self.notebook = FlatNotebook(
            self,
            agwStyle=FNB_X_ON_TAB | FNB_VC71 | FNB_NO_X_BUTTON | FNB_NO_NAV_BUTTONS,
        )
        self.canvas = wx.ScrolledWindow(self.notebook, style=wx.VERTICAL)
        self.canvas.SetScrollRate(11, 11)
        self.notebook.AddPage(self.canvas, "Схема керна")
        sz.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(sz)
        self.Layout()
        self.canvas.Bind(wx.EVT_PAINT, self.on_paint)
        self.SetVirtualSize(-1, 10 * 90 * 100)

    def on_paint(self, event): ...
