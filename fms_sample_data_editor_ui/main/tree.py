import wx

from pony.orm import db_session, select
from database import PMSampleSet, PMSample, PMTestSeries
from ui.widgets.tree import Tree, TreeNode, EVT_WIDGET_TREE_MENU, EVT_WIDGET_TREE_ACTIVATED, EVT_WIDGET_TREE_SEL_CHANGED
from ui.icon import get_icon

class PmSampleSetNode(TreeNode):
    def __init__(self, o):
        self.o = o
        
    @db_session
    def get_parent(self):
        return RootNode(self.o.pm_test_series)
        
    @db_session
    def self_reload(self):
        ...
        
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
    def self_reload(self):
        ...
        
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
    
    def is_root(self):
        return False
        
    def self_reload(self):
        ...
        
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

class PmTestSeriesTree(Tree):
    def __init__(self, parent):
        super().__init__(parent)
        self.Bind(EVT_WIDGET_TREE_MENU, self.on_menu)
        self.Bind(EVT_WIDGET_TREE_ACTIVATED, self.on_node_activated)
        self.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self.on_selection_changed)
        self.bind_all()
    
    def set_pm_test_series(self, pm_test_series):
        self.set_root_node(RootNode(pm_test_series))
        
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
        ...
        
    def on_selection_changed(self, event):
        ...
        
    def can_delete(self):
        return self.get_current_node() != None
        
    def can_add_pm_sample(self):
        node = self.get_current_node()
        return node != None and isinstance(node.o, PMSampleSet)