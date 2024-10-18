import wx
import wx.lib.mixins.listctrl as listmix
from pony.orm import *

from database import PmTestMethod
from ui.datetimeutil import decode_date
from ui.delete_object import delete_object
from ui.icon import get_art

from .pm_method_editor import PmMethodEditor


class PmMethodsPanel(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_HORZ_TEXT | wx.TB_BOTTOM)
        tool = self._toolbar.AddTool(wx.ID_ADD, "Добавить метод", get_art(wx.ART_PLUS))
        self._toolbar.Bind(wx.EVT_TOOL, self._on_create_pm_method, id=wx.ID_ADD)
        tool = self._toolbar.AddTool(wx.ID_EDIT, "Редактировать метод", get_art(wx.ART_EDIT))
        tool.Enable(False)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_item_activated, id=wx.ID_EDIT)
        tool = self._toolbar.AddTool(wx.ID_DELETE, "Удалить метод", get_art(wx.ART_DELETE))
        tool.Enable(False)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_delete_pm_method, id=wx.ID_DELETE)
        self._toolbar.Realize()
        main_sizer.Add(self._toolbar, 0, wx.EXPAND)

        self.table = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_SORT_ASCENDING)
        self.table.AppendColumn("Название", width=400)
        self.table.AppendColumn("Комментарий", width=100)
        self.table.AppendColumn("Дата введения", width=100)
        self.table.AppendColumn("Дата аннулирования", width=150)
        self.table.AppendColumn("Аналитический?", width=120)
        listmix.ColumnSorterMixin.__init__(self, 5)
        self.table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated)
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

        self._q = ""

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
        methods = select(o for o in PmTestMethod)
        self._methods = {}
        self.itemDataMap = {}
        for index, method in enumerate(methods):
            self._methods[method.RID] = method
            item = self.table.InsertItem(index, method.Name)
            self.table.SetItem(item, 1, method.Comment if method.Comment != None else "")
            self.table.SetItem(item, 2, decode_date(method.StartDate).__str__())
            if method.EndDate != None:
                end_date = decode_date(method.EndDate).__str__()
            else:
                end_date = "[Не задано]"
            self.table.SetItem(item, 3, end_date)
            if method.Analytic != None and method.Analytic:
                analytic = "Да"
            else:
                analytic = "Нет"
            self.table.SetItem(item, 4, analytic)
            self.table.SetItemData(item, method.RID)
            self.itemDataMap[method.RID] = [method.Name, decode_date(method.StartDate).__str__(), end_date, analytic]
        self.statusbar.SetStatusText("Элементов:%d" % len(methods))
        self._update_controls_state()

    def _on_whitespace_right_click(self, event: wx.MouseEvent):
        index, flags = self.table.HitTest(event.GetPosition())
        if index == -1:
            menu = wx.Menu()
            item = menu.Append(wx.ID_ADD, "Добавить метод")
            item.SetBitmap(get_art(wx.ART_PLUS))
            menu.Bind(wx.EVT_MENU, self._on_create_pm_method, item)
            self.PopupMenu(menu, event.GetPosition())
        else:
            event.Skip()

    def _on_item_menu(self, event):
        menu = wx.Menu()
        item = menu.Append(wx.ID_EDIT, "Изменить")
        item.SetBitmap(get_art(wx.ART_EDIT))
        menu.Bind(wx.EVT_MENU, self._on_item_activated, item)
        item = menu.Append(wx.ID_DELETE, "Удалить")
        menu.Bind(wx.EVT_MENU, self._on_delete_pm_method, item)
        item.SetBitmap(get_art(wx.ART_DELETE))
        self.PopupMenu(menu, event.GetPoint())

    def _on_create_pm_method(self, event):
        dlg = PmMethodEditor(self)
        if dlg.ShowModal() == wx.ID_OK:
            self._render()

    def _on_item_activated(self, event):
        self._edit_pm_method(self._methods[self.table.GetItemData(self.table.GetFirstSelected())])

    def _edit_pm_method(self, method):
        dlg = PmMethodEditor(self, method, _type="UPDATE")
        if dlg.ShowModal() == wx.ID_OK:
            self._render()

    def _on_selection_changed(self, event):
        self._update_controls_state()

    @db_session
    def _on_delete_pm_method(self, event):
        method_id = self.table.GetItemData(self.table.GetFirstSelected())
        method = select(o for o in PmTestMethod if o.RID == method_id).first()
        if method != None:
            if delete_object(method, ["pm_sample_property_values"]):
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

    def find_next(self): ...
