import wx
import wx.aui
import database
import config
from pony.orm import *

from ui.widgets.tree import EVT_WIDGET_TREE_SEL_CHANGED

from .tree import MainWindowTree
from .properties import MainWindowProperties, EVT_PROPERTIES_PROPERTY_SELECTED
from ..switch_coord_system.frame import CsTransl
from .supplied_data import MainWindowSuppliedData
from .fastview import FastviewMainWindow
from ui.windows.manage_coord_systems.manage_coord_systems_window import ManageCoordSystemsWindow
from ui.windows.create_transf_matrix.create_transf_matrix_window import CreateTransfMatrixWindow
from ui.windows.manage_pm_test_series.manage_pm_test_series_window import ManageTestSeriesWindow
from ui.windows.manage_documents.manage_documents_window import ManageDocumentsWindow

ID_FILE_EXIT = wx.ID_HIGHEST
ID_OPTIONS_FIZMECH = ID_FILE_EXIT + 1
ID_OPTIONS_COORD_SYSTEMS = ID_FILE_EXIT + 2
ID_UTIL_CS_TRANSF = ID_FILE_EXIT + 3
ID_OPTIONS_DOCS = ID_FILE_EXIT + 4
ID_OPTIONS_FIZMECH_OPTIONS = ID_FILE_EXIT + 5
ID_OPTIONS_FIZMECH_METHODS = ID_FILE_EXIT + 6
ID_OPTIONS_FIZMECH_TASKS = ID_FILE_EXIT + 7
ID_OPTIONS_FIZMECH_EQUIPMENT = ID_FILE_EXIT + 8
ID_CS_MANAGE = ID_FILE_EXIT + 9
ID_CS_TRANSF_UTLITY = ID_FILE_EXIT + 10
ID_OPTIONS_FIZMECH_SERIES = ID_FILE_EXIT + 11


class MainFrame(wx.Frame):
    def __init__(self, database_config):
        super().__init__(None, title='База данных "Геомеханика".')
        self.SetSize(1280, 600)
        self.CenterOnScreen()
        self.SetIcon(wx.Icon("./icons/logo@16.jpg"))

        self.database_config = database_config

        self.mgr = wx.aui.AuiManager(
            self,
            flags=wx.aui.AUI_MGR_DEFAULT
            | wx.aui.AUI_MGR_LIVE_RESIZE
            | wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE,
        )

        i = wx.aui.AuiPaneInfo()
        i.Left()
        i.Caption("Объекты")
        i.CloseButton(False)
        i.MaximizeButton(True)
        i.MinSize(250, 400)
        self.tree_pane = MainWindowTree(self)
        self.tree_pane.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self._on_tree_node_selection_changed)
        self.mgr.AddPane(self.tree_pane, i)

        i = wx.aui.AuiPaneInfo()
        i.MinSize(300, 150)
        i.CenterPane()
        self.properties = MainWindowProperties(self)
        self.properties.Bind(EVT_PROPERTIES_PROPERTY_SELECTED, self._on_property_selected)
        self.mgr.AddPane(self.properties, i)

        i = wx.aui.AuiPaneInfo()
        i.Right()
        i.Caption("Быстрый просмотр")
        i.CloseButton(False)
        i.MaximizeButton(True)
        i.MinSize(250, 400)
        i.BestSize(250, 400)
        self.fastview = FastviewMainWindow(self)
        self.mgr.AddPane(self.fastview, i)

        i = wx.aui.AuiPaneInfo()
        i.Caption("Сопутствующие материалы")
        i.Bottom()
        i.MinSize(300, 150)
        i.BestSize(1024, 200)
        self.supplied_data = MainWindowSuppliedData(self)
        self.mgr.AddPane(self.supplied_data, i)

        self.mgr.Update()

        self._init_controls()

        self.Show()

    def _init_controls(self):

        self.menu = wx.MenuBar()
        file = wx.Menu()
        file.Append(ID_FILE_EXIT, "Выход")
        self.menu.Append(file, "Файл")
        self.SetMenuBar(self.menu)

        menu = wx.Menu()
        self.menu.Append(menu, "Горные удары")

        menu = wx.Menu()
        item = menu.Append(ID_OPTIONS_FIZMECH_SERIES, "Наборы испытаний")
        menu.Bind(wx.EVT_MENU, self._on_open_test_series)
        menu.AppendSeparator()
        menu.Append(ID_OPTIONS_FIZMECH_OPTIONS, "Типовые свойства")
        menu.Append(ID_OPTIONS_FIZMECH_METHODS, "Методы испытаний")
        menu.Append(ID_OPTIONS_FIZMECH_TASKS, "Выполняемые задачи")
        menu.Append(ID_OPTIONS_FIZMECH_EQUIPMENT, "Оборудование")
        self.menu.Append(menu, "Физ. Мех. Свойства")

        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Управление")
        menu.Bind(wx.EVT_MENU, self._on_open_documents_manage, item)
        self.menu.Append(menu, "Документы")

        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Управление")
        self.menu.Append(menu, "Петротипы")

        utils = wx.Menu()
        item = utils.Append(ID_CS_MANAGE, "Управление")
        utils.Bind(wx.EVT_MENU, self._on_open_cs_manager, item)
        utils.AppendSeparator()
        item = utils.Append(wx.ID_ANY, "Утилита нахождения матрицы перевода")
        utils.Bind(wx.EVT_MENU, self._on_open_cs_matrix_find, item)
        item = utils.Append(ID_CS_TRANSF_UTLITY, "Утилита перевода координат")
        utils.Bind(wx.EVT_MENU, self._on_open_cs_transf, item)
        self.menu.Append(utils, "Системы координат")

        self.statusbar = wx.StatusBar(self)
        self.SetStatusBar(self.statusbar)
        self.statusbar.SetFieldsCount(4)
        self.statusbar.SetStatusText(
            "Подключен: %s:%d, %s"
            % (
                self.database_config["host"],
                self.database_config["port"],
                self.database_config["login"],
            )
        )

    def _on_open_documents_manage(self, event):
        w = ManageDocumentsWindow(self)
        w.Show()

    def _on_open_test_series(self, event):
        w = ManageTestSeriesWindow(self)
        w.Show()

    def _on_open_cs_matrix_find(self, event):
        w = CreateTransfMatrixWindow(self)
        w.Show()

    def _on_open_cs_manager(self, event):
        w = ManageCoordSystemsWindow(self)
        w.Show()

    def _on_open_cs_transf(self, event):
        w = CsTransl(self)
        w.Show()

    def _on_tree_node_selection_changed(self, event):
        if event.node != None:
            self.fastview.end()
            self.properties.start(event.node.o)

    def _on_property_selected(self, event):
        self.fastview.start(event.object, event.bounds)

