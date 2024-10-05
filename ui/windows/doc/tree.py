from typing import List
import wx

from pony.orm import *

from ui.widgets.tree import *
from ui.widgets.tree.item import TreeNode
from ui.delete_object import delete_object
from database import FoundationDocument
from ui.icon import get_art

from .create import CreateDocumentDialog

class _Document_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_parent(self):
        return _Root_Node()
    
    def get_name(self) -> str:
        return self.o.Name
    
    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_NORMAL_FILE, get_art(wx.ART_NORMAL_FILE, 16)
    
    def is_leaf(self) -> bool:
        return True
    
    def __eq__(self, node):
        return isinstance(node, _Document_Node) and node.o.RID == self.o.RID
        
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

        self.Bind(EVT_WIDGET_TREE_MENU, self._on_node_menu)

    def _on_node_menu(self, event):
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Изменить")
        menu.Bind(wx.EVT_MENU, self.update, item)
        item = menu.Append(wx.ID_ANY, "Удалить")
        menu.Bind(wx.EVT_MENU, self.delete, item)
        self.PopupMenu(menu, event.point)

    def create(self, event=None):
        dlg = CreateDocumentDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.soft_reload_childrens(_Root_Node())
            self.select_node(_Document_Node(dlg.o))

    def update(self, event=None):
        node = self.get_current_node()
        dlg = CreateDocumentDialog(self)
        if dlg.ShowModal() == wx.ID_OK:
            self.soft_reload_node(node)

    def delete(self, event=None):
        node = self.get_current_node()
        p = node.get_parent()
        if delete_object(node.o, ['discharge_series', 'pm_test_series']):
            self.soft_reload_childrens(p)