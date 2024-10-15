import wx
import wx.lib.newevent

from pony.orm import *
from database import RockBurst
from ui.icon import get_art, get_icon
from .list import RbList
from ui.class_config_provider import ClassConfigProvider

from .create import DialogCreateRockBurst
from ui.windows.main.identity import Identity
from ui.delete_object import delete_object

__CONFIG_VERSION__ = 2


RbSelectedEvent, EVT_RB_SELECTED = wx.lib.newevent.NewEvent()

class RbPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        item = self.toolbar.AddTool(
            wx.ID_ADD, "Добавить", get_icon("magic-wand")
        )
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        item = self.toolbar.AddTool(
            wx.ID_EDIT, "Изменить", get_art(wx.ART_EDIT)
        )
        item.Enable(False)
        item = self.toolbar.AddTool(
            wx.ID_DELETE, "Удалить", get_icon('delete')
        )
        item.Enable(False)
        self.toolbar.AddStretchableSpace()
        item = self.toolbar.AddCheckTool(
            wx.ID_FIND, "", get_icon('find')
        )
        self.toolbar.Realize()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)
        self._list = RbList(self)
        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_selected)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()

    @db_session
    def _on_item_selected(self, event):
        item = self._list._list.GetFirstSelected()
        if item == -1:
            return
        _id = self._list._list.GetItemData(item)
        rock_burst = RockBurst[_id]
        print(Identity(rock_burst, rock_burst, None))
        wx.PostEvent(self, RbSelectedEvent(target=self, identity=Identity(rock_burst, rock_burst, None)))

    def _on_add(self, event):
        dlg = DialogCreateRockBurst(self)
        if dlg.ShowModal() == wx.ID_OK:
            self._list._render()

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()

    def remove_selection(self):
        self._list.remove_selection()