import pubsub.pub
import wx
import wx.aui
import wx.adv
import wx.lib.agw.aui

import pubsub
from version import __GEOMECH_VERSION__
from database import *
from ui.icon import get_icon
from ui.class_config_provider import ClassConfigProvider
from .o import Objects, EVT_OBJECT_SELECTED
from .dm.widget import DischargePanel, EVT_Dm_SELECTED
from .pm.widget import PmPanel, EVT_PM_SELECTED
from .rb.widget_new import RbPanel, EVT_RB_SELECTED
from .editor import *
from .editor.md_viewer import MdViewer
from .editor.widget import EVT_ENB_STATE_CHANGED, EVT_ENB_EDITOR_CLOSED
from .editor.import_stations import ImportStations
from .fastview import FastView
from .sd import SuppliedData
from .menu import *
from .toolbar import *
from .mgr_panel_toolbar import *
from .identity import Identity
from ui.windows.cs.main import ManageCoordSystemsWindow
from ui.windows.pm.main import PmSettingsWindow
from ui.windows.doc.main import ManageDocumentsWindow
from .editor.import_bore_holes import ImportBoreHoles

__CONFIG_VERSION__ = 2


class MainFrame(wx.Frame):
    @db_session
    def __init__(self, config):
        self._frame_initialized = False
        super().__init__(None)
        self.SetMinSize(wx.Size(int(300 * 1.618), 300))
        self.SetSize(1280, 720)
        self.SetTitle('База даных "Геомеханики"')
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnScreen()
        self._config = config

        self._disable_controls = False

        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)

        self.menu_bar = MainMenu()
        self.SetMenuBar(self.menu_bar)

        self.toolbar = MainToolbar(self)
        self.SetToolBar(self.toolbar)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mgr_panel_toolbar = MgrPanelToolbar(self)
        main_sizer.Add(self.mgr_panel_toolbar, 0, wx.EXPAND)
        mgr_panel = wx.Panel(self)
        self.mgr_panel = mgr_panel
        main_sizer.Add(mgr_panel, 1, wx.EXPAND)

        self.mgr_panel_toolbar.Realize()

        self.SetSizer(main_sizer)

        self.mgr = wx.aui.AuiManager(
            mgr_panel,
            flags=wx.aui.AUI_MGR_DEFAULT
            | wx.aui.AUI_MGR_LIVE_RESIZE
            | wx.aui.AUI_MGR_RECTANGLE_HINT
            | wx.aui.AUI_MGR_ALLOW_ACTIVE_PANE
            | wx.aui.AUI_MGR_TRANSPARENT_DRAG,
        )

        self.statusbar = wx.StatusBar(self)
        self.statusbar.SetFieldsCount(4)
        self.SetStatusBar(self.statusbar)

        i = wx.aui.AuiPaneInfo()
        i.CloseButton(True)
        i.Gripper()
        i.GripperTop()
        i.Name("objects")
        i.PinButton()
        i.Caption("Объекты")
        i.MinSize(300, 200)
        i.MinSize(300, 200)
        i.MaxSize(600, 900)
        i.Icon(get_icon("hierarchy"))
        i.Hide()
        self.objects = Objects(mgr_panel, self.menu_bar, self.toolbar, self.statusbar)
        info = self.objects.get_pane_info()
        if info != None:
            self.mgr.LoadPaneInfo(info, i)
        else:
            self.objects.save_pane_info(self.mgr.SavePaneInfo(i))
        self.mgr.AddPane(self.objects, i)

        i = wx.aui.AuiPaneInfo()
        i.Top()
        i.Gripper()
        i.GripperTop()
        i.CloseButton(True)
        i.PinButton()
        i.PaneBorder()
        i.Name("dm")
        i.Caption("Разгрузка")
        i.MaximizeButton()
        i.MinSize(300, 200)
        i.MaxSize(600, 900)

        i.Icon(get_icon("book-stack"))
        i.Hide()
        self.dm = DischargePanel(mgr_panel, self.menu_bar, self.toolbar, self.statusbar)
        info = self.dm.get_pane_info()
        if info != None:
            self.mgr.LoadPaneInfo(info, i)
        else:
            self.dm.save_pane_info(self.mgr.SavePaneInfo(i))
        self.mgr.AddPane(self.dm, i)

        i = wx.aui.AuiPaneInfo()
        i.Top()
        i.Gripper()
        i.GripperTop()
        i.CloseButton(True)
        i.Name("pm")
        i.PinButton()
        i.Caption("Физ. мех. свойства")
        i.MaximizeButton()
        i.MinSize(300, 200)
        i.MaxSize(600, 900)

        i.Icon(get_icon("book-stack"))
        i.Hide()
        self.pm = PmPanel(mgr_panel)
        info = self.pm.get_pane_info()
        if info != None:
            self.mgr.LoadPaneInfo(info, i)
        else:
            self.pm.save_pane_info(self.mgr.SavePaneInfo(i))
        self.mgr.AddPane(self.pm, i)

        i = wx.aui.AuiPaneInfo()
        i.Top()
        i.MaximizeButton()
        i.Gripper()
        i.GripperTop()
        i.CloseButton(True)
        i.PaneBorder()
        i.Name("rb")
        i.PinButton()
        i.Caption("Горные удары")
        i.MinSize(300, 200)
        i.MaxSize(600, 900)

        i.Icon(get_icon("book-stack"))
        i.Hide()
        self.rb = RbPanel(mgr_panel)
        info = self.rb.get_pane_info()
        if info != None:
            self.mgr.LoadPaneInfo(info, i)
        else:
            self.rb.save_pane_info(self.mgr.SavePaneInfo(i))
        self.mgr.AddPane(self.rb, i)

        i = wx.aui.AuiPaneInfo()
        i.Center()
        i.Name("editors")
        i.CaptionVisible(False)
        i.MinSize(200, 300)
        i.CloseButton(False)
        self.editors = EditorNotebook(mgr_panel, self.menu_bar, self.statusbar, self.toolbar)
        self.mgr.AddPane(self.editors, i)

        i = wx.aui.AuiPaneInfo()
        i.Right()
        i.Gripper()
        i.GripperTop()
        i.CloseButton(True)
        i.PinButton()
        i.Name("fastview")
        i.PaneBorder()
        i.Caption("Быстрый просмотр")
        i.Icon(get_icon("show-property"))
        i.MinSize(300, 200)
        i.BestSize(300, 600)
        self.fastview = FastView(mgr_panel)
        i.Hide()
        info = self.fastview.get_pane_info()
        if info != None:
            self.mgr.LoadPaneInfo(info, i)
        else:
            self.fastview.save_pane_info(self.mgr.SavePaneInfo(i))
        self.mgr.AddPane(self.fastview, i)

        i = wx.aui.AuiPaneInfo()
        i.Bottom()
        i.CloseButton(True)
        i.Gripper()
        i.GripperTop()
        i.PinButton()
        i.PaneBorder()
        i.Name("supplied_data")
        i.Caption("Сопутствующие материалы")
        i.MinSize(300, 200)
        i.BestSize(600, 200)
        i.Hide()
        i.Icon(get_icon("versions"))
        self.supplied_data = SuppliedData(mgr_panel)
        info = self.supplied_data.get_pane_info()
        if info != None:
            self.mgr.LoadPaneInfo(info, i)
        else:
            self.supplied_data.save_pane_info(self.mgr.SavePaneInfo(i))
        self.mgr.AddPane(self.supplied_data, i)

        self.mgr.Update()
        self.Layout()

        self._bind_all()
        self._update_controls_state()
        self._start_tab = MdViewer(self.editors, "[Чтение] Начало работы", "start")
        self._start_tab.set_file("start/index.md")
        self.editors.add_editor(self._start_tab)

        self._pm_settings_window = PmSettingsWindow(self)
        self._cs_settings_window = ManageCoordSystemsWindow(self)
        self._docs_window = ManageDocumentsWindow(self)

        self._root_object = select(o for o in MineObject if o.Level == 0).first()

        if self._config_provider["width"] != None and self._config_provider["height"] != None:
            self.SetSize(self._config_provider["width"], self._config_provider["height"])
        if self._config_provider["x"] != None and self._config_provider["y"] != None:
            self.SetPosition(wx.Point(self._config_provider["x"], self._config_provider["y"]))

        self.Show()
        self._frame_initialized = True

    def _bind_all(self):
        menu = self.menu_bar
        menu.Bind(wx.EVT_MENU, self._on_find, id=wx.ID_FIND)
        menu.Bind(wx.EVT_MENU, self._on_find_next, id=ID_FIND_NEXT)
        menu.Bind(wx.EVT_MENU, self._on_editor_save, id=wx.ID_SAVE)
        menu.Bind(wx.EVT_MENU, self._on_editor_copy, id=wx.ID_COPY)
        menu.Bind(wx.EVT_MENU, self._on_editor_cut, id=wx.ID_CUT)
        menu.Bind(wx.EVT_MENU, self._on_editor_paste, id=wx.ID_PASTE)
        menu.Bind(wx.EVT_MENU, self._on_editor_undo, id=wx.ID_UNDO)
        menu.Bind(wx.EVT_MENU, self._on_editor_redo, id=wx.ID_REDO)
        menu.Bind(wx.EVT_MENU, self._on_editor_next, id=wx.ID_PREVIEW_NEXT)
        menu.Bind(wx.EVT_MENU, self._on_editor_prev, id=wx.ID_PREVIEW_PREVIOUS)
        menu.Bind(wx.EVT_MENU, self._on_editor_close, id=wx.ID_CLOSE)
        menu.Bind(wx.EVT_MENU, self._on_about_dialog, id=wx.ID_ABOUT)
        menu.Bind(wx.EVT_MENU, self._on_exit, id=wx.ID_EXIT)
        menu.Bind(wx.EVT_MENU, self._on_toggle_objects, id=ID_OBJECTS_TOGGLE)
        menu.Bind(wx.EVT_MENU, self._on_open_cs_settings_window, id=ID_SETTINGS_CS)
        menu.Bind(wx.EVT_MENU, self._on_toggle_fastview, id=ID_FASTVIEW_TOGGLE)
        menu.Bind(wx.EVT_MENU, self._on_toggle_start, id=ID_OPEN_START_TAB)
        menu.Bind(wx.EVT_MENU, self._on_open_pm_settings_window, id=ID_SETTINGS_PM)
        menu.Bind(wx.EVT_MENU, self._on_toggle_supplied_data, id=ID_SUPPLIED_DATA_TOGGLE)
        menu.Bind(wx.EVT_MENU, self._on_toggle_dm, id=ID_DM_TOGGLE)
        menu.Bind(wx.EVT_MENU, self._on_toggle_pm, id=ID_PM_TOGGLE)
        menu.Bind(wx.EVT_MENU, self._on_toggle_rb, id=ID_RB_TOGGLE)
        menu.Bind(wx.EVT_MENU, self._on_toggle_import_bore_holes, id=ID_IMPORT_BORE_HOLES)
        menu.Bind(wx.EVT_MENU, self._on_toggle_import_stations, id=ID_IMPORT_STATIONS)
        menu.Bind(wx.EVT_MENU, self._on_open_docs_window, id=ID_SETTINGS_DOCS)
        tb = self.toolbar
        tb.Bind(wx.EVT_TOOL, self._on_editor_save, id=wx.ID_SAVE)
        tb.Bind(wx.EVT_TOOL, self._on_editor_copy, id=wx.ID_COPY)
        tb.Bind(wx.EVT_TOOL, self._on_editor_cut, id=wx.ID_CUT)
        tb.Bind(wx.EVT_TOOL, self._on_editor_paste, id=wx.ID_PASTE)
        tb.Bind(wx.EVT_TOOL, self._on_editor_undo, id=wx.ID_UNDO)
        tb.Bind(wx.EVT_TOOL, self._on_editor_redo, id=wx.ID_REDO)
        mgrtb = self.mgr_panel_toolbar
        mgrtb.Bind(wx.EVT_TOOL, self._on_toggle_objects, id=ID_TOGGLE_OBJECTS)
        mgrtb.Bind(wx.EVT_TOOL, self._on_toggle_fastview, id=ID_TOGGLE_FASTVIEW)
        mgrtb.Bind(wx.EVT_TOOL, self._on_toggle_supplied_data, id=ID_TOGGLE_SUPPLIED_DATA)
        mgrtb.Bind(wx.EVT_TOOL, self._on_toggle_dm, id=ID_TOGGLE_DISCHARGE)
        mgrtb.Bind(wx.EVT_TOOL, self._on_toggle_pm, id=ID_TOGGLE_PM)
        mgrtb.Bind(wx.EVT_TOOL, self._on_toggle_rb, id=ID_TOGGLE_ROCK_BURST)
        mgrtb.Bind(wx.EVT_TOOL, self._on_toggle_dropdown, id=ID_TOGGLE_CONTAINER)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        self.mgr_panel.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self._on_pane_closed)
        self.mgr_panel.Bind(wx.aui.EVT_AUI_PANE_RESTORE, self._on_pane_restored)
        self.editors.Bind(EVT_ENB_STATE_CHANGED, self._on_editors_state_changed)
        self.objects.Bind(EVT_OBJECT_SELECTED, self._on_object_selected)
        self.editors.Bind(EVT_ENB_EDITOR_CLOSED, self._on_editor_closed)
        self.dm.Bind(EVT_Dm_SELECTED, self._on_object_selected)
        self.pm.Bind(EVT_PM_SELECTED, self._on_object_selected)
        self.rb.Bind(EVT_RB_SELECTED, self._on_object_selected)
        self.mgr_panel.Bind(wx.aui.EVT_AUI_PANE_BUTTON, self._on_pane_maximized)
        self.Bind(wx.EVT_SIZE, self._on_resize, self)
        self.Bind(wx.EVT_MOVE_END, self._on_move, self)
        pubsub.pub.subscribe(self._cmd_on_select_object, "cmd.object.select")
        pubsub.pub.subscribe(self._cmd_on_show_supplied_data, "cmd.supplied_data.show")
        pubsub.pub.subscribe(self._cmd_dm_select, "cmd.dm.select")
        pubsub.pub.subscribe(self._on_object_added, "object.added")
        pubsub.pub.subscribe(self._cmd_on_close_editor, "cmd.editor.close")
        pubsub.pub.subscribe(self._cmd_on_open_editor, "cmd.editor.open")

    def _on_open_docs_window(self, event):
        if self._docs_window.IsShown():
            self._docs_window.Raise()
        else:
            self._docs_window.Show()

    def _cmd_on_open_editor(self, target, editor):
        self.editors.add_editor(editor)

    def _cmd_on_close_editor(self, target, identity):
        index, editor = self.editors.get_by_identity(identity)
        if index != -1:
            self.editors.close_editor(editor)

    def _on_object_added(self, objects):
        self.objects.reload_for_new_objects(objects)

    def _on_toggle_import_stations(self, event):
        index, page = self.editors.get_by_identity(Identity(self._root_object, self._root_object, "import_stations"))
        if page != None:
            self.editors.select_by_index(index)
        else:
            self.editors.add_editor(ImportStations(self.editors, self.menu_bar, self.toolbar, self.statusbar))

    def _on_toggle_import_bore_holes(self, event):
        index, page = self.editors.get_by_identity(Identity(self._root_object, self._root_object, "import_bore_holes"))
        if page != None:
            self.editors.select_by_index(index)
        else:
            self.editors.add_editor(ImportBoreHoles(self.editors, self.menu_bar, self.toolbar, self.statusbar))

    def _cmd_dm_select(self, target, identity):
        if not self.mgr.GetPane("dm").IsShown():
            self.mgr.GetPane("dm").Show()
            self.mgr.Update()
            self._update_controls_state()
        self.dm.select_by_identity(identity)

    def _cmd_on_show_supplied_data(self, target):
        if not self.mgr.GetPane("supplied_data").IsShown():
            self.mgr.GetPane("supplied_data").Show()
            self.mgr.Update()
            self._update_controls_state()

    def _cmd_on_select_object(self, target, identity):
        if not self.mgr.GetPane("objects").IsShown():
            self.mgr.GetPane("objects").Show()
            self.mgr.Update()
            self._update_controls_state()
        self.objects.select_by_identity(identity)

    def _on_toggle_dropdown(self, event):
        pos = wx.GetMousePosition()
        self.mgr_panel_toolbar.PopupMenu(self.mgr_panel_toolbar._dropdown, self.mgr_panel_toolbar.ScreenToClient(pos))

    def _on_toggle_dm(self, event):
        self.mgr.GetPane("dm").Show(event.IsChecked())
        self.mgr.Update()
        self._update_controls_state()

    def _on_toggle_pm(self, event):
        self.mgr.GetPane("pm").Show(event.IsChecked())
        self.mgr.Update()
        self._update_controls_state()

    def _on_toggle_rb(self, event):
        self.mgr.GetPane("rb").Show(event.IsChecked())
        self.mgr.Update()
        self._update_controls_state()

    def _on_move(self, event):
        if not self.IsFullScreen():
            pos = self.GetPosition()
            self._config_provider["x"] = pos.x
            self._config_provider["y"] = pos.y
            self._config_provider.flush()
        event.Skip()

    def _on_resize(self, event: wx.SizeEvent):
        if not self.IsFullScreen() and self._frame_initialized:
            size = event.GetSize()
            self._config_provider["width"] = size.GetWidth()
            self._config_provider["height"] = size.GetHeight()
            self._config_provider.flush()
        event.Skip()

    def _on_pane_maximized(self, event): ...

    def _on_open_cs_settings_window(self, event):
        if self._cs_settings_window.IsShown():
            self._cs_settings_window.Raise()
        else:
            self._cs_settings_window.Show()

    def _on_open_pm_settings_window(self, event):
        if self._pm_settings_window.IsShown():
            self._pm_settings_window.Raise()
        else:
            self._pm_settings_window.Show()

    def _on_about_dialog(self, event):
        aboutInfo = wx.adv.AboutDialogInfo()
        aboutInfo.SetName('База данных "Геомеханики"')
        aboutInfo.SetVersion(__GEOMECH_VERSION__)
        aboutInfo.SetDescription('Интерфейс базы данных "Геомеханики"')
        aboutInfo.SetCopyright("(C) 2024")

        wx.adv.AboutBox(aboutInfo)

    def _on_editor_closed(self, event):
        if event.identity == "help_page":
            self.menu_bar.Check(ID_OPEN_START_TAB, False)
            self._start_tab = None

    def _on_toggle_start(self, event):
        if self._start_tab != None:
            self.editors.close_editor(self._start_tab)
        else:
            self._start_tab = MdViewer(self.editors, "[Чтение] Начало работы")
            self.editors.add_editor(self._start_tab)

    def _on_find(self, event): ...

    def _on_find_next(self, event): ...

    def _on_pane_closed(self, event):
        if event.GetPane().name == "objects":
            o = self.supplied_data.get_current_object()
            if isinstance(o, MineObject) or isinstance(o, Station) or isinstance(o, BoreHole) or isinstance(o, OrigSampleSet):
                self.supplied_data.end()
            self._update_controls_state(objects_shown=False)
        elif event.GetPane().name == "fastview":
            self._update_controls_state(fastview_shown=False)
        elif event.GetPane().name == "supplied_data":
            self._update_controls_state(supplied_data_shown=False)
        elif event.GetPane().name == "dm":
            self._update_controls_state(dm_shown=False)
        elif event.GetPane().name == "pm":
            self._update_controls_state(pm_shown=False)
        elif event.GetPane().name == "rb":
            self._update_controls_state(rb_shown=False)
        self.Raise()

    def _on_pane_restored(self, event):
        if event.GetPane().name == "objects":
            self._update_controls_state(objects_shown=True)
        elif event.GetPane().name == "fastview":
            self._update_controls_state(fastview_shown=True)
        elif event.GetPane().name == "supplied_data":
            self._update_controls_state(supplied_data_shown=True)
        elif event.GetPane().name == "dm":
            self._update_controls_state(dm_shown=True)
        elif event.GetPane().name == "pm":
            self._update_controls_state(pm_shown=True)
        elif event.GetPane().name == "rb":
            self._update_controls_state(rb_shown=True)

    def _on_editors_state_changed(self, event):
        self._update_controls_state()

    def _on_editor_save(self, event):
        self.editors.save()

    def _on_editor_copy(self, event):
        self.editors.copy()

    def _on_editor_cut(self, event):
        self.editors.cut()

    def _on_editor_paste(self, event):
        self.editors.paste()

    def _on_editor_undo(self, event):
        self.editors.undo()

    def _on_editor_redo(self, event):
        self.editors.redo()

    def _on_editor_next(self, event):
        self.editors.go_next_editor()
        self._update_controls_state()

    def _on_editor_prev(self, event):
        self.editors.go_prev_editor()
        self._update_controls_state()

    def _on_editor_close(self, event):
        self.editors.close()
        self._update_controls_state()

    def _on_page_count_changed(self, event):
        self._update_controls_state()

    def _on_notebook_selection_changed(self, event):
        self._update_controls_state()

    def _on_notebook_state_changed(self, event):
        self._update_controls_state()

    def _on_exit(self, event):
        self.Close()

    def _on_object_selected(self, event):
        _p = [self.objects, self.pm, self.dm, self.rb]
        for pane in _p:
            if not isinstance(pane, type(event.target)):
                pane.remove_selection()
        _id: Identity = event.identity
        if _id != None:
            self.fastview.start(_id)
            self.supplied_data.start(_id)
        else:
            self.fastview.stop()
            self.supplied_data.end()

    def _on_toggle_objects(self, event: wx.CommandEvent):
        print(event.IsChecked())
        self.mgr.GetPane("objects").Show(event.IsChecked())
        self.mgr.Update()
        self._update_controls_state()

    def _on_toggle_fastview(self, event):
        self.mgr.GetPane("fastview").Show(event.IsChecked())
        self.mgr.Update()
        self._update_controls_state()

    def _on_toggle_supplied_data(self, event):
        self.mgr.GetPane("supplied_data").Show(event.IsChecked())
        self.mgr.Update()
        self._update_controls_state()

    def _on_close(self, event):
        i = self.mgr.GetPane("objects")
        self.objects.save_pane_info(self.mgr.SavePaneInfo(i))
        i = self.mgr.GetPane("editors")
        self.editors.save_pane_info(self.mgr.SavePaneInfo(i))
        i = self.mgr.GetPane("fastview")
        self.fastview.save_pane_info(self.mgr.SavePaneInfo(i))
        i = self.mgr.GetPane("supplied_data")
        self.supplied_data.save_pane_info(self.mgr.SavePaneInfo(i))
        i = self.mgr.GetPane("dm")
        self.dm.save_pane_info(self.mgr.SavePaneInfo(i))
        i = self.mgr.GetPane("pm")
        self.pm.save_pane_info(self.mgr.SavePaneInfo(i))
        i = self.mgr.GetPane("rb")
        self.rb.save_pane_info(self.mgr.SavePaneInfo(i))
        pos: wx.Point = self.GetPosition()
        self._config_provider["fullscreen"] = self.IsFullScreen()
        size = self.GetSize()
        self._config_provider.flush()
        event.Skip()
        wx.GetApp().ExitMainLoop()

    def _update_controls_state(
        self,
        objects_shown=None,
        fastview_shown=None,
        supplied_data_shown=None,
        dm_shown=None,
        pm_shown=None,
        rb_shown=None,
    ):
        self.menu_bar.Enable(wx.ID_CLOSE, not self._disable_controls and self.editors.can_close())
        self.menu_bar.Enable(
            wx.ID_PREVIEW_NEXT,
            not self._disable_controls and self.editors.can_go_next_editor(),
        )
        self.menu_bar.Enable(
            wx.ID_PREVIEW_PREVIOUS,
            not self._disable_controls and self.editors.can_go_prev_editor(),
        )
        object_state = self.mgr.GetPane("objects").IsShown() if objects_shown == None else objects_shown
        fastview_state = self.mgr.GetPane("fastview").IsShown() if fastview_shown == None else fastview_shown
        sd_state = self.mgr.GetPane("supplied_data").IsShown() if supplied_data_shown == None else supplied_data_shown
        dm_state = self.mgr.GetPane("dm").IsShown() if dm_shown == None else dm_shown
        pm_state = self.mgr.GetPane("pm").IsShown() if pm_shown == None else pm_shown
        rb_state = self.mgr.GetPane("rb").IsShown() if rb_shown == None else rb_shown
        self.menu_bar.Check(
            ID_OBJECTS_TOGGLE,
            object_state,
        )
        self.menu_bar.Check(
            ID_FASTVIEW_TOGGLE,
            fastview_state,
        )
        self.menu_bar.Check(ID_SUPPLIED_DATA_TOGGLE, sd_state)
        self.menu_bar.Check(ID_DM_TOGGLE, dm_state)
        self.menu_bar.Check(ID_PM_TOGGLE, pm_state)
        self.menu_bar.Check(ID_RB_TOGGLE, rb_state)
        mgrtb = self.mgr_panel_toolbar
        if (
            mgrtb.GetToolState(ID_TOGGLE_OBJECTS) != object_state
            or mgrtb.GetToolState(ID_TOGGLE_FASTVIEW) != fastview_state
            or mgrtb.GetToolState(ID_TOGGLE_SUPPLIED_DATA) != sd_state
            or mgrtb._dropdown.IsChecked(ID_TOGGLE_DISCHARGE) != dm_state
            or mgrtb._dropdown.IsChecked(ID_TOGGLE_PM) != pm_state
            or mgrtb._dropdown.IsChecked(ID_TOGGLE_ROCK_BURST) != rb_state
        ):
            mgrtb.ToggleTool(ID_TOGGLE_OBJECTS, object_state)
            mgrtb.ToggleTool(ID_TOGGLE_FASTVIEW, fastview_state)
            mgrtb.ToggleTool(ID_TOGGLE_SUPPLIED_DATA, sd_state)
            mgrtb._dropdown.Check(ID_TOGGLE_DISCHARGE, dm_state)
            mgrtb._dropdown.Check(ID_TOGGLE_PM, pm_state)
            mgrtb._dropdown.Check(ID_TOGGLE_ROCK_BURST, rb_state)
            mgrtb.Realize()
        self.toolbar.EnableTool(wx.ID_SAVE, not self._disable_controls and self.editors.can_save())
        self.toolbar.EnableTool(wx.ID_COPY, not self._disable_controls and self.editors.can_copy())
        self.toolbar.EnableTool(wx.ID_CUT, not self._disable_controls and self.editors.can_cut())
        self.toolbar.EnableTool(wx.ID_PASTE, not self._disable_controls and self.editors.can_paste())
        self.toolbar.EnableTool(wx.ID_UNDO, not self._disable_controls and self.editors.can_undo())
        self.toolbar.EnableTool(wx.ID_REDO, not self._disable_controls and self.editors.can_redo())
        self.menu_bar.Enable(wx.ID_SAVE, not self._disable_controls and self.editors.can_save())
        self.menu_bar.Enable(wx.ID_COPY, not self._disable_controls and self.editors.can_copy())
        self.menu_bar.Enable(wx.ID_CUT, not self._disable_controls and self.editors.can_cut())
        self.menu_bar.Enable(wx.ID_PASTE, not self._disable_controls and self.editors.can_paste())
        self.menu_bar.Enable(wx.ID_UNDO, not self._disable_controls and self.editors.can_undo())
        self.menu_bar.Enable(wx.ID_REDO, not self._disable_controls and self.editors.can_redo())
        self.toolbar.Realize()
