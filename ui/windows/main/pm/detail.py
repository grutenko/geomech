import pubsub
import wx
from pony.orm import *
from pubsub import pub

from database import PMSample, PMSampleSet, PMTestSeries
from ui.delete_object import delete_object
from ui.icon import get_icon
from ui.widgets.tree.widget import (
    EVT_WIDGET_TREE_ACTIVATED,
    EVT_WIDGET_TREE_MENU,
    Tree,
    TreeNode,
)

from ..identity import Identity
from ..notebook.widget import EditorNotebook
from .grid_samples import GridSamples
from .sample_set_dialog import SampleSetDialog


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


class PmSampleSet_Node(Simple_Node):
    def __init__(self, o):
        self.o = o
        super().__init__(self._make_name(), ("file", get_icon("file")), Identity(o, o, None))

    @db_session
    def get_parent(self):
        return PmSampleSetsSection_Node(PMTestSeries[self.o.pm_test_series.RID])

    @db_session
    def _make_name(self):
        name = self.o.Number
        samples_count = select(o for o in PMSample if o.pm_sample_set == self.o).count()
        name += " (Образцов: %d)" % samples_count
        return name


class PmSampleSetsSection_Node(TreeNode):
    def __init__(self, o):
        super().__init__()
        self.o = o

    def get_parent(self):
        return Root_Node(self.o)

    @db_session
    def get_name(self):
        count = select(o for o in PMSampleSet if o.pm_test_series == self.o).count()
        return "Пробы (%d)" % count

    def get_icon(self):
        return "folder", get_icon("folder")

    def get_icon_open(self):
        return "folder-open", get_icon("folder-open")

    @db_session
    def get_subnodes(self):
        nodes = []

        for o in select(o for o in PMSampleSet if o.pm_test_series == self.o).order_by(lambda o: o.Number):
            nodes.append(PmSampleSet_Node(o))
        return nodes

    def __eq__(self, node):
        return isinstance(node, PmSampleSetsSection_Node) and node.o.RID == self.o.RID


class Root_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_parent(self) -> "TreeNode":
        return Root_Node(self.o)

    def get_name(self) -> str:
        return "Объекты"

    @db_session
    def get_subnodes(self):
        nodes = []
        nodes.append(PmSampleSetsSection_Node(self.o))
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
        if isinstance(node, PmSampleSetsSection_Node):
            item = menu.Append(wx.ID_ANY, "Добавить пробу")
            menu.Bind(wx.EVT_MENU, self._on_append_sample_sets, item)
        if isinstance(node, PmSampleSet_Node):
            _n: EditorNotebook = EditorNotebook.get_instance()
            index, page = _n.get_by_identity(Identity(node.identity.o, node.identity.o, PMSample))
            if index != -1:
                title = "Перейти к открытому редактору образцов"
            else:
                title = "Открыть редактор образцов"
            item = menu.Append(wx.ID_ANY, title)
            menu.Bind(wx.EVT_MENU, self._on_open_samples_editor, item)
            menu.AppendSeparator()
            item = menu.Append(wx.ID_ANY, "Изменить")
            menu.Bind(wx.EVT_MENU, self._on_edit_sample_set, item)
            item = menu.Append(wx.ID_ANY, "Удалить")
            menu.Bind(wx.EVT_MENU, self._on_delete_sample_set, item)
        self.PopupMenu(menu, event.point)

    def _on_open_samples_editor(self, event=None):
        node = self._tree.get_current_node()
        _n: EditorNotebook = EditorNotebook.get_instance()
        index, page = _n.get_by_identity(Identity(node.identity.o, node.identity.o, PMSample))
        if index != -1:
            _n.select_by_index(index)
        else:
            _n.add_editor(GridSamples(_n, node.identity.o, self.menubar, self.toolbar, self.statusbar))

    def _on_append_sample_sets(self, event):
        dlg = SampleSetDialog(self, self.o)
        if dlg.ShowModal() == wx.ID_OK:
            node = self._tree.get_current_node()
            self._tree.soft_reload_childrens(node)
            self._tree.soft_reload_node(node)
            self._tree.select_node(PmSampleSet_Node(dlg.o))

    def _on_edit_sample_set(self, event):
        node = self._tree.get_current_node()
        if isinstance(node, PmSampleSet_Node):
            dlg = SampleSetDialog(self, node.o, _type="UPDATE")
            if dlg.ShowModal() == wx.ID_OK:
                self._tree.soft_reload_node(node)

    def _on_delete_sample_set(self, event):
        node = self._tree.get_current_node()
        if isinstance(node, PmSampleSet_Node):

            _n: EditorNotebook = EditorNotebook.get_instance()
            index, page = _n.get_by_identity(Identity(node.identity.o, node.identity.o, PMSample))
            if index != -1:
                wx.MessageBox(
                    "Таблица-редактор для этой пробы открыт.\nЗакройте редактор и повторите удаление.", "Удаление запрещено.", wx.OK | wx.ICON_ERROR
                )
                return

            if delete_object(node.o, ["pm_samples"]):
                node = node.get_parent()
                self._tree.soft_reload_childrens(node)
                self._tree.soft_reload_node(node)
                pub.sendMessage("object.deleted", o=node.o)

    def _on_item_activated(self, event):
        node = self._tree.get_current_node()
        if isinstance(node, PmSampleSet_Node):
            self._on_open_samples_editor()

    def get_current_sample_set(self):
        node = self._tree.get_current_node()
        if isinstance(node, PmSampleSet_Node):
            o = node.o
        else:
            o = None
        return o

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
