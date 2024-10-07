import wx
from pony.orm import *

from database import *
from ui.widgets.tree import *
from ui.icon import get_art, get_icon
from ui.delete_object import delete_object
from ..dialogs.dialog_create_bore_hole import DialogCreateBoreHole
from ..dialogs.wiz_create_bore_hole import WizCreateBoreHole
from ..dialogs.dialog_create_mine_object import DialogCreateMineObject
from ..dialogs.dialog_create_orig_sample_set import DialogCreateCore
from ..dialogs.dialog_create_station import DialogCreateStation


class _MineObject_Node(TreeNode):
    def __init__(self, o: MineObject, mine_objects_only = False):
        self.o = o
        self._mine_objects_only = mine_objects_only

    @db_session
    def self_reload(self):
        self.o = MineObject[self.o.RID]

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
        return "[" + self._get_type_name() + "] " + self.o.Name

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return 'folder', get_icon('folder', 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return 'folder-open', get_icon('folder-open', 16)

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        if not self._mine_objects_only:
            for o in select(
                o for o in BoreHole if o.mine_object == self.o and o.station == None
            ):
                nodes.append(_BoreHole_Node(o))
            for o in select(o for o in Station if o.mine_object == self.o):
                nodes.append(_Station_Node(o))
        for o in select(o for o in MineObject if o.parent == self.o):
            nodes.append(_MineObject_Node(o, mine_objects_only=self._mine_objects_only))
        return nodes

    def __eq__(self, node):
        return isinstance(node, _MineObject_Node) and node.o.RID == self.o.RID


class _Station_Node(TreeNode):
    def __init__(self, o: Station, root_as_parent=False):
        self.o = o
        self._root_as_parent = root_as_parent

    @db_session
    def self_reload(self):
        self.o = Station[self.o.RID]

    def get_parent(self) -> TreeNode:
        if self._root_as_parent:
            return _StationsRoot_Node()
        return _MineObject_Node(self.o.mine_object)

    def get_name(self) -> str:
        return "[Станция] " + self.o.Name

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return 'folder', get_icon('folder', 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return 'folder-open', get_icon('folder-open', 16)

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in BoreHole if o.station == self.o):
            nodes.append(_BoreHole_Node(o))
        return nodes

    def __eq__(self, o):
        return isinstance(o, _Station_Node) and o.o.RID == self.o.RID


class _BoreHole_Node(TreeNode):
    def __init__(self, o: BoreHole, root_as_parent = False):
        self.o = o
        self._root_as_parent = root_as_parent

    @db_session
    def self_reload(self):
        self.o = BoreHole[self.o.RID]

    def get_parent(self) -> TreeNode:
        if self._root_as_parent:
            return _BoreHolesRoot_Node()
        if self.o.station != None:
            return _Station_Node(self.o.station)
        else:
            return _MineObject_Node(self.o.mine_object)

    def get_name(self) -> str:
        return "[Скважина] " + self.o.Name

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return 'folder', get_icon('folder', 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return 'folder-open', get_icon('folder-open', 16)

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

    @db_session
    def self_reload(self):
        self.o = OrigSampleSet[self.o.RID]

    def get_parent(self) -> TreeNode:
        return _BoreHole_Node(self.o.bore_hole)

    def get_name(self) -> str:
        return "[Керн]"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return 'file', get_icon('file')

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
    
class _MineObjectsRoot_Node(TreeNode):
    def get_name(self) -> str:
        return "Объекты"

    def get_parent(self) -> TreeNode:
        return _MineObjectsRoot_Node()

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in MineObject if o.Level == 0):
            nodes.append(_MineObject_Node(o, mine_objects_only=True))
        return nodes

    def __eq__(self, o):
        return isinstance(o, _MineObjectsRoot_Node)
    
class _StationsRoot_Node(TreeNode):
    def get_name(self) -> str:
        return "Объекты"

    def get_parent(self) -> TreeNode:
        return _StationsRoot_Node()

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in Station).order_by(lambda x: x.StartDate):
            nodes.append(_Station_Node(o, root_as_parent=True))
        return nodes

    def __eq__(self, o):
        return isinstance(o, _StationsRoot_Node)
    
class _BoreHolesRoot_Node(TreeNode):
    def get_name(self) -> str:
        return "Объекты"

    def get_parent(self) -> TreeNode:
        return _BoreHolesRoot_Node()

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in BoreHole).order_by(lambda x: x.StartDate):
            nodes.append(_BoreHole_Node(o, root_as_parent=True))
        return nodes

    def __eq__(self, o):
        return isinstance(o, _BoreHolesRoot_Node)

