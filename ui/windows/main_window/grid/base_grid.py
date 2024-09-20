import wx

from ui.widgets.grid import IconsOptions, ModelProto
from ui.widgets.grid.frame import Grid
from ui.widgets.grid.controller import Controller
from ui.widgets.grid.errors import Errors
from ui.icon import get_art

from ..notebook import NotebookPage, NotebookTitleChanged

class BaseGrid(NotebookPage):
    def __init__(self, parent, menubar, toolbar, statusbar, *args, **kwds):
        super().__init__(parent, *args, **kwds)
        self._title = "Вкладка"
        icons = IconsOptions(
            save=get_art(wx.ART_FILE_SAVE, scale_to=16),
            copy=get_art(wx.ART_COPY, scale_to=16),
            cut=get_art(wx.ART_CUT, scale_to=16),
            insert=get_art(wx.ART_PLUS, scale_to=16),
            cancel=get_art(wx.ART_UNDO, scale_to=16),
            back=get_art(wx.ART_REDO, scale_to=16),
            add_row=get_art(wx.ART_PLUS, scale_to=16),
            delete_row=get_art(wx.ART_CLOSE, scale_to=16),
            up=get_art(wx.ART_GO_UP, scale_to=16),
            down=get_art(wx.ART_GO_DOWN, scale_to=16),
            write_text=get_art(wx.ART_EDIT, scale_to=16)
        )
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.menubar = menubar
        self.toolbar = toolbar
        self.statusbar = statusbar

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

    def get_title(self):
        return self._title
    
    def set_title(self, title):
        wx.PostEvent(self, NotebookTitleChanged(target=self))
        self._title = title

    def start(self, model: ModelProto):
        self.controller = Controller(
            model,
            self.grid,
            self.toolbar,
            self.statusbar,
            self.menubar,
            self.icons_options,
        )

    def stop(self) -> bool:
        self.controller.detach()

    def on_close(self) -> bool:
        self.stop()
        return True
    
    def on_select(self):
        self.controller.apply_controls()

    def on_deselect(self):
        self.controller.remove_controls()