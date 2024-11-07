import wx

from ui.icon import get_art, get_icon


class SuppliedDataWidgetForNewOwner(wx.Panel):
    def __init__(self, parent, owner_type):
        super().__init__(parent)

        self.owner_type = owner_type

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        item = self.toolbar.AddTool(wx.ID_ADD, "Добавить раздел", get_icon("folder-add"))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_create_folder, item)
        item = self.toolbar.AddTool(wx.ID_FILE, "Добавить файл", get_icon("file-add"))
        self.toolbar.EnableTool(wx.ID_FILE, False)
        self.toolbar.Realize()
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)

        self._image_list = wx.ImageList(16, 16)
        self._icons = {}
        self.list = wx.dataview.TreeListCtrl(self, style=wx.dataview.TL_DEFAULT_STYLE | wx.BORDER_NONE)
        self.list.AssignImageList(self._image_list)
        self._icon_folder = self._image_list.Add(get_icon("folder"))
        self._icon_folder_open = self._image_list.Add(get_icon("folder-open"))
        self._icon_file = self._image_list.Add(get_art(wx.ART_NORMAL_FILE, scale_to=16))
        self.list.AppendColumn("Название", 250)
        self.list.AppendColumn("Тип", 50)
        self.list.AppendColumn("Размер", 50)
        self.list.AppendColumn("Датировка", 80)

        main_sizer.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(main_sizer)
        self._main_sizer = main_sizer

        self.list.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self._on_selection_changed)
        self.list.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self._on_item_contenxt_menu)

        self.Layout()

    def _on_create_folder(self, event): ...

    def _on_create_file(self, event): ...

    def _on_selection_changed(self, event): ...

    def _on_item_contenxt_menu(self, event): ...
