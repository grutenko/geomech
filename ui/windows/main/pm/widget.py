import wx
import wx.lib.newevent

from ui.class_config_provider import ClassConfigProvider
from ui.icon import get_icon
from ui.widgets.tree.widget import EVT_WIDGET_TREE_SEL_CHANGED
from pony.orm import *
from database import PMTestSeries
from ..identity import Identity
from .create import DialogCreatePmSeries
from .detail import PmSeriesDetail
from .list import PmList

__CONFIG_VERSION__ = 2

PmSelectedEvent, EVT_PM_SELECTED = wx.lib.newevent.NewEvent()


class PmPanel(wx.Panel):
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent)
        self.menubar = menubar
        self.toolbar = toolbar
        self._statusbar = statusbar
        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)

        self._current_rid = None

        self.local_toolbar = wx.ToolBar(self, style=wx.TB_FLAT)
        item = self.local_toolbar.AddTool(wx.ID_BACKWARD, label="Назад", bitmap=get_icon("undo"))
        item.Enable(False)
        self.local_toolbar.AddSeparator()
        item = self.local_toolbar.AddTool(wx.ID_ADD, "Добавить", get_icon("magic-wand"))
        self.local_toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        item = self.local_toolbar.AddTool(wx.ID_EDIT, "Изменить", get_icon("edit"))
        item.Enable(False)
        item = self.local_toolbar.AddTool(wx.ID_DELETE, "Удалить", get_icon("delete"))
        item.Enable(False)
        self.local_toolbar.AddStretchableSpace()
        item = self.local_toolbar.AddCheckTool(wx.ID_FIND, "", get_icon("find"))
        self.local_toolbar.Bind(wx.EVT_TOOL, self._on_back, id=wx.ID_BACKWARD)
        self.local_toolbar.Realize()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(self.local_toolbar, 0, wx.EXPAND)

        self.local_statusbar = wx.StatusBar(self, style=0)
        main_sizer.Add(self.local_statusbar, 0, wx.EXPAND)
        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(top_sizer, 0, wx.EXPAND | wx.BOTTOM, border=2)
        self.SetSizer(main_sizer)
        self.main_sizer = main_sizer

        self._details = PmSeriesDetail(self, self.menubar, self.toolbar, self._statusbar)
        self._details._tree.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self._on_selection_changed)
        self._list = PmList(self)
        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated)
        self._list.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_selection_changed)
        self._list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self._on_selection_changed)
        main_sizer.Add(self._list, 1, wx.EXPAND)

        self.Layout()

    def _update_controls_state(self):
        self.local_toolbar.EnableTool(wx.ID_BACKWARD, self._current_rid != None)
        self.local_toolbar.EnableTool(wx.ID_ADD, self._current_rid == None)
        self.local_toolbar.EnableTool(wx.ID_FIND, self._current_rid == None)
        self.local_toolbar.EnableTool(
            wx.ID_EDIT,
            self._current_rid == None and self._list._list.GetSelectedItemCount() > 0,
        )
        self.local_toolbar.EnableTool(
            wx.ID_DELETE,
            self._current_rid == None and self._list._list.GetSelectedItemCount() > 0,
        )

    def _on_selection_changed(self, event):
        if self._current_rid == None:
            o = self._list.get_current_o()
        else:
            o = self._details.get_current_sample_set()

        if o != None:
            identity = Identity(o, o, None)
        else:
            identity = None
        wx.PostEvent(self, PmSelectedEvent(target=self, identity=identity))
        self._update_controls_state()

    def _on_item_activated(self, event: wx.ListEvent):
        self._go_to_item(event.GetData())

    def _go_to_item(self, rid):
        if self._current_rid == None:
            self.main_sizer.Detach(3)
            self.main_sizer.Add(self._details, 1, wx.EXPAND)
            self._list.end()
        self._details.start(rid)
        self.local_statusbar.SetStatusText(self._details.get_item_name())
        self._current_rid = rid
        self.Layout()
        self._update_controls_state()

    def _go_to_list(self):
        if self._current_rid != None:
            self.main_sizer.Detach(3)
            self._details.end()
            self.main_sizer.Add(self._list, 1, wx.EXPAND)
            self._list.start()
        self.local_statusbar.SetStatusText("")
        self._current_rid = None
        self.Layout()
        self._update_controls_state()

    def _on_add(self, event):
        dlg = DialogCreatePmSeries(self)
        if dlg.ShowModal() == wx.ID_OK:
            self._list._load()

    def _on_back(self, event):
        self._go_to_list()

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()

    def remove_selection(self, silence=False):
        self._list.remove_selection(silence)

    @db_session
    def open(self, pm_sample_set):
        self._go_to_item(pm_sample_set.pm_test_series.RID)
        self._details.open_pm_sample_set(pm_sample_set)
