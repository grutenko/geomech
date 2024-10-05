import wx

from pony.orm import *
from database import *
from ui.icon import get_art, get_icon
from ui.datetimeutil import decode_date

from .create import DialogCreatePmSeries

class PmList(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self._items = []

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_list = wx.ImageList(16, 16)
        self._book_stack_icon = self._image_list.Add(get_icon("book-stack"))
        self._list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self._list.AppendColumn("Название", width=250)
        self._list.AppendColumn("Место", width=150)
        self._list.AppendColumn("Договор", width=150)
        self._list.AssignImageList(self._image_list, wx.IMAGE_LIST_SMALL)
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
            item.SetBitmap(get_art(wx.ART_EDIT))
            item = menu.Append(wx.ID_DELETE, "Удалить")
            item.SetBitmap(get_art(wx.ART_DELETE))
            menu.AppendSeparator()
            item = menu.Append(wx.ID_ADD, "Добавить набор")
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            item.SetBitmap(get_icon("magic-wand"))
        else:
            menu = wx.Menu()
            item = menu.Append(wx.ID_ADD, "Добавить набор")
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            item.SetBitmap(get_icon("magic-wand"))
        self.PopupMenu(menu, event.GetPosition())

    @db_session
    def _load(self):
        discharges = select(o for o in PMTestSeries).order_by(
            lambda x: desc(x.RID)
        )
        self._items = discharges
        for index, o in enumerate(discharges):
            item = self._list.InsertItem(index, o.Name, self._book_stack_icon)
            self._list.SetItem(item, 1, o.Location if o.Location != None else o.Location)
            self._list.SetItemData(item, o.RID)

    def _on_add(self, event):
        dlg = DialogCreatePmSeries(self)
        dlg.ShowModal()

    def get_items(self):
        return self._items

    def start(self):
        self.Show()

    def end(self):
        self.Hide()
