import wx

from pony.orm import select, db_session
from database import MineObject, OrigSampleSet, BoreHole
from ui.icon import get_icon

class OrigSampleSetList(wx.ListCtrl):
    def __init__(self, parent):
        super().__init__(parent, style=wx.LC_REPORT)
        self.AppendColumn("Название", width=250)
        self.image_list = wx.ImageList(16, 16)
        self.icon = self.image_list.Add(get_icon("read"))
        self.AssignImageList(self.image_list, wx.IMAGE_LIST_SMALL)
        self.items = []
        self.load()
        
    @db_session
    def load(self):
        for index, o in enumerate(select(o for o in OrigSampleSet if o.bore_hole == None or o.bore_hole.station == None)):
            self.items.append(o)
            self.InsertItem(index, o.Name, self.icon)