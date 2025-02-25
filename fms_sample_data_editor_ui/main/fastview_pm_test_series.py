import wx
import wx.propgrid


class FastviewPmTestSeries(wx.propgrid.PropertyGrid):
    def __init__(self, parent):
        super().__init__(parent, style=wx.propgrid.PG_SPLITTER_AUTO_CENTER | wx.propgrid.PG_TOOLBAR)
        self.Hide()

    def start(self, o):
        self.Show()
