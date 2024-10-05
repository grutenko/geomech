import wx

from pony.orm import *
from ui.icon import get_art
from ui.class_config_provider import ClassConfigProvider
from .list import DischargeList
from .discharge import DischargeDetails
from .create_discharge_wizard import run


__CONFIG_VERSION__ = 1

class DischargePanel(wx.Panel):
    @db_session
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

        self._current_rid = None

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._select_box = wx.ComboBox(self)
        self._back_btn = wx.BitmapButton(self, bitmap=get_art(wx.ART_GO_BACK))
        self._back_btn.Disable()
        self._back_btn.Bind(wx.EVT_BUTTON, self._on_back)
        top_sizer.Add(self._back_btn, 0, wx.EXPAND)
        top_sizer.Add(self._select_box, 1, wx.EXPAND)
        self._add_btn = wx.BitmapButton(self, bitmap=get_art(wx.ART_NEW))
        self._add_btn.Bind(wx.EVT_BUTTON, self._on_add_btn)
        top_sizer.Add(self._add_btn, 0, wx.EXPAND)
        self._select_box.Bind(wx.EVT_COMBOBOX, self._on_select_box_changed)
        main_sizer.Add(top_sizer, 0, wx.EXPAND | wx.BOTTOM, border=2)
        self.SetSizer(main_sizer)

        self._details = DischargeDetails(self, menubar, toolbar, statusbar)

        self._list = DischargeList(self)
        for o in self._list.get_items():
            self._select_box.Append(o.Name, o.RID)
        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_list_item_activated)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self.main_sizer = main_sizer

        self.Layout()

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
        run()

    def _go_to_item(self, rid):
        if self._current_rid == None:
            self.main_sizer.Detach(1)
            self.main_sizer.Add(self._details, 1, wx.EXPAND)
            self._list.end()
        index = -1
        for _i in range(self._select_box.GetCount()):
            if rid == self._select_box.GetClientData(_i):
                index = _i
                break
        self._select_box.SetSelection(index)
        self._back_btn.Enable()
        self._add_btn.Disable()
        self._details.start(rid)
        self._current_rid = rid
        self.Layout()

    def _go_to_list(self):
        if self._current_rid != None:
            self.main_sizer.Detach(1)
            self._details.end()
            self.main_sizer.Add(self._list, 1, wx.EXPAND)
            self._list.start()
        self._select_box.SetSelection(-1)
        self._back_btn.Disable()
        self._add_btn.Enable()
        self._current_rid = None
        self.Layout()

    def _on_back(self, event):
        self._go_to_list()

    def _on_list_item_activated(self, event: wx.ListEvent):
        print(event.GetData())
        self._go_to_item(event.GetData())

    def _on_select_box_changed(self, event: wx.CommandEvent):
        self._go_to_item(self._select_box.GetClientData(event.GetInt()))
