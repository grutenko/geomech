import wx
import wx.dataview
import os

from pony.orm import *
from database import *

from ui.icon import get_art, get_icon
from ui.resourcelocation import resource_path


class SuppliedDataWidget(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        item = self.toolbar.AddTool(wx.ID_ADD, "Добавить раздел", get_icon('folder-add'))
        item = self.toolbar.AddTool(wx.ID_FILE, "Добавить файл", get_icon('file-add'))
        self.toolbar.AddStretchableSpace()
        item = self.toolbar.AddTool(wx.ID_DOWN, "Скачать", get_icon('download'), kind=wx.ITEM_DROPDOWN)
        self.toolbar.EnableTool(wx.ID_FILE, False)
        self.toolbar.Realize()
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)

        self.statusbar = wx.StatusBar(self, style=0)
        main_sizer.Add(self.statusbar, 0, wx.EXPAND)

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
        self._icons = {}
        self.list = wx.dataview.TreeListCtrl(
            self, style=wx.dataview.TL_DEFAULT_STYLE | wx.BORDER_NONE | wx.dataview.TL_3STATE
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
        self.list.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self._on_selection_changed)

        self.SetSizer(main_sizer)
        self._main_sizer = main_sizer

        self.Layout()

    def _on_selection_changed(self, event):
        self.list.UnselectAll()
        item = self.list.GetFirstItem()
        while item.IsOk():
            self.list.CheckItem(item, wx.CHK_UNCHECKED)
            item = self.list.GetNextItem(item)
        self.list.CheckItemRecursively(event.GetItem())
        self.list.Select(event.GetItem())
        self._update_controls_state()

    def _apply_icon(self, icon_name, icon):
        if icon_name not in self._icons:
            self._icons[icon_name] = self._image_list.Add(icon)
        return self._icons[icon_name]

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
                ext = child.FileName.split(".")[-1]
                if ext == 'xlsx':
                    ext = 'xls'
                icon_path = resource_path("icons/%s.png" % ext)
                if os.path.exists(icon_path):
                    _icon = self._apply_icon(ext, wx.Bitmap(icon_path))
                else:
                    _icon = self._icon_file
                file = self.list.AppendItem(
                    folder, child.Name, _icon, _icon, child
                )
                self.list.SetItemText(file, 1, child.FileName.split(".")[-1])
                self.list.SetItemText(file, 2, "---")

    def _update_controls_state(self):
        self.toolbar.EnableTool(wx.ID_ADD, self.o != None)
        item = self.list.GetSelection()
        item_selected = False
        folder_selected = False
        if item.IsOk():
            item_selected = True
            folder_selected = isinstance(self.list.GetItemData(item), SuppliedData)
        self.toolbar.EnableTool(wx.ID_FILE, folder_selected)

    def start(self, o, _type):
        self.o = o
        self._type = _type
        self._main_sizer.Detach(2)
        self._deputy.Hide()
        self._main_sizer.Add(self.list, 1, wx.EXPAND)
        self.list.Show()
        self._render()
        self.statusbar.SetStatusText(o.get_tree_name())
        self.Layout()

    def end(self):
        self.o = None
        self._type = None
        self.list.DeleteAllItems()
        self._main_sizer.Detach(2)
        self.list.Hide()
        self._main_sizer.Add(self._deputy, 1, wx.CENTER)
        self._deputy.Show()
        self.statusbar.SetStatusText("")
        self.Layout()
