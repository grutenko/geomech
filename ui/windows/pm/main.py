from typing import List
import wx

from ui.widgets.tree.widget import Tree, TreeNode, EVT_WIDGET_TREE_ACTIVATED
from ui.icon import get_icon, get_art
from .pm_methods import PmMethodsPanel
from .pm_equipment import PmEquipment


class Item_Node(TreeNode):
    def __init__(self, id, title):
        self._id = id
        self._title = title

    def get_name(self):
        return self._title

    def is_leaf(self) -> bool:
        return True

    def __eq__(self, node):
        return isinstance(node, Item_Node) and node._id == self._id


class Properties_Node(TreeNode):
    def get_name(self):
        return "Типовые свойства"

    def get_subnodes(self) -> List[TreeNode]:
        return [
            Item_Node("support.properties.classes", "Классы свойств"),
            Item_Node("support.properties.props", "Свойства"),
        ]

    def __eq__(self, node):
        return isinstance(node, Support_Node)


class Support_Node(TreeNode):
    def get_name(self):
        return "Вспомогательные данные"

    def get_subnodes(self) -> List[TreeNode]:
        return [
            Item_Node("support.test_methods", "Методы испытаний"),
            Item_Node("support.test_equipments", "Оборудование"),
            Properties_Node(),
            Item_Node("support.tasks", "Выполняемые задачи"),
        ]

    def __eq__(self, node):
        return isinstance(node, Support_Node)


class Root_Node(TreeNode):
    def get_name(self) -> str:
        return "Объекты"

    def get_subnodes(self) -> List[TreeNode]:
        return [Support_Node()]

    def __eq__(self, node):
        return isinstance(node, Root_Node)


class Deputy(wx.Panel):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Выбрать пункт: двойной клик по элементу.")
        main_sizer.Add(label, 1, wx.CENTER | wx.ALL, border=20)
        self.SetSizer(main_sizer)
        self.Hide()

    def start(self):
        self.Show()

    def end(self):
        self.Hide()


ID_FIND_NEXT = wx.ID_HIGHEST + 250


class PmSettingsWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        self.SetSize(1200, 600)
        self.SetMinSize(wx.Size(400, 200))
        self.SetTitle('Параметры "Физ. Мех. свойства"')
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()

        self.menu = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(wx.ID_FIND, "Поиск по разделу\tCTRL+F")
        item.SetBitmap(get_art(wx.ART_FIND))
        menu.Bind(wx.EVT_MENU, self._on_find, item)
        item.Enable(False)
        item = menu.Append(ID_FIND_NEXT, "Искать далее\tCTRL+SHIFT+F")
        item.SetBitmap(get_art(wx.ART_FIND))
        menu.Bind(wx.EVT_MENU, self._on_find_next, item)
        item.Enable(False)
        self.menu.Append(menu, "Файл")
        menu = wx.Menu()
        self.menu.Append(menu, "Правка")
        self.SetMenuBar(self.menu)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        splitter = wx.SplitterWindow(self, style=wx.SP_3D | wx.SP_LIVE_UPDATE)

        self._right_panel = wx.Panel(splitter)
        self._right_sizer = wx.BoxSizer(wx.VERTICAL)
        self._right_panel.SetSizer(self._right_sizer)
        self._right_panel.Layout()

        self._deputy = Deputy(self._right_panel)
        self._pm_methods = PmMethodsPanel(self._right_panel)
        self._pm_equipment = PmEquipment(self._right_panel)

        self._right_sizer.Add(self._deputy, 1, wx.EXPAND)
        self._deputy.start()

        splitter.SetMinimumPaneSize(200)
        self.tree = Tree(splitter, use_icons=False)
        self.tree.Bind(EVT_WIDGET_TREE_ACTIVATED, self._on_node_activated)
        self.tree.bind_all()
        self.tree.set_root_node(Root_Node())
        splitter.SetSashGravity(0)
        splitter.SplitVertically(self.tree, self._right_panel, 200)
        main_sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_CLOSE, self._on_close)

        self.Layout()

    def _on_find(self, event):
        dlg = wx.TextEntryDialog(self, "Введите часть названия", "Поиск по разделу")
        dlg.SetIcon(wx.Icon(get_art(wx.ART_FIND)))
        _current_panel = self._right_sizer.GetItem(0).GetWindow()
        q = _current_panel.get_last_q()
        dlg.SetValue(q if q != None else "")
        if dlg.ShowModal() == wx.ID_OK:
            _current_panel.start_find(dlg.GetValue())

    def _on_find_next(self, event): ...

    def _on_node_activated(self, event):
        node = event.node

        if isinstance(node, Item_Node):
            if node._id == "support.test_methods":
                _panel = self._pm_methods
            elif node._id == "support.test_equipments":
                _panel = self._pm_equipment
            else:
                _panel = self._deputy
        else:
            _panel = self._deputy
        old_panel = self._right_sizer.GetItem(0).GetWindow()
        old_panel.end()
        self._right_sizer.Detach(0)
        _panel.start()
        self._right_sizer.Add(_panel, 1, wx.EXPAND)
        self._right_panel.Layout()
        self.Layout()
        self._update_controls_state()

    def _update_controls_state(self):
        panel = self._right_sizer.GetItem(0).GetWindow()
        self.menu.Enable(wx.ID_FIND, not isinstance(panel, Deputy))

    def _on_close(self, event):
        self.Hide()
