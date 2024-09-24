import wx
import wx.aui
import database
import config
from pony.orm import *

from database import *
from ui.widgets.tree import EVT_WIDGET_TREE_SEL_CHANGED, EVT_WIDGET_TREE_ACTIVATED
from ui.windows.manage_coord_systems.manage_coord_systems_window import (
    ManageCoordSystemsWindow,
)
from ui.windows.create_transf_matrix.create_transf_matrix_window import (
    CreateTransfMatrixWindow,
)
from ui.windows.manage_pm_test_series.manage_pm_test_series_window import (
    ManageTestSeriesWindow,
)
from ui.windows.manage_documents.manage_documents_window import ManageDocumentsWindow
from ui.windows.switch_coord_system.frame import CsTransl
from ui.icon import get_art, get_icon
from ui.class_config_provider import ClassConfigProvider

from .tree import MainWindowTree, EVT_TREE_OPEN_SELF_EDITOR
from .properties import (
    MainWindowProperties,
    EVT_PROPERTIES_PROPERTY_SELECTED,
    EVT_PROPERTIES_TARGET_UPDATED,
)
from .notebook import (
    MainWindowNotebook,
    EVT_NOTEBOOK_PAGE_COUNT_CHANGED,
    EVT_NOTEBOOK_PAGE_SELECTION_CHANGED,
)
from .supplied_data import MainWindowSuppliedData
from .fastview import FastviewMainWindow
from .notebook_help_page import HelpPage


ID_FILE_EXIT = wx.ID_HIGHEST + 100
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
ID_TOGGLE_FASTVIEW = ID_FILE_EXIT + 12
ID_TOGGLE_SUPPLIED_DATA = ID_FILE_EXIT + 13
ID_CLOSE_TAB = ID_FILE_EXIT + 14
ID_TOGGLE_OBJECTS = ID_FILE_EXIT + 15
ID_TOGGLE_PROPERTIES = ID_FILE_EXIT + 16
ID_NEXT_TAB = ID_FILE_EXIT + 17
ID_PREV_TAB = ID_FILE_EXIT + 18

__CONFIG_VERSION__ = 9


