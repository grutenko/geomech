import wx
import wx.propgrid
from ui.icon import get_icon

from database import PMSample


class PmPropertiesTab(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        sz = wx.BoxSizer(wx.VERTICAL)
        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_HORZ_TEXT)
        self.toolbar.AddTool(wx.ID_ADD, "Добавить свойство", get_icon("file-add"))
        self.toolbar.AddTool(wx.ID_DELETE, "Удалить свойство", get_icon("delete"))
        self.toolbar.EnableTool(wx.ID_ADD, False)
        self.toolbar.EnableTool(wx.ID_DELETE, False)
        self.toolbar.Realize()
        sz.Add(self.toolbar, 0, wx.EXPAND)
        self.propgrid = wx.propgrid.PropertyGrid(self)
        sz.Add(self.propgrid, 1, wx.EXPAND)
        self.SetSizer(sz)
        self.Layout()
        self.pm_sample: PMSample = None

    def set_pm_sample(self, pm_sample):
        self.pm_sample = pm_sample
        self.load_properties()
        self.update_controls_state()

    def load_properties(self): ...

    def remove_properties(self): ...

    def end(self):
        self.pm_sample = None
        self.remove_properties()
        self.update_controls_state()

    def update_controls_state(self):
        self.toolbar.EnableTool(wx.ID_ADD, self.pm_sample != None)
        self.toolbar.EnableTool(wx.ID_DELETE, self.pm_sample != None)
