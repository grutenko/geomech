import wx
import wx

from pony.orm import *
from database import *

from ui.widgets.tree import *
from ui.icon import get_icon, get_art
from ui.windows.main_window.grid.discharge_measurements import (
    DischargeMeasurementsEditor,
)
from ui.windows.main_window.create_dialogs.dialog_create_orig_sample_set import (
    DialogCreateCore,
)
from .create_discharge_series_dialog import CreateDischargeSeries
from ui.delete_object import delete_object
from ui.windows.main_window.notebook import MainWindowNotebook

from database import OrigSampleSet


class _SelfProps_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    @db_session
    def self_reload(self):
        self.o = OrigSampleSet[self.o.RID]

    def get_name(self) -> str:
        return 'Свойства объекта: "%s"' % self.o.Name

    def get_icon(self):
        return wx.ART_INFORMATION, get_art(wx.ART_INFORMATION, 16)

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return isinstance(node, _SelfProps_Node) and node.o.RID == self.o.RID


class _CoreBoxStorage_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "Раскладка керна по ящикам"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_NORMAL_FILE, get_art(wx.ART_NORMAL_FILE, 16)

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return isinstance(node, _CoreBoxStorage_Node) and node.o.RID == self.o.RID


class _DiscargeSeries_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    @db_session
    def self_reload(self):
        self.o = DischargeSeries[self.o.RID]

    def get_name(self) -> str:
        return "[Разгрузка] Параметры серии замеров"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_NORMAL_FILE, get_art(wx.ART_NORMAL_FILE, 16)

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return isinstance(node, _DiscargeSeries_Node) and node.o.RID == self.o.RID


class _PMStructWeakening_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "[Физ. Мех. Свойства] Коэффициент структурного ослабления"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_REPORT_VIEW, get_art(wx.ART_REPORT_VIEW, 16)

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return (
            isinstance(node, _DischargeMeasurements_Node) and node.o.RID == self.o.RID
        )


class _DischargeMeasurements_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "[Разгрузка] Замеры"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_REPORT_VIEW, get_art(wx.ART_REPORT_VIEW, 16)

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return (
            isinstance(node, _DischargeMeasurements_Node) and node.o.RID == self.o.RID
        )


class _PMSamples_Node(TreeNode):
    def __init__(self, o):
        self.o = o

    def get_name(self) -> str:
        return "[Физ. Мех. Свойства] Образцы"

    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return wx.ART_REPORT_VIEW, get_art(wx.ART_REPORT_VIEW, 16)

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
        series = select(
            o for o in DischargeSeries if o.orig_sample_set == self.o
        ).first()
        if series != None:
            nodes.append(_DiscargeSeries_Node(series))
        nodes += [
            _DischargeMeasurements_Node(self.o),
        ]
        if OrigSampleSet[self.o.RID].bore_hole.station == None:
            nodes += [_PMSamples_Node(self.o), _PMStructWeakening_Node(self.o)]
        return nodes

    def __eq__(self, node):
        return isinstance(node, _Root_Node)


TOOL_ADD_DISCHARGE_SERIES = 1


class CoreProperties(wx.Panel):
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent)

        self.menubar = menubar
        self.toolbar = toolbar
        self.statusbar = statusbar

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self._toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.TB_HORZ_TEXT)
        self._toolbar.AddTool(
            TOOL_ADD_DISCHARGE_SERIES,
            "Добавить [Разгрузка] Набор замеров",
            get_art(wx.ART_PLUS),
        )
        self._toolbar.Bind(
            wx.EVT_TOOL, self._on_create_ds, id=TOOL_ADD_DISCHARGE_SERIES
        )
        self._toolbar.EnableTool(TOOL_ADD_DISCHARGE_SERIES, False)
        main_sizer.Add(self._toolbar, 0, wx.EXPAND)
        self._toolbar.Realize()

        self._tree = Tree(self)
        main_sizer.Add(self._tree, 1, wx.EXPAND)

        self.Layout()

        self._tree.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self._on_node_selected)
        self._tree.Bind(EVT_WIDGET_TREE_MENU, self._on_node_tree_menu)
        self._tree.Bind(EVT_WIDGET_TREE_ACTIVATED, self._on_node_activated)

        self._handler_properties_object_seleted = None
        self._handler_properties_target_updated = None

    @db_session
    def start(
        self,
        o: OrigSampleSet,
        on_properties_object_selected=None,
        on_properties_target_updated=None,
    ):
        self.o = o
        self._handler_properties_object_seleted = on_properties_object_selected
        self._handler_properties_target_updated = on_properties_target_updated
        self._tree.set_root_node(_Root_Node(o))
        self._tree.bind_all()
        self.Show()
        self._tree.select_node(_SelfProps_Node(self.o))
        if (
            select(o for o in DischargeSeries if o.orig_sample_set == self.o).first()
            == None
        ):
            self._toolbar.EnableTool(TOOL_ADD_DISCHARGE_SERIES, True)

    def end(self):
        self._handler_properties_object_seleted = None
        self.Hide()
        self._tree.unbind_all()
        self.o = None

    def _on_node_activated(self, event):
        if isinstance(event.node, _DischargeMeasurements_Node):
            self._on_open_dm_editor()
        elif isinstance(event.node, _DiscargeSeries_Node):
            self._on_open_ds_editor(event.node)
        elif isinstance(event.node, _SelfProps_Node):
            self.open_self_props_editor()

    def _on_create_ds(self, event):
        dlg = CreateDischargeSeries(self, self.o, _type="CREATE")
        dlg.ShowModal()

    def _on_open_ds_editor(self, node):
        dlg = CreateDischargeSeries(self, node.o, _type="UPDATE")
        dlg.ShowModal()

    def _on_node_tree_menu(self, event):
        if isinstance(event.node, _DischargeMeasurements_Node):
            self._dm_context_menu(event.node, event.point)
        elif isinstance(event.node, _DiscargeSeries_Node):
            self._ds_context_menu(event.node, event.point)

    def _ds_context_menu(self, node, point):
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Удалить")
        menu.Bind(wx.EVT_MENU, self._delete_ds, item)
        self.PopupMenu(menu, point)

    def _delete_ds(self, event):
        node = self._tree.get_current_node()
        if delete_object(node.o):
            self._tree.soft_reload_childrens(_Root_Node())
            self._toolbar.EnableTool(TOOL_ADD_DISCHARGE_SERIES, True)

    def _dm_context_menu(self, node, point):
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Открыть редактор")
        menu.Bind(wx.EVT_MENU, self._on_open_dm_editor, item)
        self.PopupMenu(menu, point)

    def _on_open_dm_editor(self, event=None):
        notebook = MainWindowNotebook.get_instance()
        w = DischargeMeasurementsEditor(
            notebook._native_,
            self._tree.get_current_node().o,
            self.menubar,
            self.toolbar,
            self.statusbar,
        )
        notebook.add_page(w)

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

    @db_session
    def open_self_props_editor(self):
        dlg = DialogCreateCore(self, self.o, "UPDATE")
        if dlg.ShowModal() == wx.ID_OK:
            self._tree.soft_reload_node(_SelfProps_Node(self.o))
            if self._handler_properties_target_updated != None:
                self._handler_properties_target_updated(self.o)
            self.o = OrigSampleSet[self.o.RID]
