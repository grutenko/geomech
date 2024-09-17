import wx

from .tree import *

class ManageDocumentsWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(
            parent,
            title="Документы",
            style=wx.DEFAULT_FRAME_STYLE & ~wx.MAXIMIZE_BOX | wx.FRAME_FLOAT_ON_PARENT,
        )
        self.SetIcon(wx.Icon("./icons/logo@16.jpg"))
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

    def _on_create(self, event):
        ...

    def _on_edit(self, event):
        ...

    def _on_delete(self, event):
        ...