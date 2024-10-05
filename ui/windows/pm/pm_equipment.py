import wx
import wx.lib.mixins.listctrl as listmix

from pony.orm import *

from database import PmTestEquipment
from ui.icon import get_art
from ui.datetimeutil import decode_date
from ui.delete_object import delete_object

from .pm_equipment_editor import PmEquipmentEditor


class PmEquipment(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._toolbar = wx.ToolBar(
            self, style=wx.TB_FLAT | wx.TB_HORZ_TEXT | wx.TB_BOTTOM
        )
        tool = self._toolbar.AddTool(
            wx.ID_ADD, "Добавить оборудование", get_art(wx.ART_PLUS)
        )
        self._toolbar.Bind(wx.EVT_TOOL, self._on_create, id=wx.ID_ADD)
        tool = self._toolbar.AddTool(
            wx.ID_EDIT, "Редактировать оборудование", get_art(wx.ART_EDIT)
        )
        tool.Enable(False)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_update, id=wx.ID_EDIT)
        tool = self._toolbar.AddTool(
            wx.ID_DELETE, "Удалить оборудование", get_art(wx.ART_DELETE)
        )
        tool.Enable(False)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_delete, id=wx.ID_DELETE)
        self._toolbar.Realize()
        main_sizer.Add(self._toolbar, 0, wx.EXPAND)

        self.table = wx.ListCtrl(
            self, style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_SORT_ASCENDING
        )
        self.table.AppendColumn("Название", width=400)
        self.table.AppendColumn("Серийный номер", width=100)
        self.table.AppendColumn("Дата ввода в экспуатацию", width=150)
        listmix.ColumnSorterMixin.__init__(self, 3)
        self.table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_update)
        self.table.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selection_changed)
        self.table.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_selection_changed)
        self.table.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_item_menu)
        self.table.Bind(wx.EVT_RIGHT_DOWN, self._on_whitespace_right_click)
        main_sizer.Add(self.table, 1, wx.EXPAND)

        self.statusbar = wx.StatusBar(self)
        main_sizer.Add(self.statusbar, 0, wx.EXPAND)

        self.SetSizer(main_sizer)

        self.Layout()
        self.Hide()

        self._methods = {}
        self.itemDataMap = {}
        self._q = ''

    def GetListCtrl(self):
        return self.table

    def start(self):
        self.Show()
        self._render()

    def end(self):
        self.Hide()

    @db_session
    def _render(self):
        self.table.DeleteAllItems()
        equipment = select(o for o in PmTestEquipment)
        self._equipment = {}
        self.itemDataMap = {}
        for index, e in enumerate(equipment):
            self._equipment[e.RID] = e
            item = self.table.InsertItem(index, e.Name)
            self.table.SetItem(item, 1, e.SerialNo)
            self.table.SetItem(item, 2, decode_date(e.StartDate).__str__())
            self.itemDataMap[e.RID] = [
                e.Name,
                e.SerialNo,
                decode_date(e.StartDate).__str__(),
            ]
            self.table.SetItemData(item, e.RID)
        self.statusbar.SetStatusText("Элементов:%d" % len(equipment))
        self._update_controls_state()

    def _on_create(self, event):
        dlg = PmEquipmentEditor(self)
        if dlg.ShowModal() == wx.ID_OK:
            self._render()

    def _on_update(self, event):
        _id = self.table.GetItemData(self.table.GetFirstSelected())
        dlg = PmEquipmentEditor(self, self._equipment[_id], _type="UPDATE")
        if dlg.ShowModal() == wx.ID_OK:
            self._render()

    def _on_selection_changed(self, event):
        self._update_controls_state()

    def _on_item_menu(self, event):
        menu = wx.Menu()
        item = menu.Append(wx.ID_EDIT, "Изменить")
        item.SetBitmap(get_art(wx.ART_EDIT))
        menu.Bind(wx.EVT_MENU, self._on_update, item)
        item = menu.Append(wx.ID_DELETE, "Удалить")
        menu.Bind(wx.EVT_MENU, self._on_delete, item)
        item.SetBitmap(get_art(wx.ART_DELETE))
        self.PopupMenu(menu, event.GetPoint())

    def _on_whitespace_right_click(self, event):
        index, flags = self.table.HitTest(event.GetPosition())
        if index == -1:
            menu = wx.Menu()
            item = menu.Append(wx.ID_ADD, "Добавить")
            item.SetBitmap(get_art(wx.ART_PLUS))
            menu.Bind(wx.EVT_MENU, self._on_create, item)
            self.PopupMenu(menu, event.GetPosition())
        else:
            event.Skip()

    @db_session
    def _on_delete(self, event):
        _id = self.table.GetItemData(self.table.GetFirstSelected())
        e = select(o for o in PmTestEquipment if o.RID == _id).first()
        if e != None:
            if delete_object(e, []):
                self._render()

    def _update_controls_state(self):
        self._toolbar.EnableTool(wx.ID_EDIT, self.table.GetSelectedItemCount() > 0)
        self._toolbar.EnableTool(wx.ID_DELETE, self.table.GetSelectedItemCount() > 0)

    def start_find(self, q):
        self._q = q

    def get_last_q(self):
        return self._q

    def can_find_next(self):
        return False
    
    def find_next(self):
        ...