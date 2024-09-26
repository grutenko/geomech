import wx
import wx.aui
import wx.aui

from ui.icon import get_icon
from ui.class_config_provider import ClassConfigProvider
from .objects import Objects, EVT_OBJECT_SELECTED
from .editor import *
from .editor.help import HelpPage
from .editor.widget import EVT_ENB_STATE_CHANGED
from .fastview import FastView
from .supplied_data import SuppliedData
from .main_menu import *
from .main_toolbar import *

__CONFIG_VERSION__ = 1


class MainFrame(wx.Frame):
    def __init__(self, config):
        super().__init__(None)
        self.SetMinSize(wx.Size(600, 300))
        self.SetSize(1280, 700)
        self.SetTitle('База даных "Геомеханики"')
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnScreen()
        self._config = config

        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

        self.menu_bar = MainMenu()
        self.SetMenuBar(self.menu_bar)
        self.toolbar = MainToolbar(self)
        self.SetToolBar(self.toolbar)

        self.mgr = wx.aui.AuiManager(
            self, flags=wx.aui.AUI_MGR_DEFAULT | wx.aui.AUI_MGR_LIVE_RESIZE
        )

        self.statusbar = wx.StatusBar(self)
        self.statusbar.SetFieldsCount(4)
        self.SetStatusBar(self.statusbar)

        i = wx.aui.AuiPaneInfo()
        i.Left()
        i.MaximizeButton(True)
        i.CloseButton(True)
        i.Name("objects")
        i.Caption("Объекты")
        i.MinSize(300, 300)
        i.BestSize(300, 600)
        self.objects = Objects(self, self.menu_bar, self.toolbar, self.statusbar)
        info = self.objects.get_pane_info()
        if info != None:
            self.mgr.LoadPaneInfo(info, i)
        else:
            self.objects.save_pane_info(self.mgr.SavePaneInfo(i))
        self.mgr.AddPane(self.objects, i)

        i = wx.aui.AuiPaneInfo()
        i.CenterPane()
        i.Name("editors")
        self.editors = EditorNotebook(self, self.menu_bar, self.statusbar, self.toolbar)
        info = self.editors.get_pane_info()
        if info != None:
            self.mgr.LoadPaneInfo(info, i)
        else:
            self.editors.save_pane_info(self.mgr.SavePaneInfo(i))
        self.mgr.AddPane(self.editors, i)

        i = wx.aui.AuiPaneInfo()
        i.Right()
        i.MaximizeButton(True)
        i.CloseButton(True)
        i.Name("fastview")
        i.Caption("Быстрый просмотр")
        i.MinSize(300, 300)
        i.BestSize(300, 600)
        self.fastview = FastView(self)
        i.Hide()
        info = self.fastview.get_pane_info()
        if info != None:
            self.mgr.LoadPaneInfo(info, i)
        else:
            self.fastview.save_pane_info(self.mgr.SavePaneInfo(i))
        self.mgr.AddPane(self.fastview, i)

        i = wx.aui.AuiPaneInfo()
        i.Bottom()
        i.MaximizeButton(True)
        i.CloseButton(True)
        i.Name("supplied_data")
        i.Caption("Сопутствующие материалы")
        i.MinSize(300, 200)
        i.BestSize(600, 200)
        i.Hide()
        self.supplied_data = SuppliedData(self)
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
        self.Show()
        self.editors.add_editor(HelpPage(self.editors))

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
        menu.Bind(wx.EVT_MENU, self._on_exit, id=wx.ID_EXIT)
        menu.Bind(wx.EVT_MENU, self._on_toggle_objects, id=ID_OBJECTS_TOGGLE)
        menu.Bind(wx.EVT_MENU, self._on_toggle_fastview, id=ID_FASTVIEW_TOGGLE)
        menu.Bind(
            wx.EVT_MENU, self._on_toggle_supplied_data, id=ID_SUPPLIED_DATA_TOGGLE
        )
        tb = self.toolbar
        tb.Bind(wx.EVT_TOOL, self._on_editor_save, id=wx.ID_SAVE)
        tb.Bind(wx.EVT_TOOL, self._on_editor_copy, id=wx.ID_COPY)
        tb.Bind(wx.EVT_TOOL, self._on_editor_cut, id=wx.ID_CUT)
        tb.Bind(wx.EVT_TOOL, self._on_editor_paste, id=wx.ID_PASTE)
        tb.Bind(wx.EVT_TOOL, self._on_editor_undo, id=wx.ID_UNDO)
        tb.Bind(wx.EVT_TOOL, self._on_editor_redo, id=wx.ID_REDO)
        self.Bind(wx.EVT_CLOSE, self._on_close)
        # self.editors.Bind(EVT_NOTEBOOK_PAGE_COUNT_CHANGED, self._on_page_count_changed)
        # self.editors.Bind(EVT_NOTEBOOK_PAGE_SELECTION_CHANGED, self._on_notebook_selection_changed)
        # self.editors.Bind(EVT_NOTEBOOK_STATE_CHANGED, self._on_notebook_state_changed)
        self.Bind(wx.aui.EVT_AUI_PANE_CLOSE, self._on_pane_closed)
        self.Bind(wx.aui.EVT_AUI_PANE_RESTORE, self._on_pane_restored)
        self.editors.Bind(EVT_ENB_STATE_CHANGED, self._on_editors_state_changed)
        self.objects.Bind(EVT_OBJECT_SELECTED, self._on_object_selected)

    def _on_find(self, event): ...

    def _on_find_next(self, event): ...

    def _on_pane_closed(self, event):
        if event.GetPane().name == 'objects':
            self._update_controls_state(objects_shown=False)
        elif event.GetPane().name == 'fastview':
            self._update_controls_state(fastview_shown=False)
        elif event.GetPane().name == 'supplied_data':
            self._update_controls_state(supplied_data_shown=False)

    def _on_pane_restored(self, event):
        if event.GetPane().name == 'objects':
            self._update_controls_state(objects_shown=True)
        elif event.GetPane().name == 'fastview':
            self._update_controls_state(fastview_shown=True)
        elif event.GetPane().name == 'supplied_data':
            self._update_controls_state(supplied_data_shown=True)

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
        _id = event.identity
        self.fastview.start(_id)

    def _on_toggle_objects(self, event):
        if self.menu_bar.IsChecked(ID_OBJECTS_TOGGLE):
            self.mgr.GetPane("objects").Show()
        else:
            self.mgr.GetPane("objects").Hide()
        self.mgr.Update()

    def _on_toggle_fastview(self, event):
        if self.menu_bar.IsChecked(ID_FASTVIEW_TOGGLE):
            self.mgr.GetPane("fastview").Show()
        else:
            self.mgr.GetPane("fastview").Hide()
        self.mgr.Update()

    def _on_toggle_supplied_data(self, event):
        if self.menu_bar.IsChecked(ID_SUPPLIED_DATA_TOGGLE):
            self.mgr.GetPane("supplied_data").Show()
        else:
            self.mgr.GetPane("supplied_data").Hide()
        self.mgr.Update()

    def _on_close(self, event):
        i = self.mgr.GetPane("objects")
        self.objects.save_pane_info(self.mgr.SavePaneInfo(i))
        i = self.mgr.GetPane("editors")
        self.editors.save_pane_info(self.mgr.SavePaneInfo(i))
        i = self.mgr.GetPane("fastview")
        self.fastview.save_pane_info(self.mgr.SavePaneInfo(i))
        i = self.mgr.GetPane("supplied_data")
        self.supplied_data.save_pane_info(self.mgr.SavePaneInfo(i))
        event.Skip()

    def _update_controls_state(
        self, objects_shown=None, fastview_shown=None, supplied_data_shown=None
    ):
        self.menu_bar.Enable(wx.ID_CLOSE, self.editors.can_close())
        self.menu_bar.Enable(wx.ID_PREVIEW_NEXT, self.editors.can_go_next_editor())
        self.menu_bar.Enable(wx.ID_PREVIEW_PREVIOUS, self.editors.can_go_prev_editor())
        self.menu_bar.Check(
            ID_OBJECTS_TOGGLE,
            (
                self.mgr.GetPane("objects").IsShown()
                if objects_shown == None
                else objects_shown
            ),
        )
        self.menu_bar.Check(
            ID_FASTVIEW_TOGGLE,
            (
                self.mgr.GetPane("fastview").IsShown()
                if fastview_shown == None
                else fastview_shown
            ),
        )
        self.menu_bar.Check(
            ID_SUPPLIED_DATA_TOGGLE,
            (
                self.mgr.GetPane("supplied_data").IsShown()
                if supplied_data_shown == None
                else supplied_data_shown
            ),
        )
        self.toolbar.EnableTool(wx.ID_SAVE, self.editors.can_save())
        self.toolbar.EnableTool(wx.ID_COPY, self.editors.can_copy())
        self.toolbar.EnableTool(wx.ID_CUT, self.editors.can_cut())
        self.toolbar.EnableTool(wx.ID_PASTE, self.editors.can_paste())
        self.toolbar.EnableTool(wx.ID_UNDO, self.editors.can_undo())
        self.toolbar.EnableTool(wx.ID_REDO, self.editors.can_redo())
        self.menu_bar.Enable(wx.ID_SAVE, self.editors.can_save())
        self.menu_bar.Enable(wx.ID_COPY, self.editors.can_copy())
        self.menu_bar.Enable(wx.ID_CUT, self.editors.can_cut())
        self.menu_bar.Enable(wx.ID_PASTE, self.editors.can_paste())
        self.menu_bar.Enable(wx.ID_UNDO, self.editors.can_undo())
        self.menu_bar.Enable(wx.ID_REDO, self.editors.can_redo())
        self.toolbar.Realize()
