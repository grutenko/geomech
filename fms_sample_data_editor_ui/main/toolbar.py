import wx
import wx.lib.newevent
from .actions import ID_TEST_SERIES, ID_ADD_PM_SAMPLE_SET, ID_ADD_PM_SAMPLE
from ui.icon import get_icon
from pony.orm import select, db_session
from database import PMTestSeries

PmTestSeriesSelect, EVT_PM_TEST_SERIES_SELECT = wx.lib.newevent.NewEvent()
PmTestSeriesAdd, EVT_PM_TEST_SERIES_ADD = wx.lib.newevent.NewEvent()


class MainToolBar(wx.ToolBar):
    @db_session
    def __init__(self, parent):
        super().__init__(parent, style=wx.TB_FLAT | wx.TB_HORZ_TEXT)
        self.pm_test_series = None
        self.pm_test_series_tool = self.AddTool(ID_TEST_SERIES, "Выбрать договор", get_icon("read"), kind=wx.ITEM_DROPDOWN)
        self.AddTool(ID_ADD_PM_SAMPLE_SET, "Добавить пробу", get_icon("file-add"))
        self.AddTool(ID_ADD_PM_SAMPLE, "Добавить образец", get_icon("file-add"))
        self.EnableTool(ID_ADD_PM_SAMPLE_SET, False)
        self.EnableTool(ID_ADD_PM_SAMPLE, False)
        self.AddSeparator()
        self.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        self.EnableTool(wx.ID_DELETE, False)
        self.Bind(wx.EVT_TOOL_DROPDOWN, self.on_dropdown, id=ID_TEST_SERIES)
        self.Bind(wx.EVT_TOOL, self.on_dropdown, id=ID_TEST_SERIES)
        self.Realize()
        self.pm_test_series = []

    @db_session
    def on_dropdown(self, event):
        m = wx.Menu()
        i = m.Append(wx.ID_ADD, "Добавить договор")
        i.SetBitmap(get_icon("file-add"))
        m.AppendSeparator()
        self.pm_test_series = []
        for index, o in enumerate(select(o for o in PMTestSeries)):
            i = m.Append(index + 1, o.Name)
            i.SetBitmap(get_icon("read"))
            self.pm_test_series.append(o)
        m.Bind(wx.EVT_MENU, self.on_pm_test_series_menu)
        rect = self.GetClientRect()
        self.PopupMenu(m, rect.GetX(), rect.GetY() + rect.GetHeight())

    def on_pm_test_series_menu(self, event):
        if event.Id == wx.ID_ADD:
            wx.PostEvent(self, PmTestSeriesAdd())
        else:
            pm_test_series = self.pm_test_series[event.Id - 1]
            wx.PostEvent(self, PmTestSeriesSelect(pm_test_series=pm_test_series))
