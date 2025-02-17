import wx

from ui.icon import get_icon
from .causes_page import CausesPage
from .prevent_actions import PreventActionsPage
from .signs_page import SignsPage
from .types_page import TypesPage


class RockBursrsProperties(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        self.SetSize(800, 350)
        self.SetMinSize(wx.Size(400, 200))
        self.SetTitle("Параметры горных ударов")
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()

        sz = wx.BoxSizer(wx.VERTICAL)
        self.notebook = wx.Notebook(self)

        self.types_page = TypesPage(self.notebook)
        self.notebook.AddPage(self.types_page, "ТИпы событий")

        self.causes_page = CausesPage(self.notebook)
        self.notebook.AddPage(self.causes_page, "Типовые причины")

        self.signs_page = SignsPage(self.notebook)
        self.notebook.AddPage(self.signs_page, "Типовые признаки")

        self.prevent_actions_page = PreventActionsPage(self.notebook)
        self.notebook.AddPage(self.prevent_actions_page, "Типовые мероприятия")

        sz.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(sz)
        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _on_close(self, event):
        self.Hide()
