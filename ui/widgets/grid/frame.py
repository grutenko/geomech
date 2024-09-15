import wx
from wx.grid import Grid

from .column import Column
from .icons_options import IconsOptions
from .model_proto import Model
from .controller import Controller
from .errors import Errors

from typing import List


class GridEditorFrame(wx.Frame):
    def __init__(self, *args, icons: IconsOptions = IconsOptions(), **kwds):
        super().__init__(*args, **kwds)

        self.menu_bar = wx.MenuBar()
        self.toolbar = wx.ToolBar(self)
        self.statusbar = wx.StatusBar(self, style=wx.STB_DEFAULT_STYLE | wx.STB_SIZEGRIP | wx.STB_SHOW_TIPS)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        main_sizer.Add(self.splitter, 1, wx.EXPAND)

        grid_panel = wx.Panel(self.splitter)
        grid_sizer = wx.BoxSizer(wx.VERTICAL)

        self.grid = Grid(grid_panel)
        self.grid.DisableDragRowSize()
        self.grid.SetSelectionBackground(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        )
        self.grid.SetRowLabelSize(30)
        self.grid.SetColLabelSize(20)
        self.grid.CreateGrid(0, 0)
        self.grid.EnableEditing(True)

        grid_sizer.Add(self.grid, 1, wx.EXPAND)
        grid_panel.SetSizer(grid_sizer)

        self.SetMenuBar(self.menu_bar)
        self.SetToolBar(self.toolbar)
        self.SetStatusBar(self.statusbar)

        errors_panel = wx.Panel(self.splitter)
        errors_sizer = wx.BoxSizer(wx.VERTICAL)
        errors_panel.SetSizer(errors_sizer)

        self.errors = Errors(errors_panel)
        errors_sizer.Add(self.errors, 1, wx.EXPAND)

        self.splitter.SplitHorizontally(grid_panel, errors_panel, -150)
        self.splitter.SetSashGravity(1)

        self.SetSizer(main_sizer)

        self.controller = None
        self.icons_options = icons

    def start(self, model: Model):
        self.controller = Controller(
            model,
            self.grid,
            self.toolbar,
            self.statusbar,
            self.menu_bar,
            self.icons_options,
        )

    def stop(self) -> bool: ...

    def stop_force(self): ...