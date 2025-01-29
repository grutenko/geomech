import wx
from pony.orm import db_session, desc, select

from database import PMTestSeries
from ui.delete_object import delete_object
from ui.icon import get_icon

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
        self._silence_select = False

    def get_current_o(self):
        if self._list.GetFirstSelected() == -1:
            return None
        return self._items[self._list.GetFirstSelected()]

    def _bind_all(self):
        self._list.Bind(wx.EVT_RIGHT_DOWN, self._on_right_click)
        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_selected)
        self._list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_item_selected)

    def _on_item_selected(self, event):
        if not self._silence_select:
            event.Skip()

    def _on_right_click(self, event: wx.MouseEvent):
        index, flags = self._list.HitTest(event.GetPosition())
        if index != -1:
            self._list.Select(index)
            menu = wx.Menu()
            item = menu.Append(wx.ID_EDIT, "Изменить")
            item.SetBitmap(get_icon("edit"))
            item = menu.Append(wx.ID_DELETE, "Удалить")
            item.SetBitmap(get_icon("delete"))
            menu.Bind(wx.EVT_MENU, self._on_delete, item)
            menu.AppendSeparator()
            item = menu.Append(wx.ID_ADD, "Добавить набор")
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            item.SetBitmap(get_icon("wand"))
        else:
            menu = wx.Menu()
            item = menu.Append(wx.ID_ADD, "Добавить набор")
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            item.SetBitmap(get_icon("wand"))
        self.PopupMenu(menu, event.GetPosition())

    @db_session
    def _load(self):
        self._list.DeleteAllItems()
        discharges = select(o for o in PMTestSeries).order_by(lambda x: desc(x.RID))
        self._items = []
        for index, o in enumerate(discharges):
            item = self._list.InsertItem(index, o.Number, self._book_stack_icon)
            self._list.SetItem(item, 1, o.Location if o.Location != None else o.Location)
            self._list.SetItemData(item, o.RID)
            self._items.append(o)

    def _on_delete(self, event):
        index = self._list.GetFirstSelected()
        if index == -1:
            return

        o = self._items[index]
        if delete_object(o, ["pm_sample_sets"]):
            self._load()

    def _on_add(self, event):
        dlg = DialogCreatePmSeries(self)
        if dlg.ShowModal() == wx.ID_OK:
            self._load()

    def get_items(self):
        return self._items

    def start(self):
        self.Show()

    def end(self):
        self.Hide()

    def remove_selection(self, silence=False):
        i = self._list.GetFirstSelected()
        self._silence_select = silence
        try:
            while i != -1:
                self._list.Select(i, 0)
                i = self._list.GetNextSelected(i)
        finally:
            self._silence_select = False
