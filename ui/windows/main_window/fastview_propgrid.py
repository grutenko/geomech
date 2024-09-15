import wx
import wx.propgrid

class FastviewPropgrid(wx.propgrid.PropertyGrid):
    def __init__(self, parent):
        super().__init__(parent, style=wx.propgrid.PG_DEFAULT_STYLE | wx.propgrid.PG_SPLITTER_AUTO_CENTER)

    def start(self, fields):
        ... 

    def stop(self):
        ...