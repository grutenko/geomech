from typing import List, Tuple

import pubsub
import pubsub.pub
import wx
from pony.orm import commit, db_session, desc, select

from database import (
    BoreHole,
    DischargeMeasurement,
    DischargeSeries,
    MineObject,
    OrigSampleSet,
    PMSample,
    PMSampleSet,
    Station,
)
from ui.delete_object import delete_object
from ui.icon import get_art, get_icon
from ui.widgets.tree import (
    EVT_WIDGET_TREE_ACTIVATED,
    EVT_WIDGET_TREE_MENU,
    Tree,
    TreeNode,
)
from ui.windows.main.identity import Identity

from .bore_hole import DialogCreateBoreHole
from .core import DialogCreateCore
from .mine_object import DialogCreateMineObject
from .station import DialogCreateStation


class _MineObject_Node(TreeNode):
    @db_session
    def __init__(self, o: MineObject, mine_objects_only=False):
        self.o = MineObject[o.RID]
        self.p = self.o.parent
        self._mine_objects_only = mine_objects_only

    @db_session
    def self_reload(self):
        self.o = MineObject[self.o.RID]

    def get_parent(self) -> TreeNode:
        if self.p != None:
            return _MineObject_Node(self.p)
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
        return "folder", get_icon("folder", 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return "folder-open", get_icon("folder-open", 16)

    @db_session(optimistic=False)
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        if not self._mine_objects_only:
            for o in select(o for o in BoreHole if o.mine_object.RID == self.o.RID and o.station == None):
                nodes.append(_BoreHole_Node(o))
            for o in select(o for o in Station if o.mine_object.RID == self.o.RID).order_by(lambda x: desc(x.RID)):
                nodes.append(_Station_Node(o))
        for o in select(o for o in MineObject if o.parent == self.o).order_by(lambda x: desc(x.RID)):
            nodes.append(_MineObject_Node(o, mine_objects_only=self._mine_objects_only))
        return nodes

    def __eq__(self, node):
        return isinstance(node, _MineObject_Node) and node.o.RID == self.o.RID


class _Station_Node(TreeNode):
    @db_session
    def __init__(self, o: Station, root_as_parent=False):
        self.o = Station[o.RID]
        self.p = self.o.mine_object
        self._root_as_parent = root_as_parent

    @db_session
    def self_reload(self):
        self.o = Station[self.o.RID]

    def get_parent(self) -> TreeNode:
        if self._root_as_parent:
            return _StationsRoot_Node()
        return _MineObject_Node(self.p)

    def get_name(self) -> str:
        return "[Станция] " + self.o.Name

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return "folder", get_icon("folder", 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return "folder-open", get_icon("folder-open", 16)

    @db_session(optimistic=False)
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in BoreHole if o.station == self.o).order_by(lambda x: desc(x.RID)):
            nodes.append(_BoreHole_Node(o))
        return nodes

    def __eq__(self, o):
        return isinstance(o, _Station_Node) and o.o.RID == self.o.RID


class _BoreHole_Node(TreeNode):
    @db_session
    def __init__(self, o: BoreHole, root_as_parent=False):
        self.o = BoreHole[o.RID]
        self.p_mine_object = self.o.mine_object
        self.p_station = self.o.station
        self._root_as_parent = root_as_parent

    @db_session
    def self_reload(self):
        self.o = BoreHole[self.o.RID]

    def get_parent(self) -> TreeNode:
        if self._root_as_parent:
            return _BoreHolesRoot_Node()
        if self.p_station != None:
            return _Station_Node(self.p_station)
        else:
            return _MineObject_Node(self.p_mine_object)

    def get_name(self) -> str:
        return "[Скважина] " + self.o.Name

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return "folder", get_icon("folder", 16)

    def get_icon_open(self) -> Tuple[str | wx.Bitmap] | None:
        return "folder-open", get_icon("folder-open", 16)

    @db_session(optimistic=False)
    def get_subnodes(self) -> List[TreeNode]:
        core = select(o for o in OrigSampleSet if o.bore_hole == self.o).first()
        if core != None:
            return [_Core_Node(core)]
        else:
            return []

    def __eq__(self, o):
        return isinstance(o, _BoreHole_Node) and o.o.RID == self.o.RID


class _Core_Node(TreeNode):
    @db_session
    def __init__(self, o: OrigSampleSet):
        self.o = OrigSampleSet[o.RID]
        self.p = self.o.bore_hole

    @db_session
    def self_reload(self):
        self.o = OrigSampleSet[self.o.RID]

    def get_parent(self) -> TreeNode:
        return _BoreHole_Node(self.p)

    def get_name(self) -> str:
        return "[Керн]"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return "file", get_icon("file")

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return isinstance(node, _Core_Node) and node.o.RID == self.o.RID


class _Root_Node(TreeNode):
    def get_name(self) -> str:
        return "Объекты"

    def get_parent(self) -> TreeNode:
        return _Root_Node()

    @db_session(optimistic=False)
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in MineObject if o.Level == 0).order_by(lambda x: desc(x.RID)):
            nodes.append(_MineObject_Node(o))
        return nodes

    def is_root(self) -> bool:
        return True

    def __eq__(self, o):
        return isinstance(o, _Root_Node)


