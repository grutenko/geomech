import wx

from ui.class_config_provider import ClassConfigProvider

__CONFIG_VERSION__ = 1

class RbPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._select_box = wx.ComboBox(self)
        main_sizer.Add(self._select_box, 0, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()