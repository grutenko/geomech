import wx

from ui.widgets.grid import GridEditorFrame, IconsOptions
from ui.icon import get_art

class BaseGrid(GridEditorFrame):
    def __init__(self, parent, *args, **kwds):
        icons = IconsOptions(
            save=get_art(wx.ART_FILE_SAVE, scale_to=16),
            copy=get_art(wx.ART_COPY, scale_to=16),
            cut=get_art(wx.ART_CUT, scale_to=16),
            insert=get_art(wx.ART_PLUS, scale_to=16),
            cancel=get_art(wx.ART_UNDO, scale_to=16),
            back=get_art(wx.ART_REDO, scale_to=16),
            add_row=get_art(wx.ART_PLUS, scale_to=16),
            delete_row=get_art(wx.ART_DELETE, scale_to=16),
            up=get_art(wx.ART_GO_UP, scale_to=16),
            down=get_art(wx.ART_GO_DOWN, scale_to=16),
            write_text=get_art(wx.ART_EDIT, scale_to=16)
        )
        super().__init__(parent, icons=icons)