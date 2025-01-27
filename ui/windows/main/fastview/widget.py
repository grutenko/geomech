import wx

from database import *
from ui.class_config_provider import ClassConfigProvider
from ui.windows.main.identity import Identity

from .bore_hole import BoreHoleFastview
from .core import CoreFastview
from .discharge_series import DischargeSeriesFastview
from .mine_object import MineObjectFastview
from .pm_sample_set import PmSampleSetFastview
from .pm_test_series import PmTestSeriesFastview
from .rock_burst import RockBurstFastview
from .station import StationFastview

__CONFIG_VERSION__ = 2


class _deputy(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Недоступен для этого объекта")
        main_sizer.Add(label, 1, wx.EXPAND | wx.ALL, border=20)
        self.SetSizer(main_sizer)
        self.Layout()
        self.Hide()

    def start(self, o):
        self.Show()

    def end(self):
        self.Hide()


class FastView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)
        self._deputy = _deputy(self)
        self._bore_hole = BoreHoleFastview(self)
        self._core = CoreFastview(self)
        self._discharge_series = DischargeSeriesFastview(self)
        self._mine_object = MineObjectFastview(self)
        self._pm_test_series = PmTestSeriesFastview(self)
        self._rock_burst = RockBurstFastview(self)
        self._station = StationFastview(self)
        self._pm_sample_set = PmSampleSetFastview(self)

        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)
        self.statusbar = wx.StatusBar(self, style=0)
        self._sizer.Add(self.statusbar, 0, wx.EXPAND)
        self._sizer.Add(self._deputy, 1, wx.EXPAND)
        self.Layout()

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()

    def start(self, identity: Identity):
        if isinstance(identity.rel_data_o, MineObject):
            new_win = self._mine_object
        elif isinstance(identity.rel_data_o, Station):
            new_win = self._station
        elif isinstance(identity.rel_data_o, BoreHole):
            new_win = self._bore_hole
        elif isinstance(identity.rel_data_o, OrigSampleSet) and identity.rel_data_o.bore_hole != None:
            new_win = self._core
        elif isinstance(identity.rel_data_o, RockBurst):
            new_win = self._rock_burst
        elif isinstance(identity.rel_data_o, DischargeSeries):
            new_win = self._discharge_series
        elif isinstance(identity.rel_data_o, PMTestSeries):
            new_win = self._pm_test_series
        elif isinstance(identity.rel_data_o, PMSampleSet):
            new_win = self._pm_sample_set
        else:
            self.stop()
            return
        win = self._sizer.GetItem(1).GetWindow()
        win.end()
        self._sizer.Detach(1)
        self._sizer.Insert(1, new_win, 1, wx.EXPAND)
        new_win.start(identity.rel_data_o, identity.rel_data_target)
        if identity.rel_data_target == None:
            if hasattr(identity.rel_data_o, "get_tree_name"):
                self.statusbar.SetStatusText(identity.rel_data_o.get_tree_name())
            else:
                self.statusbar.SetStatusText("")
        self.Layout()

    def stop(self):
        win = self._sizer.GetItem(1).GetWindow()
        win.end()
        self._sizer.Detach(1)
        self._sizer.Add(self._deputy, 1, wx.EXPAND)
        self.Layout()
