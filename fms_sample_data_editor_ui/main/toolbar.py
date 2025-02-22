import wx
from .actions import ID_TEST_SERIES, ID_ADD_PM_SAMPLE_SET, ID_ADD_PM_SAMPLE
from ui.icon import get_icon
from pony.orm import select, db_session
from database import PMTestSeries

class MainToolBar(wx.ToolBar):
    @db_session
    def __init__(self, parent):
        super().__init__(parent, style=wx.TB_FLAT | wx.TB_HORZ_TEXT)
        self.pm_test_series = None
        self.pm_test_series_tool = self.AddTool(ID_TEST_SERIES, "Выбрать договор", get_icon("read"), kind=wx.ITEM_DROPDOWN)
        self.AddTool(ID_ADD_PM_SAMPLE_SET, "Добавить пробу", get_icon("file-add"))
        self.AddTool(ID_ADD_PM_SAMPLE, "Добавить образец", get_icon("file-add"))
        self.EnableTool(ID_ADD_PM_SAMPLE, False)
        self.AddSeparator()
        self.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        self.EnableTool(wx.ID_DELETE, False)
        self.Bind(wx.EVT_TOOL_DROPDOWN, self.on_dropdown)
        self.Realize()
        self.load()
        
    @db_session
    def load(self):
        ...
        
    def on_dropdown(self, event):
        ...
        
    def update_controls_state(self):
        if self.pm_test_series == None:
            self.pm_test_series_tool.SetLabel("Выбрать договор")
        else:
            self.pm_test_series_tool.SetLabel(self.pm_test_series.Name)
        self.Realize()