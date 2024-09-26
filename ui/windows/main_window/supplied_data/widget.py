import wx

from ui.class_config_provider import ClassConfigProvider
from ui.widgets.supplied_data.widget import SuppliedDataWidget
from database import *

__CONFIG_VERSION__ = 1

class SuppliedData(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)
        self.sd = SuppliedDataWidget(self)
        main_sizer.Add(self.sd, 1, wx.EXPAND)
        self.Layout()


    def get_pane_info(self) -> str | None:
        return self._config_provider['aui_pane_info']
    
    def save_pane_info(self, info: str):
        self._config_provider['aui_pane_info'] = info
        self._config_provider.flush()

    def start(self, o):
        if isinstance(o, MineObject):
            _type = "MINE_OBJECT"
        elif isinstance(o, Station):
            _type = "STATION"
        elif isinstance(o, BoreHole):
            _type = "BOREHOLE"
        elif isinstance(o, OrigSampleSet):
            _type = "ORIG_SAMPLE_SET"
        elif isinstance(o, RockBurst):
            _type = "ROCK_BURST"
        else:
            self.sd.end()
            return
        self.sd.start(o, _type)

    def end(self):
        self.sd.end()