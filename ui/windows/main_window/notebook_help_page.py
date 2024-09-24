import wx
import wx.html

from .notebook import NotebookPage

class HelpPage(NotebookPage):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.html_view = wx.html.HtmlWindow(self)
        main_sizer.Add(self.html_view, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()

    def get_title(self) -> str:
        return "Начало работы"
    
    def get_font_color(self) -> wx.Font:
        return wx.Colour(25, 25, 25)
    
    def on_close(self) -> bool:
        return True