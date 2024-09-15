import wx
import wx

from pony.orm import *
from database import *

from ui.widgets.tree import *
from ui.icon import get_icon

from database import OrigSampleSet


class _SelfProps_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return 'Свойства объекта: "%s"' % self.o.Name

    def get_icon(self):
        return "w2k_info", get_icon("w2k_info", scale_to=16)

    def is_leaf(self) -> bool:
        return True
    
    def __eq__(self, node):
        return isinstance(node, _SelfProps_Node) and node.o.RID == self.o.RID


class _CoreBoxStorage_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "Раскладка керна по ящикам"

    def get_icon(self):
        return "w2k_text_document", get_icon("w2k_text_document", scale_to=16)

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return isinstance(node, _CoreBoxStorage_Node) and node.o.RID == self.o.RID

class _DiscargeSeries_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "[Разгрузка] Параметры серии замеров"

    def get_icon(self):
        return "w2k_text_document", get_icon("w2k_text_document", scale_to=16)

    def is_leaf(self) -> bool:
        return True
    
    def __eq__(self, node):
        return isinstance(node, _DiscargeSeries_Node) and node.o.RID == self.o.RID


class _DischargeMeasurements_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "[Разгрузка] Замеры"

    def get_icon(self):
        return "w2k_text_document", get_icon("w2k_text_document", scale_to=16)

    def is_leaf(self) -> bool:
        return True
    
    def __eq__(self, node):
        return isinstance(node, _DischargeMeasurements_Node) and node.o.RID == self.o.RID


class _PMSamples_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "[Физ. Мех. Свойства] Образцы"

    def get_icon(self):
        return "w2k_text_document", get_icon("w2k_text_document", scale_to=16)

    def is_leaf(self) -> bool:
        return True
    
    def __eq__(self, node):
        return isinstance(node, _PMSamples_Node) and node.o.RID == self.o.RID


class _Root_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "Объекты"

    @db_session
    def get_subnodes(self) -> List[TreeNode]:
        nodes = [
            _SelfProps_Node(self.o),
        ]
        series = select(o for o in DischargeSeries if o.orig_sample_set == self.o).first()
        if series != None:
            nodes.append(_DiscargeSeries_Node(series))
        nodes += [
            _DischargeMeasurements_Node(self.o),
            _PMSamples_Node(self.o),
        ]
        return nodes

    def __eq__(self, node):
        return isinstance(node, _Root_Node)


class CoreProperties(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self._tree = Tree(self)
        main_sizer.Add(self._tree, 1, wx.EXPAND)

        self.Layout()

        self._tree.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self._on_node_selected)

        self._handler_properties_object_seleted = None

    def start(self, o: OrigSampleSet, on_properties_object_selected=None):
        self.o = o
        self._handler_properties_object_seleted = on_properties_object_selected
        self._tree.set_root_node(_Root_Node(o))
        self._tree.bind_all()
        self.Show()
        self._tree.select_node(_SelfProps_Node(self.o))

    def end(self):
        self._handler_properties_object_seleted = None
        self.Hide()
        self._tree.unbind_all()
        self.o = None

    def _on_node_selected(self, event):
        object = None
        bounds = None
        if event.node != None:
            if isinstance(event.node, _SelfProps_Node):
                object = self.o
                bounds = None
            elif isinstance(event.node, _DischargeMeasurements_Node):
                object = self.o
                bounds = DischargeMeasurement
            elif isinstance(event.node, _DiscargeSeries_Node):
                object = event.node.o
                bounds = None
            elif isinstance(event.node, _PMSamples_Node):
                object = self.o
                bounds = PMSample

        if self._handler_properties_object_seleted != None and object != None:
            self._handler_properties_object_seleted(object, bounds)
