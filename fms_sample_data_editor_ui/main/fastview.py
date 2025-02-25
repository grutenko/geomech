import wx
import wx.propgrid

from .fastview_core import FastviewOrigSampleSet
from .fastview_orig_other import FastviewOrigOther
from .fastview_pm_sample import FastviewPmSample
from .fastview_pm_sample_set import FastviewPmSampleSet
from .fastview_pm_test_series import FastviewPmTestSeries
from database import OrigSampleSet, PMSampleSet, PMSample, PMTestSeries


class Deputy(wx.propgrid.PropertyGrid):
    def __init__(self, parent):
        super().__init__(parent)
        self.Hide()

    def start(self, o):
        self.Show()


class FastView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        sz = wx.BoxSizer(wx.VERTICAL)
        self.deputy = Deputy(self)
        self.current = self.deputy
        self.core = FastviewOrigSampleSet(self)
        self.orig_other = FastviewOrigOther(self)
        self.pm_sample_set = FastviewPmSampleSet(self)
        self.pm_sample = FastviewPmSample(self)
        self.pm_test_series = FastviewPmTestSeries(self)
        sz.Add(self.current, 1, wx.EXPAND)
        self.sz = sz
        self.SetSizer(sz)
        self.Layout()

    def start(self, o):
        new_panel = None
        if o is None:
            new_panel = self.deputy
        elif isinstance(o, OrigSampleSet) and o.SampleType == "CORE":
            new_panel = self.core
        elif isinstance(o, OrigSampleSet):
            new_panel = self.orig_other
        elif isinstance(o, PMSampleSet):
            new_panel = self.pm_sample_set
        elif isinstance(o, PMSample):
            new_panel = self.pm_sample
        elif isinstance(o, PMTestSeries):
            new_panel = self.pm_test_series
        self.sz.Remove(0)
        self.current.Hide()
        self.sz.Add(new_panel, 1, wx.EXPAND)
        new_panel.start(o)
        new_panel.Layout()
        self.current = new_panel
        self.Layout()
