from typing import List
import wx

from pony.orm import *

from ui.widgets.tree import *
from ui.icon import get_icon, get_art

from database import *
from ui.widgets.tree.item import TreeNode
import ui.delete_object

from .create_rock_burst_dialog import CreateRockBurstDialog
from .create_pm_sample_set_dialog import CreatePmSampleSetDialog
from ui.windows.main_window.dialogs.dialog_create_mine_object import (
    DialogCreateMineObject,
)


class _SelfProps_Node(TreeNode):
    def __init__(self, o):
        self.o = o
        self.target = None

    @db_session
    def self_reload(self):
        self.o = MineObject[self.o.RID]

    def get_name(self) -> str:
        return 'Свойства объекта: "%s"' % self.o.Name

    def get_icon(self):
        return wx.ART_INFORMATION, get_art(wx.ART_INFORMATION, 16)

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return isinstance(node, _SelfProps_Node) and node.o.RID == self.o.RID


class _RockBursts_Node(TreeNode):
    def __init__(self, o):
        self.o = o
        self.target = RockBurst

    def get_parent(self) -> TreeNode:
        return _Root_Node(self.o)

    def get_name(self) -> str:
        return "Горные удары"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_FOLDER, get_art(wx.ART_FOLDER, 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return wx.ART_FOLDER_OPEN, get_art(wx.ART_FOLDER_OPEN, 16)

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in RockBurst if o.mine_object == self.o):
            nodes.append(_RockBurst_Node(o))
        return nodes

    def __eq__(self, node):
        return isinstance(node, _RockBursts_Node) and node.o.RID == self.o.RID


class _RockBurst_Node(TreeNode):
    def __init__(self, o):
        self.o = o
        self.target = None

    @db_session
    def self_reload(self):
        self.o = RockBurst[self.o.RID]

    @db_session
    def self_reload(self):
        self.o = RockBurst[self.o.RID]

    def get_parent(self) -> TreeNode:
        return _RockBursts_Node(self.o.mine_object)

    def get_name(self) -> str:
        return self.o.Name

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_HELP_PAGE, get_art(wx.ART_HELP_PAGE, 16)

    def is_leaf(self):
        return True

    def __eq__(self, node):
        return isinstance(node, _RockBurst_Node) and node.o.RID == self.o.RID


class _SampleSets_Node(TreeNode):
    def __init__(self, o):
        self.o = o
        self.target = PMSampleSet

    def get_name(self) -> str:
        return "[Физ. Мех. Свойства] Пробы"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_FOLDER, get_art(wx.ART_FOLDER, 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return wx.ART_FOLDER_OPEN, get_art(wx.ART_FOLDER_OPEN, 16)

    def __eq__(self, node):
        return isinstance(node, _SampleSets_Node) and node.o.RID == self.o.RID

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in PMSampleSet if o.mine_object == self.o):
            nodes.append(_SampleSet_Node(o))
        return nodes


