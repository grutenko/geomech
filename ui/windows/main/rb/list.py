import wx

from ui.icon import get_art, get_icon
from .create import DialogCreateRockBurst

class RbList(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_list = wx.ImageList(16, 16)
        self._help_page_icon = self._image_list.Add(get_art(wx.ART_HELP_PAGE))
        self._list = wx.ListCtrl(self, style=wx.LC_REPORT)
        self._list.AppendColumn("Название", width=250)
        self._list.AppendColumn("Дата события", width=100)
        self._list.AppendColumn("Месторождение", width=150)
        self._list.AssignImageList(self._image_list, wx.IMAGE_LIST_SMALL)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        self._bind_all()

    def _bind_all(self):
        self._list.Bind(wx.EVT_RIGHT_DOWN, self._on_right_click)

    def _on_right_click(self, event: wx.MouseEvent):
        index, flags = self._list.HitTest(event.GetPosition())
        if index != -1:
            self._list.Select(index)
            menu = wx.Menu()
            item = menu.Append(wx.ID_EDIT, "Изменить")
            item.SetBitmap(get_icon('edit'))
            item = menu.Append(wx.ID_DELETE, "Удалить")
            item.SetBitmap(get_icon('delete'))
            menu.AppendSeparator()
            item = menu.Append(wx.ID_ADD, "Добавить горный удар")
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            item.SetBitmap(get_icon("wand"))
        else:
            menu = wx.Menu()
            item = menu.Append(wx.ID_ADD, "Добавить горный удар")
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            item.SetBitmap(get_icon("wand"))
        self.PopupMenu(menu, event.GetPosition())

    def _on_add(self, event):
        dlg = DialogCreateRockBurst(self)
        dlg.ShowModal()

    def remove_selection(self):
        i = self._list.GetFirstSelected()
        while i != -1:
            self._list.Select(i, 0)
            i = self._list.GetNextSelected(i)