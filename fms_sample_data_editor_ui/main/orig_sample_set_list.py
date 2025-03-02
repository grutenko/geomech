import wx

from pony.orm import select, db_session, commit, sql_debug
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
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)

    def on_right_click(self, event):
        item, a = self.HitTest(event.GetPosition())
        if item == -1:
            m = wx.Menu()
            i = m.Append(wx.ID_ADD, "Добавить набор")
            i.SetBitmap(get_icon("file-add"))
            m.Bind(wx.EVT_MENU, self.on_create, i)
            self.PopupMenu(m, event.GetPosition())

    @db_session
    def load(self):
        self.DeleteAllItems()
        self.items = []
        for index, o in enumerate(select(o for o in OrigSampleSet)):
            if o.bore_hole is None or o.bore_hole.station is None:
                self.items.append(o)
                self.InsertItem(index, o.Name, self.icon)

    @db_session
    def delete(self):
        index = self.GetFirstSelected()
        if index != -1:
            o = self.items[index]
            if o.SampleType == "CORE":
                bore_hole = BoreHole[o.bore_hole.RID] if o.bore_hole.RID is not None else None
                if delete_object(o, ["pm_samples"]):
                    if bore_hole:
                        bore_hole.delete()
                        commit()
                    self.load()
            else:
                if delete_object(o, ["pm_samples"]):
                    self.load()

    def on_create(self, event=None):
        dlg = OrigSampleSetSelectTypeDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            if dlg.type == "CORE":
                dlg0 = OrigSampleSetCoreDialog(self)
            else:
                dlg0 = OrigSampleSetOtherDialog(self)
            if dlg0.ShowModal() == wx.ID_OK:
                self.load()

    def get_selected_orig_sample_set(self):
        index = self.GetFirstSelected()
        if index != -1:
            return self.items[index]
        return None
