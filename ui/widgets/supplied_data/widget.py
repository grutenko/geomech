import wx
import wx.dataview

from pony.orm import *
from database import *

from ui.icon import get_art, get_icon


class SuppliedDataWidget(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._deputy = wx.Panel(self)
        deputy_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(
            self._deputy,
            label="Недоступны для этого объекта",
            style=wx.ST_ELLIPSIZE_MIDDLE,
        )
        deputy_sizer.Add(label, 1, wx.CENTER | wx.ALL, border=20)
        self._deputy.SetSizer(deputy_sizer)
        main_sizer.Add(self._deputy, 1, wx.EXPAND)

        self._image_list = wx.ImageList(16, 16)
        self.list = wx.dataview.TreeListCtrl(
            self, style=wx.dataview.TL_DEFAULT_STYLE | wx.BORDER_NONE
        )
        self.list.AssignImageList(self._image_list)
        self._icon_folder = self._image_list.Add(get_icon('folder'))
        self._icon_folder_open = self._image_list.Add(
            get_icon('folder-open'))
        self._icon_file = self._image_list.Add(get_art(wx.ART_NORMAL_FILE, scale_to=16))
        self.list.AppendColumn("Название", 250)
        self.list.AppendColumn("Тип", 50)
        self.list.AppendColumn("Размер", 50)
        self.list.AppendColumn("Датировка", 80)
        self.list.Hide()

        self.SetSizer(main_sizer)
        self._main_sizer = main_sizer

        self.Layout()

    @db_session
    def _render(self):
        self.list.DeleteAllItems()
        for o in select(
            o for o in SuppliedData if o.OwnID == self.o.RID and o.OwnType == self._type
        ):
            folder = self.list.AppendItem(
                self.list.GetRootItem(),
                o.Name,
                self._icon_folder,
                self._icon_folder_open,
                o,
            )
            self.list.SetItemText(folder, 1, "Папка")
            self.list.SetItemText(folder, 2, "---")
            for child in o.parts:
                file = self.list.AppendItem(
                    folder, child.Name, self._icon_file, self._icon_file, child
                )
                self.list.SetItemText(file, 1, child.FileName.split(".")[-1])
                self.list.SetItemText(file, 2, "---")

    def start(self, o, _type):
        self.o = o
        self._type = _type
        self._main_sizer.Detach(0)
        self._deputy.Hide()
        self._main_sizer.Add(self.list, 1, wx.EXPAND)
        self.list.Show()
        self._render()
        self.Layout()

    def end(self):
        self.o = None
        self._type = None
        self.list.DeleteAllItems()
        self._main_sizer.Detach(0)
        self.list.Hide()
        self._main_sizer.Add(self._deputy, 1, wx.CENTER)
        self._deputy.Show()
        self.Layout()
