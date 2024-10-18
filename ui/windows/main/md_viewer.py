import wx

from ui.resourcelocation import resource_path
from ui.widgets.md.wxmarkdown import *

from .notebook.widget import BasicEditor


class MdViewer(BasicEditor):
    def __init__(self, notebook, title="Редактор", identity=None):
        super().__init__(notebook, title, identity)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.viewer = Markdown(self)
        main_sizer.Add(self.viewer, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

    def set_file(self, filename):
        with open(resource_path("md/" + filename), "r") as f:
            self.viewer.AddContent(f.read())
