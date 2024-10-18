import pubsub
import pubsub.pub
import wx
import wx.dataview
from pony.orm import *

from database import MineObject, RockBurst
from ui.class_config_provider import ClassConfigProvider
from ui.datetimeutil import decode_datetime
from ui.delete_object import delete_object
from ui.icon import get_icon
from ui.windows.main.identity import Identity

from .rock_burst import DialogCreateRockBurst

__CONFIG_VERSION__ = 2


RbSelectedEvent, EVT_RB_SELECTED = wx.lib.newevent.NewEvent()


class RbPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.TB_FLAT)
        item = self.toolbar.AddTool(wx.ID_ADD, "Добавить", get_icon("magic-wand"))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        item = self.toolbar.AddTool(wx.ID_EDIT, "Изменить", get_icon("edit"))
        item.Enable(False)
        item = self.toolbar.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        item.Enable(False)
        self.toolbar.AddStretchableSpace()
        item = self.toolbar.AddCheckTool(wx.ID_FIND, "", get_icon("find"))
        self.toolbar.Realize()
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)

        self.list = wx.dataview.DataViewListCtrl(self, style=wx.dataview.DV_ROW_LINES)
        self.list.AppendBitmapColumn("", 0, width=20, flags=0)
        column = self.list.AppendTextColumn("Название", 1, width=350)
        column.SetSortable(sortable=True)
        column = self.list.AppendDateColumn("Дата события", 2)
        column.SetSortable(sortable=True)
        column = self.list.AppendTextColumn("Месторождение", 3)
        column.SetSortable(sortable=True)
        main_sizer.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(main_sizer)
        self.Layout()
        self._bind_all()
        self.render()

    def _bind_all(self):
        self.list.Bind(wx.dataview.EVT_DATAVIEW_ITEM_CONTEXT_MENU, self._on_item_context_menu)
        self.list.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self._on_selection_changed)

    def _on_selection_changed(self, event):
        index = self.list.GetSelectedRow()
        if index != wx.NOT_FOUND:
            o = self.items[index]
            identity = Identity(o, o, None)
        else:
            identity = None
        wx.PostEvent(self, RbSelectedEvent(target=self, identity=identity))
        self._update_controls_state()

    def _on_item_context_menu(self, event: wx.dataview.DataViewEvent):
        item = event.GetItem()
        menu = wx.Menu()
        if item.IsOk():
            item = menu.Append(wx.ID_ANY, "Изменить")
            item.SetBitmap(get_icon("edit"))
            menu.Bind(wx.EVT_MENU, self._on_edit, item)
            item = menu.Append(wx.ID_ANY, "Удалить")
            item.SetBitmap(get_icon("file-delete"))
            menu.Bind(wx.EVT_MENU, self._on_delete, item)
            menu.AppendSeparator()
            item = menu.Append(wx.ID_ADD, "Добавить горный удар")
            item.SetBitmap(get_icon("file-add"))
            menu.Bind(wx.EVT_MENU, self._on_add, item)
            sub = wx.Menu()
            item = sub.Append(wx.ID_ANY, 'Показать в "Объектах"')
            sub.Bind(wx.EVT_MENU, self._on_select_mine_object, item)
            item.SetBitmap(get_icon("share"))
            menu.AppendSubMenu(sub, "[Горный объект]")
            menu.AppendSeparator()
            item = menu.Append(wx.ID_ANY, "Сопутствующие материалы")
            item.SetBitmap(get_icon("versions"))
            menu.Bind(wx.EVT_MENU, self._on_open_supplied_data, item)
        else:
            item = menu.Append(wx.ID_ADD, "Добавить горный удар")
            item.SetBitmap(get_icon("file-add"))
            menu.Bind(wx.EVT_MENU, self._on_add, item)

        self.PopupMenu(menu, event.GetPosition())

    @db_session
    def _on_select_mine_object(self, event):
        index = self.list.GetSelectedRow()
        if index != wx.NOT_FOUND:
            mine_object = MineObject[self.items[index].mine_object.RID]
            pubsub.pub.sendMessage("cmd.object.select", target=self, identity=Identity(mine_object, mine_object, None))

    def _on_open_supplied_data(self, event):
        pubsub.pub.sendMessage("cmd.supplied_data.show", target=self)

    def _on_add(self, event):
        dlg = DialogCreateRockBurst(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.render()

    def _on_edit(self, event):
        index = self.list.GetSelectedRow()
        dlg = DialogCreateRockBurst(self, self.items[index], _type="UPDATE")
        if dlg.ShowModal() == wx.ID_OK:
            self.render()

    def _on_delete(self, event):
        index = self.list.GetSelectedRow()
        if delete_object(self.items[index], []):
            self.render()
            wx.PostEvent(self, RbSelectedEvent(target=self, identity=None))

    def _update_controls_state(self):
        index = self.list.GetSelectedRow()
        self.toolbar.EnableTool(wx.ID_EDIT, index != wx.NOT_FOUND)
        self.toolbar.EnableTool(wx.ID_DELETE, index != wx.NOT_FOUND)

    @db_session
    def render(self):
        self.list.DeleteAllItems()
        m = [
            "REGION",
            "ROCKS",
            "FIELD",
            "HORIZON",
            "EXCAVATION",
        ]
        self.items = []
        for o in select(o for o in RockBurst).order_by(lambda x: desc(x.RID)):
            self.items.append(o)
            _row = []
            _row.append(wx.Icon(get_icon("file")))
            _row.append(o.Name)
            _row.append(decode_datetime(o.BurstDate))
            mine_object = o.mine_object
            _target_index = m.index("FIELD")
            if mine_object.Type in m:
                while m.index(mine_object.Type) > _target_index:
                    mine_object = mine_object.parent
            _row.append(mine_object.Name)
            self.list.AppendItem(_row)

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()

    def remove_selection(self, silence=False):
        self.list.UnselectAll()
