import wx
import wx.lib.newevent
from pony.orm import db_session, select
from database import PMSampleSet, PMSample
from ui.widgets.tree import Tree, TreeNode, EVT_WIDGET_TREE_MENU, EVT_WIDGET_TREE_ACTIVATED, EVT_WIDGET_TREE_SEL_CHANGED
from ui.windows.main.pm.sample_set_dialog import SampleSetDialog
from .pm_sample_dialog import PmSampleDialog
from ui.icon import get_icon
from ui.delete_object import delete_object

PmSampleSetActivate, EVT_PM_SAMPLE_SET_ACTIVATE = wx.lib.newevent.NewEvent()
PmSampleActivate, EVT_PM_SAMPLE_ACTIVATE = wx.lib.newevent.NewEvent()


class PmSampleSetNode(TreeNode):
    def __init__(self, o):
        self.o = o

    @db_session
    def get_parent(self):
        return RootNode(self.o.pm_test_series)

    @db_session
    def self_reload(self): ...

    def get_name(self):
        return self.o.Name

    def get_icon(self):
        return "folder", get_icon("folder", 16)

    def get_icon_open(self):
        return "folder-open", get_icon("folder-open", 16)

    @db_session
    def get_subnodes(self):
        nodes = []
        for o in select(o for o in PMSample if o.pm_sample_set == self.o):
            nodes.append(PmSampleNode(o))
        return nodes

    @db_session
    def is_leaf(self):
        return select(o for o in PMSample if o.pm_sample_set == self.o).count() == 0

    def __eq__(self, o):
        return isinstance(o, PmSampleSetNode) and o.o.RID == self.o.RID


class PmSampleNode(TreeNode):
    def __init__(self, o):
        self.o = o

    @db_session
    def get_parent(self):
        return PmSampleSetNode(self.o.pm_sample_set)

    @db_session
    def self_reload(self): ...

    def get_name(self):
        return self.o.Name

    def get_icon(self):
        return "file", get_icon("file", 16)

    def get_icon_open(self):
        return "file", get_icon("file", 16)

    @db_session
    def get_subnodes(self):
        return []

    def is_leaf(self):
        return True

    def __eq__(self, o):
        return isinstance(o, PmSampleNode) and o.o.RID == self.o.RID


class RootNode(TreeNode):
    def __init__(self, pm_test_series):
        self.pm_test_series = pm_test_series
        self.o = pm_test_series

    def is_root(self):
        return False

    def self_reload(self): ...

    def get_parent(self):
        return RootNode(self.pm_test_series)

    def get_name(self):
        return "Обьекты"

    @db_session
    def get_subnodes(self):
        nodes = []
        for o in select(o for o in PMSampleSet if o.pm_test_series == self.pm_test_series):
            nodes.append(PmSampleSetNode(o))
        return nodes

    def __eq__(self, o):
        return isinstance(o, RootNode)

class DeputyNode(TreeNode):
    def get_name(self):
        return "[Не выбран договор]"

    def is_name_italic(self):
        return True

    def is_leaf(self):
        return True

    def get_icon(self):
        return "error", get_icon("error")

    def get_icon_open(self):
        return "error", get_icon("error")

    def __eq__(self, node):
        return isinstance(node,DeputyNode)

class DeputyRoot(TreeNode):
    def get_name(self):
        return "Объекты"

    def get_subnodes(self):
        return [DeputyNode()]

    def is_root(self):
        return True

    def __eq__(self, node):
        return isinstance(node, DeputyRoot)
        


class PmTestSeriesTree(Tree):
    def __init__(self, parent):
        super().__init__(parent)
        self.Bind(EVT_WIDGET_TREE_MENU, self.on_menu)
        self.Bind(EVT_WIDGET_TREE_ACTIVATED, self.on_node_activated)
        self.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self.on_selection_changed)
        self.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
        self.bind_all()
        self.pm_test_series = None
        self.set_pm_test_series(None)

    def on_right_click(self, event):
        a, b = self.HitTest(event.GetPoint())
        m = wx.Menu()
        if a == -1:
            m.Append(wx.ID_ADD, "Добавить пробу")
            m.SetBitmap(get_icon("file-add"))
        self.PopupMenu(m, event.GetPoint())

    def set_pm_test_series(self, pm_test_series):
        self.pm_test_series = pm_test_series
        if self.pm_test_series is not None:
            self.set_root_node(RootNode(pm_test_series))
        else:
            self.set_root_node(DeputyRoot())

    def on_menu(self, event):
        m = wx.Menu()
        if isinstance(event.node.o, PMSampleSet):
            i = m.Append(wx.ID_ADD, "Добавить образец")
            i.SetBitmap(get_icon("file-add"))
            m.AppendSeparator()
            i = m.Append(wx.ID_EDIT, "Изменить пробу")
            i.SetBitmap(get_icon("edit"))
            i = m.Append(wx.ID_DELETE, "Удалить")
            i.SetBitmap(get_icon("delete"))

        self.PopupMenu(m, event.point)

    def on_node_activated(self, event):
        if isinstance(event.node, PMSampleSet):
            wx.PostEvent(self, PmSampleSetActivate(pm_sample_set=event.node))
        elif isinstance(event.node, PMSample):
            wx.PostEvent(self, PmSampleActivate(pm_sample=event.node))

    def on_selection_changed(self, event): ...

    def can_delete(self):
        return self.get_current_node() is not None

    def can_add_pm_sample(self):
        node = self.get_current_node()
        return node is not None and isinstance(node.o, PMSampleSet)

    def delete(self):
        node = self.get_current_node()
        if node is not None:
            relations = []
            if isinstance(node.o, PMSampleSet):
                relations = ["pm_samples"]
            elif isinstance(node.o, PMSample):
                relations = [""]
            if delete_object(node.o, relations):
                self.soft_reload_childrens(node.get_parent())

    def on_add_sample_set(self):
        dlg = SampleSetDialog(self, self.pm_test_series)
        if dlg.ShowModal() == wx.ID_OK:
            self.soft_reload_childrens(RootNode(self.pm_test_series))

    def on_add_sample(self):
        node = self.get_current_node()
        if isinstance(node.o, PMSampleSet):
            dlg = PmSampleDialog(self, node.o)
            if dlg.ShowModal() == wx.ID_OK:
                ...
