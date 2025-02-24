import wx

from pony.orm import select, db_session
from database import MineObject, OrigSampleSet, BoreHole
from ui.icon import get_icon
from ui.delete_object import delete_object
from .orig_sample_set_dialog import OrigSampleSetCoreDialog, OrigSampleSetOtherDialog, OrigSampleSetSelectTypeDialog


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
        self.DeleteAllItems()
        self.items = []
        for index, o in enumerate(select(o for o in OrigSampleSet if o.bore_hole == None or o.bore_hole.station == None)):
            self.items.append(o)
            self.InsertItem(index, o.Name, self.icon)

    def delete(self):
        index = self.GetFirstSelected()
        if index != -1:
            if delete_object(self.items[index], ["pm_samples"]):
                self.load()

    def on_create(self):
        dlg = OrigSampleSetSelectTypeDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.type == "CORE":
                dlg0 = OrigSampleSetCoreDialog(self)
            else:
                dlg0 = OrigSampleSetOtherDialog(self)
            if dlg0.ShowModal() == wx.ID_OK:
                self.load()
