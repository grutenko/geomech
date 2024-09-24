import wx
import wx

from pony.orm import *

from ui.widgets.tree import *
from ui.icon import get_icon, get_art
from ui.windows.main_window.create_dialogs.dialog_create_bore_hole import (
    DialogCreateBoreHole,
)

from database import BoreHole


class _SelfProps_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    @db_session
    def self_reload(self):
        self.o = BoreHole[self.o.RID]

    def get_name(self) -> str:
        return 'Свойства объекта: "%s"' % self.o.Name

    def get_icon(self):
        return wx.ART_INFORMATION, get_art(wx.ART_INFORMATION, 16)

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return isinstance(node, _SelfProps_Node) and node.o.RID == self.o.RID


class _Root_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "Объекты"

    def get_subnodes(self) -> List[TreeNode]:
        return [
            _SelfProps_Node(self.o),
        ]

    def __eq__(self, node):
        return isinstance(node, _Root_Node)


class BoreHoleProperties(wx.Panel):
    def __init__(self, parent, menubar, statusbar):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self._tree = Tree(self)
        main_sizer.Add(self._tree, 1, wx.EXPAND)

        self.Layout()

        self._handler_properties_object_seleted = None
        self._handler_properties_target_updated = None

        self._tree.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self._on_node_selected)
        self._tree.Bind(EVT_WIDGET_TREE_ACTIVATED, self._on_node_activated)

    def start(
        self,
        o: BoreHole,
        on_properties_object_selected=None,
        on_properties_target_updated=None,
    ):
        self.o = o
        self._handler_properties_object_seleted = on_properties_object_selected
        self._handler_properties_target_updated = on_properties_target_updated
        self._tree.set_root_node(_Root_Node(o))
        self._tree.bind_all()
        self.Show()
        self._tree.select_node(_SelfProps_Node(self.o))

    def end(self):
        self.o = None
        self._handler_properties_object_seleted = None
        self.Hide()
        self._tree.unbind_all()

    def _on_node_activated(self, event):
        if isinstance(event.node, _SelfProps_Node):
            self.open_self_props_editor()

    def _on_node_selected(self, event):
        object = None
        bounds = None
        if event.node != None:
            if isinstance(event.node, _SelfProps_Node):
                object = self.o
                bounds = None

        if self._handler_properties_object_seleted != None and object != None:
            self._handler_properties_object_seleted(object, bounds)

    @db_session
    def open_self_props_editor(self):
        dlg = DialogCreateBoreHole(self, self.o, "UPDATE")
        if dlg.ShowModal() == wx.ID_OK:
            self._tree.soft_reload_node(_SelfProps_Node(self.o))
            self.o = BoreHole[self.o.RID]
