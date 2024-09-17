import wx
from typing import List, Tuple
from pony.orm import *

from database import MineObject, Station, BoreHole, OrigSampleSet
import ui.delete_object
from ui.icon import get_icon, get_art
from ui.widgets.tree import *
from ui.widgets.tree.item import TreeNode

from .create_dialogs.dialog_create_bore_hole import DialogCreateBoreHole
from .create_dialogs.dialog_create_mine_object import DialogCreateMineObject
from .create_dialogs.dialog_create_station import DialogCreateStation
from .create_dialogs.dialog_create_orig_sample_set import DialogCreateCore


class _MineObject_Node(TreeNode):
    def __init__(self, o: MineObject):
        self.o = o

    def get_parent(self) -> TreeNode:
        if self.o.parent != None:
            return _MineObject_Node(self.o.parent)
        else:
            return _Root_Node()

    def _get_type_name(self):
        m = {
            "REGION": "Регион",
            "ROCKS": "Горный массив",
            "FIELD": "Месторождение",
            "HORIZON": "Горизонт",
            "EXCAVATION": "Выработка",
        }
        return m[self.o.Type]

    def get_name(self) -> str:
        return '[' + self._get_type_name() + "] " + self.o.Name

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_FOLDER, get_art(wx.ART_FOLDER, 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return wx.ART_FOLDER_OPEN, get_art(wx.ART_FOLDER_OPEN, 16)

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(
            o for o in BoreHole if o.mine_object == self.o and o.station == None
        ):
            nodes.append(_BoreHole_Node(o))
        for o in select(o for o in Station if o.mine_object == self.o):
            nodes.append(_Station_Node(o))
        for o in select(o for o in MineObject if o.parent == self.o):
            nodes.append(_MineObject_Node(o))
        return nodes

    def __eq__(self, node):
        return isinstance(node, _MineObject_Node) and node.o.RID == self.o.RID


class _Station_Node(TreeNode):
    def __init__(self, o: Station):
        self.o = o

    def get_parent(self) -> TreeNode:
        return _MineObject_Node(self.o.mine_object)

    def get_name(self) -> str:
        return "[Станция] " + self.o.Name

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_FOLDER, get_art(wx.ART_FOLDER, 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return wx.ART_FOLDER_OPEN, get_art(wx.ART_FOLDER_OPEN, 16)

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in BoreHole if o.station == self.o):
            nodes.append(_BoreHole_Node(o))
        return nodes

    def __eq__(self, o):
        return isinstance(o, _Station_Node) and o.o.RID == self.o.RID


class _BoreHole_Node(TreeNode):
    def __init__(self, o: BoreHole):
        self.o = o

    def get_parent(self) -> TreeNode:
        if self.o.station != None:
            return _Station_Node(self.o.station)
        else:
            return _MineObject_Node(self.o.mine_object)

    def get_name(self) -> str:
        return "[Скважина] " + self.o.Name

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_FOLDER, get_art(wx.ART_FOLDER, 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return wx.ART_FOLDER_OPEN, get_art(wx.ART_FOLDER_OPEN, 16)

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        core = select(o for o in OrigSampleSet if o.bore_hole == self.o).first()
        if core != None:
            return [_Core_Node(core)]
        else:
            return []

    def __eq__(self, o):
        return isinstance(o, _BoreHole_Node) and o.o.RID == self.o.RID


class _Core_Node(TreeNode):
    def __init__(self, o: OrigSampleSet):
        self.o = o

    def get_parent(self) -> TreeNode:
        return _BoreHole_Node(self.o.bore_hole)

    def get_name(self) -> str:
        return "[Керн]"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_NORMAL_FILE, get_art(wx.ART_NORMAL_FILE, 16)

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return isinstance(node, _Core_Node) and node.o.RID == self.o.RID


class _Root_Node(TreeNode):
    def get_name(self) -> str:
        return "Объекты"

    def get_parent(self) -> TreeNode:
        return _Root_Node()

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in MineObject if o.Level == 0):
            nodes.append(_MineObject_Node(o))
        return nodes

    def __eq__(self, o):
        return isinstance(o, _Root_Node)


class MainWindowTree(Tree):
    def __init__(self, parent):
        super().__init__(parent)
        self.bind_all()
        self.set_root_node(_Root_Node())

        self.Bind(EVT_WIDGET_TREE_MENU, self._on_node_context_menu)

        self._current_object = None
        self._current_node = None

    def _create_node(self, o):
        if isinstance(o, MineObject):
            return _MineObject_Node(o)
        elif isinstance(o, Station):
            return _Station_Node(o)
        elif isinstance(o, BoreHole):
            return _BoreHole_Node(o)
        elif isinstance(o, OrigSampleSet) and o.bore_hole != None:
            return _Core_Node(o)
        return None

    def _mine_object_context_menu(self, node: _MineObject_Node, point: wx.Point):
        self._current_object = node.o
        menu = wx.Menu()
        subnode_menu = wx.Menu()
        m = {
            "REGION": "Регион",
            "ROCKS": "Горный массив",
            "FIELD": "Месторождение",
            "HORIZON": "Горизонт",
            "EXCAVATION": "Выработка",
        }

        if node.o.Type != "EXCAVATION":
            child_mine_object_name = list(m.values()).__getitem__(
                list(m.keys()).index(node.o.Type) + 1
            )
            item = subnode_menu.Append(wx.ID_ANY, child_mine_object_name)
            subnode_menu.Bind(wx.EVT_MENU, self._on_create_mine_object, item)
            subnode_menu.AppendSeparator()

        item = subnode_menu.Append(wx.ID_ANY, "Измерительную станцию")
        subnode_menu.Bind(wx.EVT_MENU, self._on_create_station, item)
        item = subnode_menu.Append(wx.ID_ANY, "Скважину")
        subnode_menu.Bind(wx.EVT_MENU, self._on_create_bore_hole, item)
        menu.AppendSubMenu(subnode_menu, "Добавить")
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Удалить")
        menu.Bind(wx.EVT_MENU, self._on_delete_mine_object, item)
        self.PopupMenu(menu, point)

    def _create_object(self, parent_object, instance_class):
        if instance_class == MineObject:
            dlg = DialogCreateMineObject(self, parent_object)
        elif instance_class == Station:
            dlg = DialogCreateStation(self, self._current_object)
        elif instance_class == BoreHole:
            dlg = DialogCreateBoreHole(self, self._current_object)
        elif instance_class == OrigSampleSet:
            dlg = DialogCreateCore(self, self._current_object)
        if dlg.ShowModal() == wx.ID_OK:
            # Элемент дерева - объект родителя перезагружается из базы данных
            self.soft_reload_childrens(self._current_node)
            self.select_node(self._create_node(dlg.o))

    def _on_create_mine_object(self, event):
        self._create_object(self._current_object, MineObject)

    def _on_create_station(self, event):
        self._create_object(self._current_object, Station)

    def _on_create_bore_hole(self, event):
        self._create_object(self._current_object, BoreHole)

    def _delete_object(self, node):
        if isinstance(node.o, MineObject):
            relations = [
                "childrens",
                "stations",
                "bore_holes",
                "orig_sample_sets",
                "discharge_series",
                "rock_bursts",
            ]
        elif isinstance(node.o, Station):
            relations = ["bore_holes"]
        elif isinstance(node.o, BoreHole):
            relations = ["orig_sample_sets"]
        elif isinstance(node.o, OrigSampleSet):
            relations = ["discharge_series", "discharge_measurements"]

        if ui.delete_object.delete_object(node.o, relations):
            self.soft_reload_childrens(node.get_parent())

    def _on_delete_mine_object(self, event):
        self._delete_object(self._current_node)

    def _station_context_menu(self, node: _Station_Node, point: wx.Point):
        menu = wx.Menu()
        subnode_menu = wx.Menu()
        item = subnode_menu.Append(wx.ID_ANY, "Скважину")
        subnode_menu.Bind(wx.EVT_MENU, self._on_create_bore_hole, item)
        menu.AppendSubMenu(subnode_menu, "Добавить")
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Удалить")
        menu.Bind(wx.EVT_MENU, self._on_delete_bore_hole, item)
        self.PopupMenu(menu, point)

    def _on_delete_station(self, event):
        self._delete_object(self._current_node)

    @db_session
    def _bore_hole_context_menu(self, node: _BoreHole_Node, point: wx.Point):
        self._current_object = node.o
        menu = wx.Menu()
        subnode_menu = wx.Menu()
        core = select(o for o in OrigSampleSet if o.bore_hole == node.o).first()
        if core != None:
            item = subnode_menu.Append(wx.ID_ANY, "(Добавлен) Привязать Керн")
            item.Enable(False)
        else:
            item = subnode_menu.Append(wx.ID_ANY, "Привязать Керн")
            subnode_menu.Bind(wx.EVT_MENU, self._on_create_core, item)
        menu.AppendSubMenu(subnode_menu, "Добавить")
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Удалить")
        menu.Bind(wx.EVT_MENU, self._on_delete_bore_hole, item)
        self.PopupMenu(menu, point)

    def _on_create_core(self, event):
        self._create_object(self._current_object, OrigSampleSet)

    def _on_delete_bore_hole(self, event):
        self._delete_object(self._current_node)

    def _core_context_menu(self, node: _Core_Node, point: wx.Point):
        self._current_object = node.o
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Удалить")
        menu.Bind(wx.EVT_MENU, self._on_delete_core, item)
        self.PopupMenu(menu, point)

    def _on_delete_core(self, event):
        self._delete_object(self._current_node)

    def _open_context_menu(self, node: TreeNode, point: wx.Point):
        self._current_object = node.o
        self._current_node = node
        if isinstance(node, _MineObject_Node):
            self._mine_object_context_menu(node, point)
        elif isinstance(node, _Station_Node):
            self._station_context_menu(node, point)
        elif isinstance(node, _BoreHole_Node):
            self._bore_hole_context_menu(node, point)
        elif isinstance(node, _Core_Node):
            self._core_context_menu(node, point)

    def _on_node_context_menu(self, event):
        self._open_context_menu(event.node, event.point)
