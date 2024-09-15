from typing import List, Tuple
import wx
from pony.orm import *

from database import CoordSystem
from ui.widgets.tree import *
from ui.widgets.tree.item import TreeNode
from ui.icon import get_icon
from ui.delete_object import delete_object

from .create_coord_system_dialog import CreateCoordSystemDialog

class _CoordSystem_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    @db_session
    def get_parent(self) -> TreeNode:
        return self.o.parent

    def get_name(self):
        return self.o.Name
    
    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return "coord_system", get_icon("coord_system", scale_to=16)
    
    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in CoordSystem if o.parent == self.o):
            nodes.append(_CoordSystem_Node(o))
        return nodes
    
    def __eq__(self, node):
        return isinstance(node, _CoordSystem_Node) and node.o.RID == self.o.RID
    
    @db_session
    def is_leaf(self) -> bool:
        return select(o for o in CoordSystem if o.parent == self.o).first() == None
    
class _Root_Node(TreeNode):
    def get_name(self):
        return "Системы координат"

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = []
        for o in select(o for o in CoordSystem if o.Level == 0):
            nodes.append(_CoordSystem_Node(o))
        return nodes
    
    def __eq__(self, node):
        return isinstance(node, _Root_Node)

class CoordSystemTree(Tree):
    def __init__(self, parent):
        super().__init__(parent)
        self.set_root_node(_Root_Node())
        self.bind_all()

        self.Bind(EVT_WIDGET_TREE_MENU, self._on_node_context_menu)
        self.Bind(EVT_WIDGET_TREE_ACTIVATED, self._on_node_activated)

        self._current_node = None
        self._current_object = None

    def _on_node_context_menu(self, event):
        self._current_node = event.node
        self._current_object = event.node.o
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Добавить дочернюю систему")
        menu.Bind(wx.EVT_MENU, self._on_create_coord_system, item)
        item = menu.Append(wx.ID_ANY, "Изменить")
        menu.Bind(wx.EVT_MENU, self._on_create_coord_system, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Удалить")
        menu.Bind(wx.EVT_MENU, self._on_delete_coord_system, item)
        self.PopupMenu(menu, event.point)

    def _on_create_coord_system(self, event):
        dlg = CreateCoordSystemDialog(self, self._current_object)
        if dlg.ShowModal() == wx.ID_YES:
            self.soft_reload_node(self._current_node)
            self.select_node(_CoordSystem_Node(dlg.o))

    def _on_delete_coord_system(self, event):
        p = self._current_node.get_parent()
        if delete_object(self._current_object, ['mine_objects', 'childrens']):
            self.soft_reload_node(p)

    def _on_node_activated(self, event):
        dlg = CreateCoordSystemDialog(self, event.node.o, type='UPDATE')
        dlg.ShowModal()
