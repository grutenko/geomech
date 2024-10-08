import wx
import wx.html

from ui.resourcelocation import resource_path
from ui.windows.main.identity import Identity
from .widget import BasicEditor

class HelpPage(BasicEditor):
    def __init__(self, parent):
        super().__init__(parent, "Начало работы")

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.viewer = wx.html.HtmlWindow(self)
        main_sizer.Add(self.viewer, 1, wx.EXPAND)
        with open(resource_path("html/help_page.html"), 'rb') as f:
            data = f.read()
        self.viewer.SetPage(data)

        self.SetSizer(main_sizer)
        self.Layout()

    def get_identity(self) -> Identity | None:
        return "help_page"
    
    def is_read_only(self) -> bool:
        return True