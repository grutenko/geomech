import wx
from pony.orm import *
import wx.lib.mixins.listctrl as listmix
import pubsub

from database import RockBurst
from ui.icon import get_art, get_icon
from .create import DialogCreateRockBurst
from ui.datetimeutil import decode_datetime
from ui.windows.main.identity import Identity


class RbList(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        super().__init__(parent)

        self._items = {}
        self.itemDataMap = {}

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_list = wx.ImageList(16, 16)
        self._help_page_icon = self._image_list.Add(get_art(wx.ART_HELP_PAGE))
        self._list = wx.ListCtrl(self, style=wx.LC_REPORT)
        listmix.ColumnSorterMixin.__init__(self, 6)
        self._list.AppendColumn("Название", width=250)
        self._list.AppendColumn("Дата события", width=100)
        self._list.AppendColumn("Месторождение", width=150)
        self._list.AssignImageList(self._image_list, wx.IMAGE_LIST_SMALL)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        self._bind_all()
        self._render()

    def GetListCtrl(self):
        return self._list

    def _bind_all(self):
        self._list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_right_click)

    @db_session
    def _render(self):
        rock_bursts = select(o for o in RockBurst).order_by(lambda x: desc(x.RID))
        self._list.DeleteAllItems()
        self._items = {}
        for o in rock_bursts:
            self._items[o.RID] = o
        self.itemDataMap = {}
        m = [
            "REGION",
            "ROCKS",
            "FIELD",
            "HORIZON",
            "EXCAVATION",
        ]
        for index, o in enumerate(rock_bursts):
            _row = []
            _row.append(o.Name)
            _row.append(decode_datetime(o.BurstDate))
            mine_object = o.mine_object
            _target_index = m.index("FIELD")
            if mine_object.Type in m:
                while m.index(mine_object.Type) > _target_index:
                    mine_object = mine_object.parent
            _row.append(mine_object.Name)
            item = self._list.InsertItem(index, _row[0], self._help_page_icon)
            self._list.SetItem(item, 1, _row[1].__str__())
            self._list.SetItem(item, 2, _row[2])
            self._list.SetItemData(item, o.RID)
            self.itemDataMap[o.RID] = _row

    def _on_right_click(self, event: wx.ListEvent):
        index = event.GetIndex()
        if index != -1:
            self._list.Select(index)
            menu = wx.Menu()
            item = menu.Append(wx.ID_EDIT, "Изменить")
            item.SetBitmap(get_icon("edit"))
            item = menu.Append(wx.ID_DELETE, "Удалить")
            item.SetBitmap(get_icon("delete"))
            menu.AppendSeparator()
            item = menu.Append(wx.ID_ADD, "Добавить горный удар")
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            item.SetBitmap(get_icon("wand"))
        else:
            menu = wx.Menu()
            item = menu.Append(wx.ID_ADD, "Добавить горный удар")
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            item.SetBitmap(get_icon("wand"))
        self.PopupMenu(menu, event.GetPoint())

    def _on_add(self, event):
        dlg = DialogCreateRockBurst(self)
        dlg.ShowModal()

    def remove_selection(self):
        i = self._list.GetFirstSelected()
        while i != -1:
            self._list.Select(i, 0)
            i = self._list.GetNextSelected(i)
