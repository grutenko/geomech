import wx

from ui.icon import get_art, get_icon
from .list import RbList
from ui.class_config_provider import ClassConfigProvider

from .create import DialogCreateRockBurst

__CONFIG_VERSION__ = 1

class RbPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        item = self.toolbar.AddTool(
            wx.ID_ADD, "Добавить", get_icon("magic-wand")
        )
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        item = self.toolbar.AddTool(
            wx.ID_EDIT, "Изменить", get_art(wx.ART_EDIT)
        )
        item.Enable(False)
        item = self.toolbar.AddTool(
            wx.ID_DELETE, "Удалить", get_icon('delete')
        )
        item.Enable(False)
        self.toolbar.AddStretchableSpace()
        item = self.toolbar.AddCheckTool(
            wx.ID_FIND, "", get_icon('find')
        )
        self.toolbar.Realize()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)
        self._list = RbList(self)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()

    def _on_add(self, event):
        dlg = DialogCreateRockBurst(self)
        dlg.ShowModal()

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()