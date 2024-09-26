import wx
import wx.html

from ui.windows.main_window.identity import Identity
from .widget import BasicEditor

class HelpPage(BasicEditor):
    def __init__(self, parent):
        super().__init__(parent, "Начало работы")

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.viewer = wx.html.HtmlWindow(self)
        main_sizer.Add(self.viewer, 1, wx.EXPAND)
        with open("html/help_page.html", 'r') as f:
            data = f.read().encode('WINDOWS-1251')
        self.viewer.SetPage(data)

        self.SetSizer(main_sizer)
        self.Layout()

    def get_identity(self) -> Identity | None:
        return "help_page"
    
    def is_read_only(self) -> bool:
        return True