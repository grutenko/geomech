import wx
import wx.lib.newevent
from pony.orm import *

from ui.class_config_provider import ClassConfigProvider
from ui.icon import get_art, get_icon
from ui.windows.main.identity import Identity

from .create import DialogCreateDischargeSeries
from .detail import DischargeDetails
from database import OrigSampleSet, DischargeSeries
from .list import DischargeList
import logging

__CONFIG_VERSION__ = 2


DmSelEvent, EVT_Dm_SELECTED = wx.lib.newevent.NewEvent()


class DischargePanel(wx.Panel):
    @db_session
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)

        self._current_rid = None

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        item = self.toolbar.AddTool(wx.ID_BACKWARD, label="Назад", bitmap=get_icon("undo"))
        item.Enable(False)
        self.toolbar.AddSeparator()
        item = self.toolbar.AddTool(wx.ID_ADD, "Добавить", get_icon("wand"))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        item = self.toolbar.AddTool(wx.ID_EDIT, "Изменить", get_icon("edit"))
        item.Enable(False)
        item = self.toolbar.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        item.Enable(False)
        self.toolbar.AddStretchableSpace()
        item = self.toolbar.AddCheckTool(wx.ID_FIND, "", get_icon("filter"))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_back, id=wx.ID_BACKWARD)
        self.toolbar.Realize()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(top_sizer, 0, wx.EXPAND | wx.BOTTOM, border=2)
        self.SetSizer(main_sizer)

        self.statusbar = wx.StatusBar(self, style=0)
        main_sizer.Add(self.statusbar, 0, wx.EXPAND)

        self._details = DischargeDetails(self, menubar, toolbar, statusbar)

        self._list = DischargeList(self)
        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_item_activated)
        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selection_changed)
        self._list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_selection_changed)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self.main_sizer = main_sizer

        self.Layout()

        self._table = {}
        self.itemDataMap = {}

    def _on_add(self, event):
        dlg = DialogCreateDischargeSeries(self)
        dlg.ShowModal()

    def _on_selection_changed(self, event):
        o = self._list.get_current_o()
        if o != None:
            wx.PostEvent(self, DmSelEvent(target=self, identity=Identity(o, o, None)))
        self._update_controls_state()

    def _on_back(self, event):
        self._go_to_list()

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()

    def _on_page_changed(self, event: wx.BookCtrlEvent):
        if self._notebook_configured:
            self._config_provider["notebook_page"] = self._notebook.GetSelection()
            self._config_provider.flush()

    def _on_add_btn(self, event=None, core=None):
        dlg = DialogCreateDischargeSeries(self, suggested_core=core)
        if dlg.ShowModal() == wx.ID_OK:
            self._list._load()

    def _update_controls_state(self):
        self.toolbar.EnableTool(wx.ID_BACKWARD, self._current_rid != None)
        self.toolbar.EnableTool(wx.ID_ADD, self._current_rid == None)
        self.toolbar.EnableTool(wx.ID_FIND, self._current_rid == None)
        self.toolbar.EnableTool(
            wx.ID_EDIT,
            self._current_rid == None and self._list._list.GetSelectedItemCount() > 0,
        )
        self.toolbar.EnableTool(
            wx.ID_DELETE,
            self._current_rid == None and self._list._list.GetSelectedItemCount() > 0,
        )

    def _go_to_item(self, rid):
        if self._current_rid == None:
            self.main_sizer.Detach(3)
            self.main_sizer.Add(self._details, 1, wx.EXPAND)
            self._list.end()
        self._details.start(rid)
        self.statusbar.SetStatusText(self._details.get_item_name())
        self._current_rid = rid
        self.Layout()
        self._update_controls_state()

    def _go_to_list(self):
        if self._current_rid != None:
            self.main_sizer.Detach(3)
            self._details.end()
            self.main_sizer.Add(self._list, 1, wx.EXPAND)
            self._list.start()
        self._current_rid = None
        self.statusbar.SetStatusText("")
        self.Layout()
        self._update_controls_state()

    def _on_back(self, event):
        self._go_to_list()

    def _on_list_item_activated(self, event: wx.ListEvent):
        self._go_to_item(event.GetData())

    def _on_select_box_changed(self, event: wx.CommandEvent):
        self._go_to_item(self._select_box.GetClientData(event.GetInt()))

    def remove_selection(self, silence=False):
        self._list.remove_selection(silence)

    def select_by_identity(self, identity):
        self._list.select_by_identity(identity)

    @db_session
    def open_by_identity(self, identity: Identity):
        if isinstance(identity.rel_data_o, OrigSampleSet):
            series = select(o for o in DischargeSeries if o.orig_sample_set == identity.rel_data_o).first()
            if series != None:
                self._go_to_item(series.RID)
                try:
                    self._details._open_editor()
                except Exception as e:
                    logging.exception(e)

    def create(self, core):
        self._on_add_btn(core=core)

    @db_session
    def delete(self, core):
        self._list.select_by_identity(Identity(core, core))
        self._list._on_delete()
