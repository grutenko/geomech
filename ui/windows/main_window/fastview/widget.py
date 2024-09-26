import wx

from ui.class_config_provider import ClassConfigProvider

__CONFIG_VERSION__ = 1

class FastView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

    def get_pane_info(self) -> str | None:
        return self._config_provider['aui_pane_info']
    
    def save_pane_info(self, info: str):
        self._config_provider['aui_pane_info'] = info
        self._config_provider.flush()

    def start(self, identity):
        ...

    def stop():
        ...