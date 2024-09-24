from typing import List, Tuple
import wx

from database import *

from .properties_panels.mine_object.properties import MineObjectProperties
from .properties_panels.station.properties import StationProperties
from .properties_panels.bore_hole.properties import BoreHoleProperties
from .properties_panels.orig_sample_set.properties import CoreProperties

import wx.lib.newevent

PropertiesPropertySelectedEvent, EVT_PROPERTIES_PROPERTY_SELECTED = (
    wx.lib.newevent.NewEvent()
)
PropertiesTargetUpdatedEvent, EVT_PROPERTIES_TARGET_UPDATED = wx.lib.newevent.NewEvent()


class _Deputy(wx.Panel):
    def start(self, o):
        self.Show()

    def end(self):
        self.Hide()


class MainWindowProperties(wx.Panel):
    def __init__(self, parent, menubar, statusbar):
        super().__init__(parent)
        self.menubar = menubar
        self.statusbar = statusbar
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.main_sizer)

        self.properties = {
            MineObject: MineObjectProperties(self, menubar, statusbar),
            Station: StationProperties(self, menubar, statusbar),
            BoreHole: BoreHoleProperties(self, menubar, statusbar),
            OrigSampleSet: CoreProperties(self, menubar, statusbar),
        }
        for p in self.properties.values():
            p.Hide()

        self._deputy_panel = _Deputy(self)
        self.main_sizer.Add(self._deputy_panel, 1, wx.EXPAND)
        self.Layout()

    def start(self, o):
        if isinstance(o, MineObject):
            panel = self.properties[MineObject]
        elif isinstance(o, Station):
            panel = self.properties[Station]
        elif isinstance(o, BoreHole):
            panel = self.properties[BoreHole]
        elif isinstance(o, OrigSampleSet):
            panel = self.properties[OrigSampleSet]
        else:
            return
        old_panel = self.main_sizer.GetItem(0).GetWindow()
        old_panel.end()
        self.main_sizer.Detach(0)
        self.main_sizer.Add(panel, 1, wx.EXPAND)
        panel.start(
            o, self._on_properties_object_selected, self._on_properties_target_updated
        )
        self.Layout()

    def _on_properties_object_selected(self, object, bounds=None):
        wx.PostEvent(
            self, PropertiesPropertySelectedEvent(object=object, bounds=bounds)
        )

    def _on_properties_target_updated(self, object):
        wx.PostEvent(self, PropertiesTargetUpdatedEvent(object=object))

    def open_self_editor(self):
        panel = self.main_sizer.GetItem(0).GetWindow()
        if not isinstance(panel, _Deputy):
            panel.open_self_props_editor()
