import wx

from ui.widgets.supplied_data.widget import SuppliedDataWidget
from .tree import TestSeriesTree, EVT_WIDGET_TREE_SEL_CHANGED


class ManageTestSeriesWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Наборы испытаний",
            style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX | wx.FRAME_FLOAT_ON_PARENT,
            size=wx.Size(350, 400)
        )
        self.SetIcon(wx.Icon("./icons/logo@16.jpg"))
        self.CenterOnParent()

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(top_sizer)

        splitter = wx.SplitterWindow(self)

        top_sizer.Add(splitter, 1, wx.EXPAND)

        main_panel = wx.Panel(splitter)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_panel.SetSizer(main_sizer)

        self._tree = TestSeriesTree(main_panel)
        main_sizer.Add(self._tree, 1, wx.EXPAND)

        self.Layout()

        menu_bar = wx.MenuBar()
        self.SetMenuBar(menu_bar)
        menu = wx.Menu()
        item = menu.Append(wx.ID_ADD, "Добавить набор")
        menu.Bind(wx.EVT_MENU, self._on_add_series, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_FILE, "Открыть сопутствующие материалы")
        item.Enable(False)
        item = menu.Append(wx.ID_EDIT, "Изменить параметры набора")
        item.Enable(False)
        menu.Bind(wx.EVT_MENU, self._on_update_series, item)
        item = menu.Append(wx.ID_DELETE, "Удалить набор")
        item.Enable(False)
        menu.Bind(wx.EVT_MENU, self._on_add_series, item)
        menu_bar.Append(menu, "Управление")
        self.menu_bar = menu_bar

        self._tree.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self._on_selection_changed)

        splitter.Initialize(main_panel)

        self.Layout()

    def _on_selection_changed(self, event):
        self.menu_bar.Enable(wx.ID_EDIT, event.node != None)
        self.menu_bar.Enable(wx.ID_EDIT, event.node != None)
        self.menu_bar.Enable(wx.ID_FILE, event.node != None)

    def _on_add_series(self, event):
        self._tree.open_create_series_dialog()

    def _on_update_series(self, event):
        self._tree.open_edit_series_dialog()
