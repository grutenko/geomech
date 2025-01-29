import wx
import wx.lib.mixins.listctrl as listmix
from pony.orm import db_session, select

from database import PmPropertyClass
from ui.delete_object import delete_object
from ui.icon import get_icon

from .property_class_editor import PmPropertyClassEditor


class PropertyClasses(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_HORZ_TEXT | wx.TB_BOTTOM)
        tool = self._toolbar.AddTool(wx.ID_ADD, "Добавить класс", get_icon("add-row"))
        self._toolbar.Bind(wx.EVT_TOOL, self._on_create, id=wx.ID_ADD)
        tool = self._toolbar.AddTool(wx.ID_EDIT, "Редактировать класс", get_icon("edit"))
        tool.Enable(False)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_item_activated, id=wx.ID_EDIT)
        tool = self._toolbar.AddTool(wx.ID_DELETE, "Удалить класс", get_icon("delete"))
        tool.Enable(False)
        self._toolbar.Bind(wx.EVT_TOOL, self._on_delete, id=wx.ID_DELETE)
        self._toolbar.Realize()
        main_sizer.Add(self._toolbar, 0, wx.EXPAND)

        self.table = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_SORT_ASCENDING)
        self.table.AppendColumn("Название", width=400)
        self.table.AppendColumn("Комментарий", width=100)
        self.table.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated)
        self.table.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selection_changed)
        self.table.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_selection_changed)
        self.table.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_item_menu)
        self.table.Bind(wx.EVT_RIGHT_DOWN, self._on_whitespace_right_click)
        listmix.ColumnSorterMixin.__init__(self, 2)
        main_sizer.Add(self.table, 1, wx.EXPAND)

        self.SetSizer(main_sizer)
        self.Layout()

        self._classes = {}
        self.itemDataMap = {}

        self._q = ""

        self.load()

    def GetListCtrl(self):
        return self.table

    def _update_controls_state(self):
        self._toolbar.EnableTool(wx.ID_EDIT, self.table.GetSelectedItemCount() > 0)
        self._toolbar.EnableTool(wx.ID_DELETE, self.table.GetSelectedItemCount() > 0)

    @db_session
    def load(self):
        self.table.DeleteAllItems()

        self._classes = {}
        self.itemDataMap = {}

        for index, o in enumerate(select(o for o in PmPropertyClass)):
            self._classes[o.RID] = o
            item = self.table.InsertItem(index, o.Name)
            self.table.SetItem(item, 1, o.Comment if o.Comment != None else "")
            self.table.SetItemData(item, o.RID)
            self.itemDataMap[o.RID] = [o.Name, o.Comment]

        self._update_controls_state()

    def _on_selection_changed(self, event):
        self._update_controls_state()

    def _on_item_menu(self, event):
        menu = wx.Menu()
        item = menu.Append(wx.ID_EDIT, "Изменить")
        item.SetBitmap(get_icon("edit"))
        menu.Bind(wx.EVT_MENU, self._on_item_activated, item)
        item = menu.Append(wx.ID_DELETE, "Удалить")
        menu.Bind(wx.EVT_MENU, self._on_delete, item)
        item.SetBitmap(get_icon("delete"))
        self.PopupMenu(menu, event.GetPoint())

    @db_session
    def _on_delete(self, event):
        _id = self.table.GetItemData(self.table.GetFirstSelected())
        o = select(o for o in PmPropertyClass if o.RID == _id).first()
        if o != None:
            if delete_object(o, ["pm_properties"]):
                self.load()

    def _on_whitespace_right_click(self, event):
        index, flags = self.table.HitTest(event.GetPosition())
        if index == -1:
            menu = wx.Menu()
            item = menu.Append(wx.ID_ADD, "Добавить класс")
            item.SetBitmap(get_icon("file-add"))
            menu.Bind(wx.EVT_MENU, self._on_create, item)
            self.PopupMenu(menu, event.GetPosition())
        else:
            event.Skip()

    def _on_create(self, event):
        dlg = PmPropertyClassEditor(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.load()

    def _on_item_activated(self, event):
        index = self.table.GetFirstSelected()
        _id = self.table.GetItemData(index)

        dlg = PmPropertyClassEditor(self, self._classes[_id], _type="UPDATE")
        if dlg.ShowModal() == wx.ID_OK:
            self.load()
