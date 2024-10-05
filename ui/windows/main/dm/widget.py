import wx

from pony.orm import *
from ui.icon import get_art, get_icon
from ui.class_config_provider import ClassConfigProvider
from .list import DischargeList
from .discharge import DischargeDetails
from .create_dialog import DialogCreateDischargeSeries


__CONFIG_VERSION__ = 1


class DischargePanel(wx.Panel):
    @db_session
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

        self._current_rid = None

        self.toolbar = wx.ToolBar(self, style=wx.TB_HORZ_TEXT | wx.TB_FLAT)
        item = self.toolbar.AddTool(
            wx.ID_BACKWARD, label="Назад", bitmap=get_art(wx.ART_GO_BACK)
        )
        item.Enable(False)
        self.toolbar.AddSeparator()
        item = self.toolbar.AddTool(wx.ID_ADD, "Добавить", get_icon("magic-wand"))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        item = self.toolbar.AddTool(wx.ID_EDIT, "Изменить", get_art(wx.ART_EDIT))
        item.Enable(False)
        item = self.toolbar.AddTool(wx.ID_DELETE, "Удалить", get_art(wx.ART_DELETE))
        item.Enable(False)
        self.toolbar.AddStretchableSpace()
        item = self.toolbar.AddCheckTool(wx.ID_FIND, "", get_art(wx.ART_FIND))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_back, id=wx.ID_BACKWARD)
        self.toolbar.Realize()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.toolbar, 0, wx.EXPAND)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(top_sizer, 0, wx.EXPAND | wx.BOTTOM, border=2)
        self.SetSizer(main_sizer)

        self._details = DischargeDetails(self, menubar, toolbar, statusbar)

        self._list = DischargeList(self)
        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_item_activated)
        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selection_changed)
        self._list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_selection_changed)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self.main_sizer = main_sizer

        self.Layout()

    def _on_add(self, event):
        dlg = DialogCreateDischargeSeries(self)
        dlg.ShowModal()

    def _on_selection_changed(self, event):
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

    def _on_add_btn(self, event):
        dlg = DialogCreateDischargeSeries(self)
        dlg.ShowModal()

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
            self.main_sizer.Detach(1)
            self.main_sizer.Add(self._details, 1, wx.EXPAND)
            self._list.end()
        self._details.start(rid)
        self._current_rid = rid
        self.Layout()
        self._update_controls_state()

    def _go_to_list(self):
        if self._current_rid != None:
            self.main_sizer.Detach(1)
            self._details.end()
            self.main_sizer.Add(self._list, 1, wx.EXPAND)
            self._list.start()
        self._current_rid = None
        self.Layout()
        self._update_controls_state()

    def _on_back(self, event):
        self._go_to_list()

    def _on_list_item_activated(self, event: wx.ListEvent):
        self._go_to_item(event.GetData())

    def _on_select_box_changed(self, event: wx.CommandEvent):
        self._go_to_item(self._select_box.GetClientData(event.GetInt()))
