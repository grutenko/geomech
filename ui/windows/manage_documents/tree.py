from typing import List
import wx

from pony.orm import *

from ui.widgets.tree import *
from ui.widgets.tree.item import TreeNode
from database import FoundationDocument
from ui.icon import get_icon

class _Document_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_parent(self):
        return _Root_Node()
    
    def get_name(self) -> str:
        return self.o.Name
    
    def get_icon(self):
        return "w2k_text_document", get_icon("w2k_text_document", scale_to=16)
    
    def is_leaf(self) -> bool:
        return True
        
class _Root_Node(TreeNode):
    def get_name(self):
        return "Объекты"
    
    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in FoundationDocument):
            nodes.append(_Document_Node(o))
        return nodes
    
    def __eq__(self, node):
        return isinstance(node, _Root_Node)

class DocumentsTree(Tree):
    def __init__(self, parent):
        super().__init__(parent)
        self.bind_all()
        self.set_root_node(_Root_Node())