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
        self._current = None
        self.Layout()


    def get_pane_info(self) -> str | None:
        return self._config_provider['aui_pane_info']
    
    def save_pane_info(self, info: str):
        self._config_provider['aui_pane_info'] = info
        self._config_provider.flush()

    def start(self, _id):
        if _id.rel_data_target != None:
            self.sd.end()
            return
        if isinstance(_id.rel_data_o, MineObject):
            _type = "MINE_OBJECT"
        elif isinstance(_id.rel_data_o, Station):
            _type = "STATION"
        elif isinstance(_id.rel_data_o, BoreHole):
            _type = "BOREHOLE"
        elif isinstance(_id.rel_data_o, OrigSampleSet):
            _type = "ORIG_SAMPLE_SET"
        elif isinstance(_id.rel_data_o, RockBurst):
            _type = "ROCK_BURST"
        else:
            self.sd.end()
            return
        self._current = _id.rel_data_o
        self.sd.start(_id.rel_data_o, _type)

    def get_current_object(self):
        return self._current

    def end(self):
        self._current = None
        self.sd.end()