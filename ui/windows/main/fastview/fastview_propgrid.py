import wx
import wx.propgrid


class FastviewPropgrid(wx.propgrid.PropertyGridManager):
    def __init__(self, parent):
        super().__init__(parent, style=wx.propgrid.PG_SPLITTER_AUTO_CENTER | wx.propgrid.PG_TOOLBAR)
        self.AddPage("Параметры")

    def start(self, fields): ...

    def stop(self): ...
