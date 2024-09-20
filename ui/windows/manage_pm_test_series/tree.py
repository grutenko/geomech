from typing import List, Tuple
import wx

from pony.orm import *

from database import *
from ui.widgets.tree import *
from ui.widgets.tree.item import TreeNode
from ui.icon import get_art
from ui.delete_object import delete_object
from .create_test_series_dialog import CreateTestSeriesDialog

class _PMTestSeries_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_parent(self):
        return _Root_Node()
    
    def get_name(self):
        return self.o.Name
    
    def get_icon(self):
        return wx.ART_NORMAL_FILE, get_art(wx.ART_NORMAL_FILE, scale_to=16)
    
    def is_leaf(self) -> bool:
        return True
    
    def __eq__(self, node):
        return isinstance(node, _PMTestSeries_Node) and node.o.RID == self.o.RID

class _Root_Node(TreeNode):
    def get_name(self) -> str:
        return "Обьекты"
    
    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in PMTestSeries):
            nodes.append()
        return nodes

class TestSeriesTree(Tree):
    def __init__(self, parent):
        super().__init__(parent)
        self.bind_all()
        self.set_root_node(_Root_Node())

    def open_create_series_dialog(self):
        dlg = CreateTestSeriesDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.soft_reload_childrens()

    def open_edit_series_dialog(self):
        node = self.get_current_node()
        if node != None:
            dlg = CreateTestSeriesDialog(self, node.o, type="UPDATE")
            dlg.ShowModal()

    def delete(self):
        node = self.get_current_node()
        if delete_object(node.o, ['pm_sample_sets']):
            self.soft_reload_childrens(_Root_Node())