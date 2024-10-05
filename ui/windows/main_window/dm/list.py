import wx

from pony.orm import *
from database import *
from ui.icon import get_art
from ui.datetimeutil import decode_date


class DischargeList(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self._items = []

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_list = wx.ImageList(16, 16)
        self._folder_icon = self._image_list.Add(get_art(wx.ART_FOLDER))
        self._list = wx.ListCtrl(self, style=wx.LC_LIST)
        self._list.AppendColumn("Название", width=250)
        self._list.AssignImageList(self._image_list, wx.IMAGE_LIST_SMALL)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        self._load()

    @db_session
    def _load(self):
        discharges = select(o for o in DischargeSeries).order_by(
            lambda x: desc(x.StartMeasure)
        )
        self._items = discharges
        for index, o in enumerate(discharges):
            item = self._list.InsertItem(index, o.Name, self._folder_icon)
            self._list.SetItemData(item, o.RID)

    def get_items(self):
        return self._items

    def start(self):
        self.Show()

    def end(self):
        self.Hide()
