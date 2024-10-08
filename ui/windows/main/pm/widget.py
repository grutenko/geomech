import wx
import wx.lib.newevent

from ui.class_config_provider import ClassConfigProvider
from ui.icon import get_art, get_icon
from .list import PmList
from .create import DialogCreatePmSeries

__CONFIG_VERSION__ = 2

PmSelectedEvent, EVT_PM_SELECTED = wx.lib.newevent.NewEvent()

class PmPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

        self._current_rid = None

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        item = self.toolbar.AddTool(
            wx.ID_BACKWARD, label="Назад", bitmap=get_icon('undo')
        )
        item.Enable(False)
        self.toolbar.AddSeparator()
        item = self.toolbar.AddTool(wx.ID_ADD, "Добавить", get_icon("magic-wand"))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        item = self.toolbar.AddTool(wx.ID_EDIT, "Изменить", get_icon('edit'))
        item.Enable(False)
        item = self.toolbar.AddTool(wx.ID_DELETE, "Удалить", get_icon('delete'))
        item.Enable(False)
        self.toolbar.AddStretchableSpace()
        item = self.toolbar.AddCheckTool(wx.ID_FIND, "", get_icon('find'))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_back, id=wx.ID_BACKWARD)
        self.toolbar.Realize()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(top_sizer, 0, wx.EXPAND | wx.BOTTOM, border=2)
        self.SetSizer(main_sizer)

        self._details = None
        self._list = PmList(self)
        main_sizer.Add(self._list, 1, wx.EXPAND)

        self.Layout()

    def _on_add(self, event):
        dlg = DialogCreatePmSeries(self)
        dlg.ShowModal()

    def _on_back(self, event):
        ...

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()

    def remove_selection(self):
        self._list.remove_selection()