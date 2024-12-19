import pubsub
import wx
from pony.orm import *

from database import PMSample, PmSamplePropertyValue, PMSampleSet, PMTestSeries
from ui.icon import get_icon
from ui.widgets.tree.widget import (
    EVT_WIDGET_TREE_ACTIVATED,
    EVT_WIDGET_TREE_MENU,
    Tree,
    TreeNode,
)

from ..identity import Identity
from ..notebook.widget import EditorNotebook
from .grid_sample_sets import PmSampleSetsEditor
from .grid_sample_test_values import GridSampleTests
from .grid_samples import PmSampleEditor


class Simple_Node(TreeNode):
    def __init__(self, name, icon, identity):
        self.name = name
        self.icon = icon
        self.identity = identity

    def set_name(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_icon(self):
        return self.icon

    def get_icon_open(self):
        return self.icon

    def is_leaf(self):
        return True

    def __eq__(self, node):
        return isinstance(node, Simple_Node) and node.identity.__eq__(self.identity)


class _PmSamplesSets_Node(Simple_Node):
    def __init__(self, _series):
        super().__init__(self._make_name(_series), ("table", get_icon("table")), Identity(_series, _series, PMSampleSet))

    @db_session
    def _make_name(self, _series):
        count = select(o for o in PMSampleSet if o.pm_test_series == _series).count()
        return "Пробы (%d)" % count


class _PmSamples_Node(Simple_Node):
    def __init__(self, _series):
        super().__init__(self._make_name(_series), ("table", get_icon("table")), Identity(_series, _series, PMSample))

    @db_session
    def _make_name(self, _series):
        count = select(o for o in PMSample if o.pm_sample_set.pm_test_series == _series).count()
        return "Образцы (%d)" % count


class _PmSampleTestValues(Simple_Node):
    def __init__(self, _series):
        super().__init__(self._make_name(_series), ("table", get_icon("table")), Identity(_series, _series, PmSamplePropertyValue))

    @db_session
    def _make_name(self, _series):
        return "Значения свойств для образцов"


class Root_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_parent(self) -> "TreeNode":
        return TreeNode(self.o)

    def get_name(self) -> str:
        return "Объекты"

    @db_session
    def get_subnodes(self):
        nodes = []
        nodes.append(_PmSamplesSets_Node(self.o))
        nodes.append(_PmSamples_Node(self.o))
        nodes.append(_PmSampleTestValues(self.o))
        return nodes

    def is_root(self):
        return True

    def __eq__(self, node):
        return isinstance(node, Root_Node)


class PmSeriesDetail(wx.Panel):
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent)
        self.o = None
        self.menubar = menubar
        self.toolbar = toolbar
        self.statusbar = statusbar

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._tree = Tree(self)
        main_sizer.Add(self._tree, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()
        self.Hide()

        pubsub.pub.subscribe(self._on_editor_saved, "editor.saved")

    def _on_editor_saved(self, target, editor):
        if self.o != None:
            _id = editor.get_identity()
            _pm_sample_set_id = Identity(self.o, self.o, PMSampleSet)
            _pm_sample_id = Identity(self.o, self.o, PMSample)
            if editor != None and _id != None and (_id.__eq__(_pm_sample_set_id) or _id.__eq__(_pm_sample_id)):
                self._render()

    def _on_item_menu(self, event):
        menu = wx.Menu()
        node = event.node
        if isinstance(node, _PmSamplesSets_Node):
            index, _ = EditorNotebook.get_instance().get_by_identity(Identity(self.o, self.o, PMSampleSet))
            if index == -1:
                item = menu.Append(wx.ID_OPEN, "Открыть редактор")
            else:
                item = menu.Append(wx.ID_OPEN, "Перейти к открытому редактору")
            menu.Bind(wx.EVT_MENU, self._on_open_sample_sets, item)
        if isinstance(node, _PmSamples_Node):
            index, _ = EditorNotebook.get_instance().get_by_identity(Identity(self.o, self.o, PMSample))
            if index == -1:
                item = menu.Append(wx.ID_OPEN, "Открыть редактор")
            else:
                item = menu.Append(wx.ID_OPEN, "Перейти к открытому редактору")
            menu.Bind(wx.EVT_MENU, self._on_open_samples, item)
        if isinstance(node, _PmSampleTestValues):
            index, _ = EditorNotebook.get_instance().get_by_identity(Identity(self.o, self.o, PmSamplePropertyValue))
            if index == -1:
                item = menu.Append(wx.ID_OPEN, "Открыть редактор")
            else:
                item = menu.Append(wx.ID_OPEN, "Перейти к открытому редактору")
            menu.Bind(wx.EVT_MENU, self._on_open_sample_propety_values, item)
        self.PopupMenu(menu, event.point)

    def _on_add_values_by_method(self, event): ...

    def _on_item_activated(self, event):
        if isinstance(event.node, _PmSamplesSets_Node):
            self._on_open_sample_sets(event)
        if isinstance(event.node, _PmSamples_Node):
            self._on_open_samples(event)
        if isinstance(event.node, _PmSampleTestValues):
            self._on_open_sample_propety_values(event)

    def _on_open_sample_propety_values(self, event):
        n = EditorNotebook.get_instance()
        _id = Identity(self.o, self.o, PmSamplePropertyValue)
        if not n.select_by_identity(_id):
            n.add_editor(GridSampleTests(n, _id, self.o, self.menubar, self.toolbar, self.statusbar))

    def _on_open_samples(self, event):
        n = EditorNotebook.get_instance()
        _id = Identity(self.o, self.o, PMSample)
        if not n.select_by_identity(_id):
            n.add_editor(PmSampleEditor(n, _id, self.menubar, self.toolbar, self.statusbar))

    def _on_open_sample_sets(self, event):
        n = EditorNotebook.get_instance()
        _id = Identity(self.o, self.o, PMSampleSet)
        if not n.select_by_identity(_id):
            n.add_editor(PmSampleSetsEditor(n, _id, self.menubar, self.toolbar, self.statusbar))

    def get_item_name(self):
        if self.o != None:
            return self.o.get_tree_name()
        return ""

    def _render(self):
        self._tree.set_root_node(Root_Node(self.o))

    @db_session
    def start(self, rid):
        self.o = PMTestSeries[rid]
        self.rid = self.o.RID
        self._render()
        self.Show()
        self._tree.bind_all()
        self._tree.Bind(EVT_WIDGET_TREE_ACTIVATED, self._on_item_activated)
        self._tree.Bind(EVT_WIDGET_TREE_MENU, self._on_item_menu)

    def end(self):
        self.o = None
        self.rid = None
        self.Hide()
        self._tree.unbind_all()
        self._tree.Unbind(EVT_WIDGET_TREE_ACTIVATED, handler=self._on_item_activated)
        self._tree.Unbind(EVT_WIDGET_TREE_MENU, handler=self._on_item_menu)
