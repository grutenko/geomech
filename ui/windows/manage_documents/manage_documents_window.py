import wx

from ui.icon import get_icon
from .tree import *

class ManageDocumentsWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Документы",
            style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX | wx.FRAME_FLOAT_ON_PARENT,
        )
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self._tree = DocumentsTree(self)
        main_sizer.Add(self._tree, 1, wx.EXPAND)

        menu_bar = wx.MenuBar()
        self.SetMenuBar(menu_bar)
        menu = wx.Menu()
        item = menu.Append(wx.ID_ADD, "Добавить документ")
        menu.AppendSeparator()
        menu.Bind(wx.EVT_MENU, self._on_create, item)
        item = menu.Append(wx.ID_EDIT, "Изменить документ")
        item.Enable(False)
        menu.Bind(wx.EVT_MENU, self._on_edit, item)
        item = menu.Append(wx.ID_DELETE, "Удалить документ")
        item.Enable(False)
        menu.Bind(wx.EVT_MENU, self._on_delete, item)
        menu_bar.Append(menu, "Управление")
        self._menu_bar = menu_bar

        self._tree.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self._on_node_selection_changed)

    def _on_node_selection_changed(self, event):
        self._menu_bar.Enable(wx.ID_EDIT, event.node != None)
        self._menu_bar.Enable(wx.ID_DELETE, event.node != None)

    def _on_create(self, event):
        self._tree.create()

    def _on_edit(self, event):
        self._tree.update()

    def _on_delete(self, event):
        self._tree.delete()