class _MineObjectsRoot_Node(TreeNode):
    def get_name(self) -> str:
        return "Объекты"

    def get_parent(self) -> TreeNode:
        return _MineObjectsRoot_Node()

    @db_session(optimistic=False)
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in MineObject if o.Level == 0).order_by(lambda x: desc(x.RID)):
            nodes.append(_MineObject_Node(o, mine_objects_only=True))
        return nodes

    def is_root(self) -> bool:
        return True

    def __eq__(self, o):
        return isinstance(o, _MineObjectsRoot_Node)


class _StationsRoot_Node(TreeNode):
    def get_name(self) -> str:
        return "Объекты"

    def get_parent(self) -> TreeNode:
        return _StationsRoot_Node()

    @db_session(optimistic=False)
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in Station).order_by(lambda x: desc(x.RID)):
            nodes.append(_Station_Node(o, root_as_parent=True))
        return nodes

    def is_root(self) -> bool:
        return True

    def __eq__(self, o):
        return isinstance(o, _StationsRoot_Node)


class _BoreHolesRoot_Node(TreeNode):
    def get_name(self) -> str:
        return "Объекты"

    def get_parent(self) -> TreeNode:
        return _BoreHolesRoot_Node()

    def is_root(self) -> bool:
        return True

    @db_session(optimistic=False)
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in BoreHole).order_by(lambda x: desc(x.RID)):
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
        self._mode = "all"
        self.Bind(EVT_WIDGET_TREE_MENU, self._on_node_context_menu)
        self.Bind(EVT_WIDGET_TREE_ACTIVATED, self._on_node_activated)

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

    @db_session
    def _on_node_activated(self, event):
        if isinstance(event.node.o, OrigSampleSet) and select(o for o in DischargeSeries if o.orig_sample_set == event.node.o).count() > 0:
            pubsub.pub.sendMessage("cmd.dm.open", target=self, identity=Identity(event.node.o, event.node.o))

    @db_session
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
            child_mine_object_name = list(m.values()).__getitem__(list(m.keys()).index(node.o.Type) + 1)
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
        item.SetBitmap(get_icon("edit", scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_open_self_editor, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Удалить")
        item.SetBitmap(get_icon("delete", scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_delete_mine_object, item)
        menu.AppendSeparator()
        if node.o.Type == "FIELD":
            m = wx.Menu()
            sample_sets = select(o for o in PMSampleSet if o.mine_object == node.o)
            for o in sample_sets:
                count = select(sample for sample in PMSample if sample.pm_sample_set == o).count()
                item = m.Append(wx.ID_ANY, "Дог. %s Проба №%s (образцов: %d)" % (o.pm_test_series.Name, o.Number, count))
                self._on_open_pm_sample_set_bind(m, o)
            menu.AppendSubMenu(m, "ФМС")
        item = menu.Append(wx.ID_ANY, "Сопутствующие материалы")
        item.SetBitmap(get_icon("versions"))
        menu.Bind(wx.EVT_MENU, self._on_open_supplied_data, item)
        self.PopupMenu(menu, point)

    def _on_open_pm_sample_set_bind(self, menu, pm_sample_set):
        def handler(event):
            pubsub.pub.sendMessage("cmd.pm.open", target=self, pm_sample_set=pm_sample_set)

        menu.Bind(wx.EVT_MENU, handler)

    def change_mode(self, mode):
        if mode == "all":
            node = _Root_Node()
        elif mode == "mine_objects":
            node = _MineObjectsRoot_Node()
        elif mode == "stations":
            node = _StationsRoot_Node()
        elif mode == "bore_holes":
            node = _BoreHolesRoot_Node()
        else:
            return
        sel = self.get_current_node()
        self.set_root_node(node)
        if self != None:
            self.select_node(sel)
        self._mode = mode

    def _create_object(self, parent_object, instance_class):
        window = wx.GetApp().GetTopWindow().FindFocus().GetTopLevelParent()
        if instance_class == MineObject:
            dlg = DialogCreateMineObject(window, parent_object)
        elif instance_class == Station:
            dlg = DialogCreateStation(window, self._current_object)
        elif instance_class == BoreHole:
            dlg = DialogCreateBoreHole(window, self._current_object)
        elif instance_class == OrigSampleSet:
            dlg = DialogCreateCore(window, self._current_object)
        if dlg.ShowModal() == wx.ID_OK:
            # Элемент дерева - объект родителя перезагружается из базы данных
            self.soft_reload_childrens(self._current_node)
            self.select_node(self._create_node(dlg.o))
            pubsub.pub.sendMessage("object.added", o=dlg.o)

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
            relations = ["discharge_series", "discharge_measurements", "pm_samples"]

        if delete_object(node.o, relations):
            pubsub.pub.sendMessage("object.deleted", o=node.o)
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
        item.SetBitmap(get_icon("edit", scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_open_self_editor, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Удалить")
        item.SetBitmap(get_icon("delete", scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_delete_station, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Сопутствующие материалы")
        item.SetBitmap(get_icon("versions"))
        menu.Bind(wx.EVT_MENU, self._on_open_supplied_data, item)
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
        item.SetBitmap(get_icon("edit", scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_open_self_editor, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Удалить")
        item.SetBitmap(get_icon("delete", scale_to=16))

        menu.Bind(wx.EVT_MENU, self._on_delete_bore_hole, item)
        menu.AppendSeparator()

        item = menu.Append(wx.ID_ANY, "Сопутствующие материалы")
        item.SetBitmap(get_icon("versions"))
        menu.Bind(wx.EVT_MENU, self._on_open_supplied_data, item)
        self.PopupMenu(menu, point)

    def _on_create_core(self, event):
        self._create_object(self._current_object, OrigSampleSet)

    def _on_delete_bore_hole(self, event):
        self._delete_object(self._current_node)

    @db_session
    def _core_context_menu(self, node: _Core_Node, point: wx.Point):
        self._current_object = node.o
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Изменить")
        item.SetBitmap(get_icon("edit", scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_open_self_editor, item)
        item = menu.Append(wx.ID_ANY, "Удалить")
        item.SetBitmap(get_icon("delete", scale_to=16))
        menu.Bind(wx.EVT_MENU, self._on_delete_core, item)
        menu.AppendSeparator()
        m = wx.Menu()
        series = select(o for o in DischargeSeries if o.orig_sample_set == node.o).first()
        if series == None:
            item = m.Append(wx.ID_ANY, "(Серия не создана) Открыть")
            item.Enable(False)
        else:
            count = select(o for o in DischargeMeasurement if o.orig_sample_set == node.o).count()
            item = m.Append(wx.ID_ANY, "Открыть (замеров: %d)" % count)
        item.SetBitmap(get_icon("book-stack"))
        m.Bind(wx.EVT_MENU, self._on_select_dm, item)
        if series == None:
            item = m.Append(wx.ID_ANY, "(Серия не создана) Удалить серию замеров")
            item.Enable(False)
        else:
            item = m.Append(wx.ID_ANY, "Удалить серию замеров")
            m.Bind(wx.EVT_MENU, self._on_delete_discharge_series, item)
        if series != None:
            item = m.Append(wx.ID_ANY, "(Привязано) Создать серию замеров")
            item.Enable(False)
        else:
            item = m.Append(wx.ID_ANY, "Создать серию замеров")
            m.Bind(wx.EVT_MENU, self._on_create_discharge_series, item)
        menu.AppendSubMenu(m, "Разгрузочные замеры")
        item = menu.Append(wx.ID_ANY, "Сопутствующие материалы")
        item.SetBitmap(get_icon("versions"))
        menu.Bind(wx.EVT_MENU, self._on_open_supplied_data, item)
        self.PopupMenu(menu, point)

    def _on_delete_discharge_series(self, event):
        o = self._current_object
        # Посылаем команду открытия окна создания серии замеров
        pubsub.pub.sendMessage("cmd.dm.delete", target=self, core=o)

    def _on_create_discharge_series(self, event):
        o = self._current_object
        # Посылаем команду открытия окна создания серии замеров
        pubsub.pub.sendMessage("cmd.dm.create", target=self, core=o)
        pubsub.pub.sendMessage("cmd.dm.open", target=self, identity=Identity(o, o, None))

    def _on_select_dm(self, event):
        o = self._current_object
        # Посылаем запрос на открытие вкладки таблицы замеров для этого керна
        pubsub.pub.sendMessage("cmd.dm.open", target=self, identity=Identity(o, o, None))

    def _on_open_supplied_data(self, event):
        pubsub.pub.sendMessage("cmd.supplied_data.show", target=self)

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
            node = _MineObject_Node(o)
        elif isinstance(o, Station):
            node = _Station_Node(o)
        elif isinstance(o, BoreHole):
            node = _BoreHole_Node(o)
        elif isinstance(o, OrigSampleSet) and o.SampleType == "CORE":
            node = _Core_Node(o)
        else:
            return
        self.soft_reload_node(node)

    def _on_open_self_editor(self, event):
        wx.PostEvent(self, OpenSelfEditorEvent(target=self._current_object))

    def select_by_identity(self, identity):
        if isinstance(identity.rel_data_o, MineObject) and self._mode in [
            "all",
            "mine_objects",
        ]:
            node = _MineObject_Node(identity.rel_data_o, mine_objects_only=self._mode == "mine_objects")
        elif isinstance(identity.rel_data_o, Station) and self._mode in [
            "all",
            "stations",
        ]:
            node = _Station_Node(identity.rel_data_o, root_as_parent=self._mode == "stations")
        elif isinstance(identity.rel_data_o, BoreHole) and self._mode in [
            "all",
            "stations",
            "bore_holes",
        ]:
            node = _BoreHole_Node(identity.rel_data_o, root_as_parent=self._mode == "bore_holes")
        elif isinstance(identity.rel_data_o, OrigSampleSet) and self._mode in [
            "all",
            "stations",
            "bore_holes",
        ]:
            node = _Core_Node(identity.rel_data_o)
        else:
            return

        self.select_node(node)