OpenSelfEditorEvent, EVT_TREE_OPEN_SELF_EDITOR = wx.lib.newevent.NewEvent()

class TreeWidget(Tree):
    def __init__(self, parent):
        super().__init__(parent)
        self.bind_all()
        self.set_root_node(_Root_Node())
        self._mode = 'all'
        self.Bind(EVT_WIDGET_TREE_MENU, self._on_node_context_menu)

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
        item.SetBitmap(get_icon("wand"))
        subnode_menu.Bind(wx.EVT_MENU, self._on_create_bore_hole, item)
        item = menu.AppendSubMenu(subnode_menu, "Добавить")
        item.SetBitmap(get_art(wx.ART_NEW, scale_to=16))
        item = menu.Append(wx.ID_ANY, "Изменить")
        item.SetBitmap(get_icon('edit', scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_open_self_editor, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Удалить")
        item.SetBitmap(get_icon('delete', scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_delete_mine_object, item)
        self.PopupMenu(menu, point)

    def change_mode(self, mode):
        if mode == 'all':
            self.set_root_node(_Root_Node())
        elif mode == 'mine_objects':
            self.set_root_node(_MineObjectsRoot_Node())
        elif mode == 'stations':
            self.set_root_node(_StationsRoot_Node())
        elif mode == 'bore_holes':
            self.set_root_node(_BoreHolesRoot_Node())
        else:
            return
        self._mode = mode

    def _create_object(self, parent_object, instance_class):
        window = wx.GetApp().GetTopWindow().FindFocus().GetTopLevelParent()
        if instance_class == MineObject:
            dlg = DialogCreateMineObject(window, parent_object)
        elif instance_class == Station:
            dlg = DialogCreateStation(window, self._current_object)
        elif instance_class == BoreHole:
            dlg = WizCreateBoreHole(window, self._current_object)
        elif instance_class == OrigSampleSet:
            dlg = DialogCreateCore(window, self._current_object)
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

        if delete_object(node.o, relations):
            self.soft_reload_childrens(node.get_parent())

    def _on_delete_mine_object(self, event):
        self._delete_object(self._current_node)

    def _station_context_menu(self, node: _Station_Node, point: wx.Point):
        menu = wx.Menu()
        subnode_menu = wx.Menu()
        item = subnode_menu.Append(wx.ID_ANY, "Скважину")
        item.SetBitmap(get_icon("wand"))
        subnode_menu.Bind(wx.EVT_MENU, self._on_create_bore_hole, item)
        item = menu.AppendSubMenu(subnode_menu, "Добавить")
        item.SetBitmap(get_art(wx.ART_NEW, scale_to=16))
        item = menu.Append(wx.ID_ANY, "Изменить")
        item.SetBitmap(get_icon('edit', scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_open_self_editor, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Удалить")
        item.SetBitmap(get_icon('delete', scale_to=16))
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
        item = menu.AppendSubMenu(subnode_menu, "Добавить")
        item.SetBitmap(get_art(wx.ART_NEW, scale_to=16))
        item = menu.Append(wx.ID_ANY, "Изменить")
        item.SetBitmap(get_icon('edit', scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_open_self_editor, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Удалить")
        item.SetBitmap(get_icon('delete', scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_delete_bore_hole, item)
        self.PopupMenu(menu, point)

    def _on_create_core(self, event):
        self._create_object(self._current_object, OrigSampleSet)

    def _on_delete_bore_hole(self, event):
        self._delete_object(self._current_node)

    def _core_context_menu(self, node: _Core_Node, point: wx.Point):
        self._current_object = node.o
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Изменить")
        item.SetBitmap(get_icon('edit', scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_open_self_editor, item)
        item = menu.Append(wx.ID_ANY, "Удалить")
        item.SetBitmap(get_icon('delete', scale_to=16))
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

    def reload_object(self, o):
        if isinstance(o, MineObject):
            self.soft_reload_node(_MineObject_Node(o))
        elif isinstance(o, Station):
            self.soft_reload_node(_Station_Node(o))
        elif isinstance(o, BoreHole):
            self.soft_reload_node(_BoreHole_Node(o))
        elif isinstance(o, OrigSampleSet) and o.SampleType == 'CORE':
            self.soft_reload_node(_Core_Node(o))

    def _on_open_self_editor(self, event):
        wx.PostEvent(self, OpenSelfEditorEvent(target=self._current_object))

