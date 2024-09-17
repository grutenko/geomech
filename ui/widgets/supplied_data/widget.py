import wx
import wx.dataview

from pony.orm import *
from database import *

from ui.icon import get_art

class SuppliedDataWidget(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_list = wx.ImageList(16, 16)
        self.list = wx.dataview.TreeListCtrl(self, style=wx.dataview.TL_DEFAULT_STYLE | wx.BORDER_NONE)
        self.list.AssignImageList(self._image_list)
        self._icon_folder = self._image_list.Add(get_art(wx.ART_FOLDER, scale_to=16))
        self._icon_folder_open = self._image_list.Add(get_art(wx.ART_FOLDER_OPEN, scale_to=16))
        self._icon_file = self._image_list.Add(get_art(wx.ART_NORMAL_FILE, scale_to=16))
        self.list.AppendColumn("Название", 250)
        self.list.AppendColumn("Тип", 50)
        self.list.AppendColumn("Размер", 150)
        main_sizer.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(main_sizer)

        self.Layout()

    def start(self, o, _type):
        self.o = o
        self._type = _type