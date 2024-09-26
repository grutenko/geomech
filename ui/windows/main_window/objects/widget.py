import wx
import wx.lib.newevent

from ui.class_config_provider import ClassConfigProvider
from ui.windows.main_window.identity import Identity

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

        wnd = wx.SplitterWindow(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(wnd, 1, wx.EXPAND)
        self.tree = TreeWidget(wnd)
        self.related_data = RelatedData(wnd, menubar, toolbar, statusbar)
        wnd.SetSashGravity(0.5)
        wnd.SplitHorizontally(self.tree, self.related_data)
        self.SetSizer(main_sizer)

        self._bind_all()

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
        print(rel_data_o)
        wx.PostEvent(
            self,
            ObjectSelectedEvent(
                target=self, identity=Identity(o_node.o, rel_data_o, rel_data_target)
            ),
        )

    def _on_open_self_editor(self, event):
        self.related_data.open_self_editor()