class _SampleSet_Node(TreeNode):
    def __init__(self, o):
        self.o = o
        self.target = None

    @db_session
    def self_reload(self):
        self.o = PMSampleSet[self.o.RID]

    def get_name(self) -> str:
        return "[Физ. Мех. Свойства] Пробы"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_FOLDER, get_art(wx.ART_FOLDER, 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return wx.ART_FOLDER_OPEN, get_art(wx.ART_FOLDER_OPEN, 16)

    def __eq__(self, node):
        return isinstance(node, _SampleSet_Node) and node.o.RID == self.o.RID


class _Root_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "Объекты"

    def get_subnodes(self) -> List[TreeNode]:
        nodes = [_SelfProps_Node(self.o)]
        if self.o.Type == "FIELD":
            nodes.append(_RockBursts_Node(self.o))
            nodes.append(_SampleSets_Node(self.o))
        return nodes

    def __eq__(self, node):
        return isinstance(node, _Root_Node)


class MineObjectProperties(wx.Panel):
    def __init__(self, parent, menubar, statusbar):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self._tree = Tree(self)
        self._tree.Bind(EVT_WIDGET_TREE_MENU, self._on_context_menu)
        main_sizer.Add(self._tree, 1, wx.EXPAND)

        self.Layout()

        self._tree.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self._on_node_selected)
        self._tree.Bind(EVT_WIDGET_TREE_ACTIVATED, self._on_tree_item_activated)

        self._current_node = None
        self._current_object = None
        self._handler_properties_object_seleted = None
        self._handler_properties_target_updated = None


    def _on_tree_item_activated(self, event):
        self._edit_node(event.node)

    @db_session
    def _edit_node(self, node):
        if isinstance(node, _RockBurst_Node):
            dlg = CreateRockBurstDialog(self, node.o, _type="UPDATE")
        elif isinstance(node, _SelfProps_Node):
            dlg = DialogCreateMineObject(self, node.o, _type="UPDATE")
        else:
            return
        if dlg.ShowModal() == wx.ID_OK:
            self._tree.soft_reload_node(node)
            if isinstance(node, _SelfProps_Node):
                if self._handler_properties_target_updated != None:
                    self._handler_properties_target_updated(self.o)
                self.o = MineObject[self.o.RID]


    def start(
        self,
        o: MineObject,
        on_properties_object_selected=None,
        on_properties_target_updated=None,
    ):
        self._handler_properties_object_seleted = on_properties_object_selected
        self._handler_properties_target_updated = on_properties_target_updated
        self.o = o
        self._tree.set_root_node(_Root_Node(o))
        self._tree.bind_all()
        self.Show()
        self._tree.select_node(_SelfProps_Node(self.o))

    def end(self):
        self._handler_properties_object_seleted = None
        self.Hide()
        self._tree.unbind_all()
        self.o = None

    def _rock_bursrts_context_menu(self, node, point):
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Добавить Горный удар")
        menu.Bind(wx.EVT_MENU, self._on_create_rock_burst, item)
        self.PopupMenu(menu)

    def _create_node(self, o):
        if isinstance(o, RockBurst):
            return _RockBurst_Node(o)

    def _create_object(self, instance_class):
        if instance_class == RockBurst:
            dlg = CreateRockBurstDialog(self, self._current_object)
        elif instance_class == PMSampleSet:
            dlg = CreatePmSampleSetDialog(self, self._current_object)
        else:
            return
        if dlg.ShowModal() == wx.ID_OK:
            self._tree.soft_reload_childrens(self._current_node)
            self._tree.select_node(self._create_node(dlg.o))

    def _delete_node(self, node):
        if isinstance(node.o, RockBurst):
            relations = []
        else:
            return
        if ui.delete_object.delete_object(node.o, relations):
            self._tree.soft_reload_childrens(node.get_parent())

    def _on_create_rock_burst(self, event):
        self._create_object(RockBurst)

    def _rock_burst_context_menu(self, node, point):
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Удалить")
        menu.Bind(wx.EVT_MENU, self._on_delete_rock_burst, item)
        self.PopupMenu(menu)

    def _pm_sample_sets_context_menu(self, node, point):
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Добавить Пробу")
        menu.Bind(wx.EVT_MENU, self._on_create_pm_sample_set, item)
        self.PopupMenu(menu)

    def _on_create_pm_sample_set(self, event):
        self._create_object(PMSampleSet)

    def _on_delete_rock_burst(self, event):
        self._delete_node(self._current_node)

    def _on_context_menu(self, event):
        self._current_node = event.node
        self._current_object = event.node.o
        if isinstance(event.node, _RockBursts_Node):
            self._rock_bursrts_context_menu(event.node, event.point)
        elif isinstance(event.node, _RockBurst_Node):
            self._rock_burst_context_menu(event.node, event.point)
        elif isinstance(event.node, _SampleSets_Node):
            self._pm_sample_sets_context_menu(event.node, event.point)
        else:
            return

    def _on_node_selected(self, event):
        object = None
        bounds = None
        if event.node != None:
            if isinstance(event.node, _SelfProps_Node):
                object = self.o
                bounds = None
            elif isinstance(event.node, _RockBursts_Node):
                object = self.o
                bounds = RockBurst
            elif isinstance(event.node, _RockBurst_Node):
                object = event.node.o
                bounds = None
            elif isinstance(event.node, _SampleSets_Node):
                object = self.o
                bounds = PMSampleSet

        if self._handler_properties_object_seleted != None and object != None:
            self._handler_properties_object_seleted(object, bounds)

    def open_self_props_editor(self):
        self._edit_node(_SelfProps_Node(self.o))

    def get_current_object(self):
        node = self._tree.get_current_node()
        if node != None:
            return node.o, node.target
        return None