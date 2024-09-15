import wx

from ui.widgets.grid import *
from ui.widgets.grid.icons_options import IconsOptions

class DischargeMeasurementsEditor(GridEditorFrame):
    def __init__(self, *args, icons: IconsOptions = ..., **kwds):
        super().__init__(*args, icons=icons, **kwds)