class MainFrame(wx.Frame):
    def __init__(self, database_config):
        super().__init__(None, title='База данных "Геомеханика".')
        self.SetSize(1280, 600)
        self.CenterOnScreen()
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.SetMinSize(wx.Size(600, 300))

        self.database_config = database_config
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

        o = self._config_provider["window"]
        if o != None:
            self.SetSize(o["x"], o["y"], o["width"], o["height"])

        self.mgr = wx.aui.AuiManager(
            self,
            flags=wx.aui.AUI_MGR_DEFAULT
            | wx.aui.AUI_MGR_LIVE_RESIZE
            | wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE,
        )
        self.mgr.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self._on_panel_closed)

        i = wx.aui.AuiPaneInfo()
        i.Name("objects")
        i.Left()
        i.Caption("Объекты")
        i.MaximizeButton(True)
        i.CloseButton(True)
        i.MinSize(250, 150)
        i.Hide()
        self.tree_pane = MainWindowTree(self)
        self.tree_pane.Bind(
            EVT_WIDGET_TREE_SEL_CHANGED, self._on_tree_node_selection_changed
        )
        self.tree_pane.Bind(EVT_TREE_OPEN_SELF_EDITOR, self._on_open_self_editor)
        self.mgr.AddPane(self.tree_pane, i)

        self._init_controls()

        i = wx.aui.AuiPaneInfo()
        i.Caption("Связаные данные")
        i.Name("properties")
        i.Left()
        i.MaximizeButton(True)
        i.CloseButton(True)
        i.MinSize(300, 150)
        i.Hide()
        self.properties = MainWindowProperties(self, self.menu, self.statusbar)
        self.properties.Bind(
            EVT_PROPERTIES_PROPERTY_SELECTED, self._on_property_selected
        )
        self.properties.Bind(
            EVT_PROPERTIES_TARGET_UPDATED, self._on_property_target_updated
        )
        self.mgr.AddPane(self.properties, i)

        i = wx.aui.AuiPaneInfo()
        i.Caption("Вкладки")
        i.Name("notebook")
        i.CenterPane()
        i.CloseButton(False)
        self.notebook = MainWindowNotebook(self)
        self.notebook.Bind(EVT_NOTEBOOK_PAGE_COUNT_CHANGED, self._on_page_count_changed)
        self.notebook.Bind(EVT_NOTEBOOK_PAGE_SELECTION_CHANGED, self._on_page_selection_changed)
        self.mgr.AddPane(self.notebook, i)
        self.notebook.add_page(HelpPage(self.notebook.notebook))

        i = wx.aui.AuiPaneInfo()
        i.Name("fastview")
        i.Right()
        i.Caption("Быстрый просмотр")
        i.MaximizeButton(True)
        i.MinSize(250, 150)
        i.BestSize(250, 400)
        i.Hide()
        i.Float()
        self.fastview = FastviewMainWindow(self)
        self.mgr.AddPane(self.fastview, i)

        i = wx.aui.AuiPaneInfo()
        i.Name("supplied_data")
        i.Caption("Сопутствующие материалы")
        i.Bottom()
        i.MaximizeButton(True)
        i.MinSize(300, 150)
        i.BestSize(1024, 200)
        i.Float()
        i.Hide()
        self.supplied_data = MainWindowSuppliedData(self)
        self.mgr.AddPane(self.supplied_data, i)

        perspective = self._config_provider["perspective"]
        if perspective != None:
            try:
                self.mgr.LoadPerspective(perspective, False)
            except:
                pass

        self.mgr.GetPane('objects').Icon(get_art(wx.ART_HARDDISK, scale_to=16))
        self.mgr.GetPane('properties').Icon(get_art(wx.ART_HELP_BOOK, scale_to=16))
        self.mgr.GetPane('fastview').Icon(get_art(wx.ART_HELP_PAGE, scale_to=16))
        self.mgr.GetPane('supplied_data').Icon(get_art(wx.ART_FOLDER_OPEN, scale_to=16))

        self.mgr.Update()

        self.Show()

        self.Bind(wx.EVT_CLOSE, self._on_close)

    def _init_controls(self):
        self.menu = wx.MenuBar()
        file = wx.Menu()
        item = file.Append(wx.ID_FIND, "Найти\tCTRL+F")
        item.SetBitmap(get_art(wx.ART_FIND, scale_to=16))
        item = file.Append(wx.ID_PREVIEW_NEXT, "Найти далее\tCTRL+SHIFT+F")
        item.SetBitmap(get_art(wx.ART_FIND, scale_to=16))
        item.Enable(False)
        file.AppendSeparator()
        item = file.Append(ID_NEXT_TAB, "Следующая вкладка\tCTRL+RIGHT")
        item.SetBitmap(get_art(wx.ART_GO_FORWARD, scale_to=16))
        item.Enable(False)
        file.Bind(wx.EVT_MENU, self._on_next_tab, item)
        item = file.Append(ID_PREV_TAB, "Предыдущая вкладка\tCTRL+LEFT")
        item.SetBitmap(get_art(wx.ART_GO_BACK, scale_to=16))
        item.Enable(False)
        file.Bind(wx.EVT_MENU, self._on_prev_tab, item)
        item = file.Append(ID_CLOSE_TAB, "Закрыть вкладку\tCTRL+W")
        item.SetBitmap(get_art(wx.ART_CLOSE, scale_to=16))
        item.Enable(False)
        file.Bind(wx.EVT_MENU, self._on_close_tab, item)
        file.AppendSeparator()
        item = file.Append(ID_FILE_EXIT, "Выход\tCTRL+ALT+E")
        file.Bind(wx.EVT_MENU, self._on_exit, item)
        self.menu.Append(file, "Файл")
        self.SetMenuBar(self.menu)

        menu = wx.Menu()
        item = menu.AppendCheckItem(
            ID_TOGGLE_OBJECTS, "Показать/Скрыть панель объектов\tCTRL+ALT+B"
        )
        toggle = self._config_provider["toggle_objects"]
        menu.Check(ID_TOGGLE_OBJECTS, toggle if toggle != None else False)
        menu.Bind(wx.EVT_MENU, self._on_toggle_objects, item)
        item = menu.AppendCheckItem(
            ID_TOGGLE_PROPERTIES, "Показать/Скрыть панель связаных данных\tCTRL+ALT+R"
        )
        toggle = self._config_provider["toggle_properties"]
        menu.Check(ID_TOGGLE_PROPERTIES, toggle if toggle != None else False)
        menu.Bind(wx.EVT_MENU, self._on_toggle_properties, item)
        item = menu.AppendCheckItem(
            ID_TOGGLE_FASTVIEW, "Показать/Скрыть панель быстрого просмотра\tCTRL+ALT+F"
        )
        toggle = self._config_provider["toggle_fastview"]
        menu.Check(ID_TOGGLE_FASTVIEW, toggle if toggle != None else False)
        menu.Bind(wx.EVT_MENU, self._on_toggle_fastview, item)
        item = menu.AppendCheckItem(
            ID_TOGGLE_SUPPLIED_DATA, "Показать/Скрыть панель сопутствующи материалов\tCTRL+ALT+D"
        )
        toggle = self._config_provider["toggle_supplied_data"]
        menu.Check(ID_TOGGLE_SUPPLIED_DATA, toggle if toggle != None else False)
        menu.Bind(wx.EVT_MENU, self._on_toggle_supplied_data, item)
        self.menu.Append(menu, "Вид")

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

        menu = wx.Menu()
        item = menu.Append(wx.ID_ABOUT, "О программе")
        self.menu.Append(menu, "?")

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

    def _on_page_selection_changed(self, event):
        self._update_controls_state()

    def _update_controls_state(self):
        self.menu.Enable(ID_NEXT_TAB, self.notebook.can_go_next())
        self.menu.Enable(ID_PREV_TAB, self.notebook.can_go_prev())
        self.menu.Enable(ID_CLOSE_TAB, self.notebook.get_page_count() > 0)

    def _on_next_tab(self, event):
        self.notebook.go_next()

    def _on_prev_tab(self, event):
        self.notebook.go_prev()

    def _on_page_count_changed(self, event):
        self._update_controls_state()

    def _on_close_tab(self, event):
        self.notebook.close_current_page()

    def _on_open_self_editor(self, event):
        self.properties.open_self_editor()

    def _on_toggle_fastview(self, event: wx.MenuEvent):
        if self.menu.IsChecked(ID_TOGGLE_FASTVIEW):
            self.mgr.GetPane("fastview").Show()
        else:
            self.mgr.GetPane("fastview").Hide()
        self._config_provider["toggle_fastview"] = self.menu.IsChecked(
            ID_TOGGLE_FASTVIEW
        )
        self._config_provider.flush()
        self.mgr.Update()

    def _on_toggle_objects(self, event: wx.MenuEvent):
        if self.menu.IsChecked(ID_TOGGLE_OBJECTS):
            self.mgr.GetPane("objects").Show()
        else:
            self.mgr.GetPane("objects").Hide()
        self._config_provider["toggle_objects"] = self.menu.IsChecked(ID_TOGGLE_OBJECTS)
        self._config_provider.flush()
        self.mgr.Update()

    def _on_toggle_properties(self, event: wx.MenuEvent):
        if self.menu.IsChecked(ID_TOGGLE_PROPERTIES):
            self.mgr.GetPane("properties").Show()
        else:
            self.mgr.GetPane("properties").Hide()
        self._config_provider["toggle_properties"] = self.menu.IsChecked(
            ID_TOGGLE_PROPERTIES
        )
        self._config_provider.flush()
        self.mgr.Update()

    def _on_toggle_supplied_data(self, event):
        if self.menu.IsChecked(ID_TOGGLE_SUPPLIED_DATA):
            self.mgr.GetPane("supplied_data").Show()
        else:
            self.mgr.GetPane("supplied_data").Hide()
        self._config_provider["toggle_supplied_data"] = self.menu.IsChecked(
            ID_TOGGLE_SUPPLIED_DATA
        )
        self._config_provider.flush()
        self.mgr.Update()

    def _on_panel_closed(self, event: wx.aui.AuiManagerEvent):
        if event.GetPane().name == "fastview":
            self.menu.Check(ID_TOGGLE_FASTVIEW, False)
            self._config_provider["toggle_fastview"] = False
        elif event.GetPane().name == "supplied_data":
            self.menu.Check(ID_TOGGLE_SUPPLIED_DATA, False)
            self._config_provider["toggle_supplied_data"] = False
        elif event.GetPane().name == "objects":
            self.menu.Check(ID_TOGGLE_OBJECTS, False)
            self._config_provider["toggle_objects"] = False
        elif event.GetPane().name == "properties":
            self.menu.Check(ID_TOGGLE_PROPERTIES, False)
            self._config_provider["toggle_properties"] = False

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

    def _on_property_target_updated(self, event):
        self.tree_pane.reload_object(event.object)

    def _on_property_selected(self, event):
        self.fastview.start(event.object, event.bounds)
        o = event.object
        if event.bounds != None:
            self.supplied_data.end()
            return
        if isinstance(o, MineObject):
            _type = "MINE_OBJECT"
        elif isinstance(o, Station):
            _type = "STATION"
        elif isinstance(o, BoreHole):
            _type = "BOREHOLE"
        elif isinstance(o, OrigSampleSet):
            _type = "ORIG_SAMPLE_SET"
        elif isinstance(o, RockBurst):
            _type = "ROCK_BURST"
        elif isinstance(o, PMTestSeries):
            _type = "PM_TEST_SERIES"
        else:
            self.supplied_data.end()
            return

        self.supplied_data.start(o, _type)

    def _on_exit(self, event):
        self.Close()

    def _on_close(self, event):
        if self.notebook.close_all():
            event.Skip()

        self._config_provider["perspective"] = self.mgr.SavePerspective()
        x, y = self.GetScreenPosition().Get()
        size: wx.Size = self.GetSize()
        self._config_provider["window"] = {
            "x": x,
            "y": y,
            "width": size.GetWidth(),
            "height": size.GetHeight(),
        }
        self._config_provider.flush()
        wx.App.GetInstance().ExitMainLoop()