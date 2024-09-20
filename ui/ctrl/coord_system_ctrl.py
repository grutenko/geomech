import wx

from pony.orm import *
from database import CoordSystem

class CoordSystemCtrl(wx.Choice):
    def __init__(self, parent):
        super().__init__(parent)

        self._coord_systems = []
        self._load_coord_systems()
        if len(self._coord_systems) > 0:
            self.SetSelection(0)

    @db_session
    def _load_coord_systems(self, p = None):
        if p == None:
            coord_systems = select(o for o in CoordSystem if o.Level == 0)
        else:
            coord_systems = select(o for o in CoordSystem if o.parent == p)
        for cs in coord_systems:
            self._coord_systems.append(cs)
            self.Append((" . " * cs.Level) + cs.Name, cs)
            self._load_coord_systems(cs)

    def GetValue(self):
        i = self.GetSelection()
        if i != -1:
            return self._coord_systems[i]
        return None
    
    def SetValue(self, value):
        for index, o in enumerate(self._coord_systems):
            if o.RID == value.RID:
                self.SetSelection(index)
