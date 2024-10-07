import wx
import wx.lib.mixins.listctrl as listmix

from pony.orm import *
from database import *
from ui.icon import get_art, get_icon
from ui.icon import get_art
from ui.datetimeutil import decode_date

from .create import DialogCreateDischargeSeries


class DischargeList(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        super().__init__(parent)

        self._items = []

        self.itemDataMap = {}


        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_list = wx.ImageList(16, 16)
        self._book_stack_icon = self._image_list.Add(get_icon("read"))
        self._list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self._list.AppendColumn("Название", width=250)
        self._list.AppendColumn("Дата начала", width=100)
        self._list.AppendColumn("Дата окончания", width=100)
        self._list.AppendColumn("Договор", width=150)
        self._list.AppendColumn("Месторождение", width=150)
        self._list.AppendColumn("ID", format=wx.LIST_FORMAT_RIGHT, width=70)
        self._list.AssignImageList(self._image_list, wx.IMAGE_LIST_SMALL)
        listmix.ColumnSorterMixin.__init__(self, 6)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        self._load()
        self._bind_all()

    def _bind_all(self):
        self._list.Bind(wx.EVT_RIGHT_DOWN, self._on_right_click)

    def _on_right_click(self, event: wx.MouseEvent):
        index, flags = self._list.HitTest(event.GetPosition())
        if index != -1:
            self._list.Select(index)
            menu = wx.Menu()
            item = menu.Append(wx.ID_EDIT, "Изменить")
            item.SetBitmap(get_icon("edit"))
            item = menu.Append(wx.ID_DELETE, "Удалить")
            item.SetBitmap(get_icon("delete"))
            menu.AppendSeparator()
            item = menu.Append(wx.ID_ADD, "Добавить разгрузку")
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            item.SetBitmap(get_icon("wand"))
        else:
            menu = wx.Menu()
            item = menu.Append(wx.ID_ADD, "Добавить разгрузку")
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            item.SetBitmap(get_icon("wand"))
        self.PopupMenu(menu, event.GetPosition())

    @db_session
    def _load(self):
        discharges = select(o for o in DischargeSeries).order_by(
            lambda x: desc(x.StartMeasure)
        )
        self._items = discharges
        m = [
            "REGION",
            "ROCKS",
            "FIELD",
            "HORIZON",
            "EXCAVATION",
        ]
        self.itemDataMap = {}
        for index, o in enumerate(discharges):
            _row = []
            _row.append(o.Name)
            _row.append(decode_date(o.StartMeasure))
            if o.EndMeasure != None:
                _end_measure = decode_date(o.EndMeasure)
            else:
                _end_measure = ""
            _row.append(_end_measure)
            if o.foundation_document != None:
                _doc = o.foundation_document.Name
            else:
                _doc = ""
            _row.append(_doc)
            mine_object = o.orig_sample_set.mine_object
            _target_index = m.index("FIELD")
            if mine_object.Type in m:
                while m.index(mine_object.Type) > _target_index:
                    mine_object = mine_object.parent
            _row.append(mine_object.Name)
            _row.append(o.RID)

            item = self._list.InsertItem(index, _row[0], self._book_stack_icon)
            self._list.SetItem(item, 1, _row[1].__str__())
            self._list.SetItem(item, 2, _row[2].__str__())
            self._list.SetItem(item, 3, _row[3])
            self._list.SetItem(item, 4, _row[4])
            self._list.SetItem(item, 5, _row[5].__str__())
            self._list.SetItemData(item, o.RID)
            self.itemDataMap[o.RID] = _row
        print(list(self.itemDataMap.keys()))

    def GetListCtrl(self):
        return self._list

    def _on_add(self, event):
        dlg = DialogCreateDischargeSeries(self)
        dlg.ShowModal()

    def get_items(self):
        return self._items

    def start(self):
        self.Show()

    def end(self):
        self.Hide()
