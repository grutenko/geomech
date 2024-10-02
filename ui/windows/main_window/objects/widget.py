import wx
import wx.lib.newevent

from ui.class_config_provider import ClassConfigProvider
from ui.windows.main_window.identity import Identity
from ui.icon import get_art

from .tree import TreeWidget, EVT_WIDGET_TREE_SEL_CHANGED, EVT_TREE_OPEN_SELF_EDITOR
from .related_data import RelatedData, EVT_PROPERTIES_PROPERTY_SELECTED

__CONFIG_VERSION__ = 1

ObjectSelectedEvent, EVT_OBJECT_SELECTED = wx.lib.newevent.NewEvent()


class Objects(wx.Panel):
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )
        self._synthetic_sash_pos = False

        wnd = wx.SplitterWindow(self, style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE)
        self.wnd = wnd
        wnd.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGED, self._on_sash_pos_changed)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wnd, 1, wx.EXPAND)
        first_panel = wx.Panel(wnd)
        first_sizer = wx.BoxSizer(wx.VERTICAL)
        first_panel.SetSizer(first_sizer)

        tree_panel = wx.Panel(first_panel)
        tree_sizer = wx.BoxSizer(wx.VERTICAL)
        search_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._tree_search = wx.SearchCtrl(tree_panel)
        menu = wx.Menu()
        item = menu.AppendCheckItem(wx.ID_ANY, "Регионы")
        item.Check(True)
        item = menu.AppendCheckItem(wx.ID_ANY, "Горные массивы")
        item.Check(True)
        item = menu.AppendCheckItem(wx.ID_ANY, "Месторождения")
        item.Check(True)
        item = menu.AppendCheckItem(wx.ID_ANY, "Станции")
        item.Check(True)
        item = menu.AppendCheckItem(wx.ID_ANY, "Скважины")
        item.Check(True)
        self._tree_search.SetMenu(menu)
        self._tree_search.SetDescriptiveText("Введите часть названия")
        search_sizer.Add(self._tree_search, 1, wx.EXPAND | wx.BOTTOM, border=2)
        tree_sizer.Add(search_sizer, 0, wx.EXPAND)
        tree_panel.SetSizer(tree_sizer)
        self.tree = TreeWidget(tree_panel)
        tree_sizer.Add(self.tree, 1, wx.EXPAND)

        first_sizer.Add(tree_panel, 1, wx.EXPAND)

        self.related_data = RelatedData(wnd, menubar, toolbar, statusbar)
        wnd.SetSashGravity(0.5)
        wnd.SetMinimumPaneSize(200)
        wnd.SplitHorizontally(first_panel, self.related_data)
        self.SetSizer(main_sizer)
        if self._config_provider["sash_pos"] != None:
            self._synthetic_sash_pos = True
            self.wnd.SetSashPosition(self._config_provider["sash_pos"])
            self._synthetic_sash_pos = False
        else:
            self._config_provider["sash_pos"] = self.wnd.GetSashPosition()

        self._bind_all()

    def _on_sash_pos_changed(self, event):
        if not self._synthetic_sash_pos:
            self._config_provider["sash_pos"] = self.wnd.GetSashPosition()
            self._config_provider.flush()

    def _bind_all(self):
        self.tree.Bind(EVT_TREE_OPEN_SELF_EDITOR, self._on_open_self_editor)
        self.tree.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self._on_object_selected)
        self.related_data.Bind(
            EVT_PROPERTIES_PROPERTY_SELECTED, self._on_rel_data_sel_changed
        )

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()

    def _on_object_selected(self, event):
        self.related_data.start(event.node.o)

    def _on_rel_data_sel_changed(self, event):
        o_node = self.tree.get_current_node()
        rel_data_o, rel_data_target = self.related_data.get_current_object()
        wx.PostEvent(
            self,
            ObjectSelectedEvent(
                target=self, identity=Identity(o_node.o, rel_data_o, rel_data_target)
            ),
        )

    def _on_open_self_editor(self, event):
        self.related_data.open_self_editor()
