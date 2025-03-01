import wx

from ui.icon import get_icon
from ui.widgets.tree import EVT_WIDGET_TREE_SEL_CHANGED
from .tree import PmTestSeriesTree
from .menu import MainMenu
from .actions import ID_ADD_PM_SAMPLE_SET, ID_ADD_PM_SAMPLE, ID_ADD_ORIG_SAMPLE_SET
from .toolbar import MainToolBar, EVT_PM_TEST_SERIES_MANAGE, EVT_PM_TEST_SERIES_SELECT
from .orig_sample_set_list import OrigSampleSetList
from .pm_properties_tab import PmPropertiesTab
from .pm_test_series_manage import PmTestSeriesManage
from .fastview import FastView
from pony.orm import db_session, select
from database import PMTestSeries, PMSample
from ui.class_config_provider import ClassConfigProvider

__CONFIG_VERSION__ = 1


class MainWindow(wx.Frame):
    def __init__(self, config):
        self.config = config
        super().__init__(None, title="Геомеханика: редактор ФМС", size=wx.Size(1280, 720))
        self.SetIcon(wx.Icon(get_icon("logo")))
        self.CenterOnScreen()
        self.config = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)
        self.menu = MainMenu()
        self.SetMenuBar(self.menu)
        self.toolbar = MainToolBar(self)
        self.SetToolBar(self.toolbar)
        self.statusbar = wx.StatusBar(self)
        self.statusbar.SetFieldsCount(6)
        self.SetStatusBar(self.statusbar)
        sz = wx.BoxSizer(wx.VERTICAL)
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetSashGravity(0)
        self.splitter.SetMinimumPaneSize(300)
        left = wx.SplitterWindow(self.splitter, style=wx.SP_LIVE_UPDATE)
        self.notebook = wx.Notebook(left, style=wx.NB_LEFT)
        p = wx.Panel(self.notebook)
        p_main_sz = wx.BoxSizer(wx.VERTICAL)
        p_sz = wx.BoxSizer(wx.VERTICAL)
        self.tree = PmTestSeriesTree(p)
        p_sz.Add(self.tree, 1, wx.EXPAND)
        p_main_sz.Add(p_sz, 1, wx.EXPAND)
        p.SetSizer(p_main_sz)
        self.notebook.AddPage(p, "Пробы")
        self.fastview = FastView(left)
        left.SplitHorizontally(self.notebook, self.fastview, 300)
        left.SetSashGravity(0.5)
        left.SetMinimumPaneSize(250)
        self.orig_sample_set_list = OrigSampleSetList(self.notebook)
        self.notebook.AddPage(self.orig_sample_set_list, "Наборы образцов")
        self.pm_properties_tab = PmPropertiesTab(self.splitter)
        self.splitter.SplitVertically(left, self.pm_properties_tab, 300)
        sz.Add(self.splitter, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(sz)
        self.Layout()
        self.Show()
        self.load()

        self.pm_test_series: PMTestSeries = None
        self.bind_all()
        self.update_controls_state()

    def bind_all(self):
        self.tree.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self.on_selection_changed)
        self.orig_sample_set_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_selection_changed)
        self.orig_sample_set_list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.on_selection_changed)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_selection_changed)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_delete, id=wx.ID_DELETE)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_add_sample_set, id=ID_ADD_PM_SAMPLE_SET)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_add_sample, id=ID_ADD_PM_SAMPLE)
        self.toolbar.Bind(wx.EVT_TOOL, self.on_add_orig_sample_set, id=ID_ADD_ORIG_SAMPLE_SET)
        self.toolbar.Bind(EVT_PM_TEST_SERIES_MANAGE, self.on_pm_test_series_manage)
        self.toolbar.Bind(EVT_PM_TEST_SERIES_SELECT, self.on_pm_test_series_select)

    def on_selection_changed(self, event):
        o = None
        if self.notebook.GetSelection() == 0:
            if self.tree.get_current_node() is not None:
                o = self.tree.get_current_node().o
            else:
                o = None
        elif self.notebook.GetSelection() == 1:
            o = self.orig_sample_set_list.get_selected_orig_sample_set()
        self.fastview.start(o)
        if o is not None:
            self.statusbar.SetStatusText(o.get_tree_name(), 0)
        else:
            self.statusbar.SetStatusText("", 0)
        if isinstance(o, PMSample):
            self.pm_properties_tab.set_pm_sample(o)
        else:
            self.pm_properties_tab.end()
        self.on_controls_state_changed(event)

    def on_add_orig_sample_set(self, event):
        self.orig_sample_set_list.on_create()

    def on_sample_set_activate(self, event): ...

    def on_add_sample_set(self, event):
        self.tree.on_add_sample_set()

    def on_add_sample(self, event):
        self.tree.on_add_sample()

    def on_delete(self, event):
        if self.notebook.GetSelection() == 0:
            self.tree.delete()
        else:
            self.orig_sample_set_list.delete()
        self.update_controls_state()

    def on_controls_state_changed(self, event):
        self.update_controls_state()

    @db_session
    def on_pm_test_series_manage(self, event):
        dlg = PmTestSeriesManage(self)
        dlg.ShowModal()
        if self.pm_test_series is not None and select(o for o in PMTestSeries if o.RID == self.pm_test_series.RID).count() == 0:
            self.pm_test_series = None
            self.tree.set_pm_test_series(self.pm_test_series)
        self.update_controls_state()

    def on_pm_test_series_select(self, event):
        self.pm_test_series = event.pm_test_series
        self.tree.set_pm_test_series(self.pm_test_series)
        self.on_selection_changed(event)
        self.update_controls_state()

    @db_session
    def load(self): ...

    def update_controls_state(self):
        if self.pm_test_series is None:
            self.toolbar.pm_test_series_tool.SetLabel("Выбрать договор")
        else:
            self.toolbar.pm_test_series_tool.SetLabel("Договор: %s" % self.pm_test_series.Name)
        self.tree.Enable(self.pm_test_series is not None)
        self.toolbar.EnableTool(ID_ADD_PM_SAMPLE_SET, self.notebook.GetSelection() == 0 and self.pm_test_series is not None)
        self.toolbar.EnableTool(
            ID_ADD_PM_SAMPLE, self.notebook.GetSelection() == 0 and self.pm_test_series is not None and self.tree.can_add_pm_sample()
        )
        self.toolbar.EnableTool(ID_ADD_ORIG_SAMPLE_SET, self.notebook.GetSelection() == 1)
        self.toolbar.EnableTool(
            wx.ID_DELETE,
            (self.notebook.GetSelection() == 0 and self.pm_test_series is not None and self.tree.get_current_node() is not None)
            or self.notebook.GetSelection() == 1
            and self.orig_sample_set_list.GetSelectedItemCount() > 0,
        )
        self.toolbar.Realize()
