import wx

from database import *

class _Deputy(wx.Panel):
    def start(self, o, bounds = None):
        self.Show()
    def end(self):
        self.Hide()

from .fastview_panels.bore_hole import BoreHoleFastview
from .fastview_panels.core import CoreFastview
from .fastview_panels.mine_object import MineObjectFastview
from .fastview_panels.pm_sample_set import PmSampleSetFastview
from .fastview_panels.pm_sample_sets_list import PmSampleSetsListFastview
from .fastview_panels.rock_burst import RockBurstFastview
from .fastview_panels.rock_bursts_list import RockBurstsListFastview
from .fastview_panels.station import StationFastview
from .fastview_panels.pm_samples_list import PmSamplesListFastview
from .fastview_panels.discharge_series import DischargeSeriesFastview
from .fastview_panels.discharge_measurements_list import DischargeMeasurementsListFastview

class FastviewMainWindow(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._deputy_panel = _Deputy(self)
        self.main_sizer.Add(self._deputy_panel, 1, wx.EXPAND)

        self._bore_hole_panel = BoreHoleFastview(self)
        self._core_panel = CoreFastview(self)
        self._mine_object_panel = MineObjectFastview(self)
        self._pm_sample_set_panel = PmSampleSetFastview(self)
        self._pm_sample_sets_list_panel = PmSampleSetsListFastview(self)
        self._rock_burst_panel = RockBurstFastview(self)
        self._rock_bursts_list_panel = RockBurstsListFastview(self)
        self._station_panel = StationFastview(self)
        self._pm_samples_panel = PmSamplesListFastview(self)
        self._discharge_series_panel = DischargeSeriesFastview(self)
        self._discharge_measurements_list_panel = DischargeMeasurementsListFastview(self)

        self.SetSizer(self.main_sizer)
        self.Layout()

    def start(self, o, bounds = None):
        if isinstance(o, BoreHole):
            panel = self._bore_hole_panel
        elif isinstance(o, OrigSampleSet) and bounds == DischargeMeasurement:
            panel = self._discharge_measurements_list_panel
        elif isinstance(o, DischargeSeries):
            panel = self._discharge_series_panel
        elif isinstance(o, OrigSampleSet) and bounds == PMSample:
            panel = self._pm_samples_panel
        elif isinstance(o, OrigSampleSet) and o.bore_hole != None:
            panel = self._core_panel
        elif isinstance(o, MineObject) and bounds == PMSampleSet:
            panel = self._pm_sample_sets_list_panel
        elif isinstance(o, MineObject) and bounds == RockBurst:
            panel = self._rock_bursts_list_panel
        elif isinstance(o, MineObject):
            panel = self._mine_object_panel
        elif isinstance(o, PMSampleSet):
            panel = self._pm_sample_set_panel
        elif isinstance(o, RockBurst):
            panel = self._rock_burst_panel
        elif isinstance(o, Station):
            panel = self._station_panel
        else:
            panel = self._deputy_panel
        old_panel = self.main_sizer.GetItem(0).GetWindow()
        old_panel.end()
        self.main_sizer.Detach(0)
        self.main_sizer.Add(panel, 1, wx.EXPAND)
        panel.start(o, bounds)
        self.Layout()

    def end(self):
        old_panel = self.main_sizer.GetItem(0).GetWindow()
        old_panel.end()
        self.main_sizer.Detach(0)
        self.main_sizer.Add(self._deputy_panel, 1, wx.EXPAND)
        self._deputy_panel.start(None, None)
        self.Layout()