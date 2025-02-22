import wx

from ui.icon import get_icon
from .tree import PmTestSeriesTree
from .menu import MainMenu
from .toolbar import MainToolBar
from .orig_sample_set_list import OrigSampleSetList
from pony.orm import db_session, select
from database import PMTestSeries
from ui.class_config_provider import ClassConfigProvider

__CONFIG_VERSION__ = 1


class MainWindow(wx.Frame):
    def __init__(self, config):
        self.config = config
        super().__init__(None, title="Геомеханика: редактор ФМС", size=wx.Size(1280, 720))
        self.SetIcon(wx.Icon(get_icon('logo')))
        self.CenterOnScreen()
        self.config = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)
        self.menu = MainMenu()
        self.SetMenuBar(self.menu)
        self.toolbar = MainToolBar(self)
        self.SetToolBar(self.toolbar)
        sz = wx.BoxSizer(wx.VERTICAL)
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetSashGravity(0)
        self.splitter.SetMinimumPaneSize(300)
        self.notebook = wx.Notebook(self.splitter, style=wx.NB_LEFT)
        p = wx.Panel(self.notebook)
        p_main_sz = wx.BoxSizer(wx.VERTICAL)
        p_sz = wx.BoxSizer(wx.VERTICAL)
        self.tree = PmTestSeriesTree(p)
        p_sz.Add(self.tree, 1, wx.EXPAND)
        p_main_sz.Add(p_sz, 1, wx.EXPAND | wx.ALL, border=10)
        p.SetSizer(p_main_sz)
        self.notebook.AddPage(p, "Пробы")
        self.orig_sample_set_list = OrigSampleSetList(self.notebook)
        self.notebook.AddPage(self.orig_sample_set_list, "Наборы образцов")
        self.deputy = wx.Panel(self.splitter)
        self.splitter.SplitVertically(self.notebook, self.deputy, 300)
        sz.Add(self.splitter, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(sz)
        self.Layout()
        self.Show()
        self.load()
    
    @db_session
    def load(self):
        ...