import wx
import wx.lib.agw.flatnotebook
import wx.lib.newevent

from database import *
from ui.class_config_provider import ClassConfigProvider
from ui.windows.main.identity import Identity

from .bore_hole import DialogCreateBoreHole
from .core import DialogCreateCore
from .mine_object import DialogCreateMineObject
from .station import DialogCreateStation
from .tree import EVT_TREE_OPEN_SELF_EDITOR, EVT_WIDGET_TREE_SEL_CHANGED, TreeWidget

__CONFIG_VERSION__ = 2

ObjectSelectedEvent, EVT_OBJECT_SELECTED = wx.lib.newevent.NewEvent()


class Objects(wx.Panel):
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._tree_search = wx.SearchCtrl(self)
        menu = wx.Menu()
        item = menu.AppendRadioItem(1, "Искать все")
        item.Check(True)
        item = menu.AppendRadioItem(2, "Только Регионы")
        item = menu.AppendRadioItem(3, "Только Горные массивы")
        item = menu.AppendRadioItem(4, "Только Месторождения")
        item = menu.AppendRadioItem(5, "Только Станции")
        item = menu.AppendRadioItem(6, "Только Скважины")
        self._tree_search.SetMenu(menu)
        self._tree_search.SetDescriptiveText("Введите часть названия")
        main_sizer.Add(self._tree_search, 0, wx.EXPAND)

        self.tree = TreeWidget(self)
        main_sizer.Add(self.tree, 1, wx.EXPAND)

        self._view_choice = wx.Choice(
            self,
            choices=[
                "Показывать все",
                "Только Горные объекты",
                "Только Станции",
                "Только Скважины",
            ],
        )
        self._view_choice.Bind(wx.EVT_CHOICE, self._on_change_mode)
        self._view_choice.SetSelection(0)
        main_sizer.Add(self._view_choice, 0, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()

        self._bind_all()

        self._current_mode = "all"
        self._update_controls_state()

    def _update_controls_state(self):
        _mode = self._current_mode
        _menu = self._tree_search.GetMenu()
        _menu.Enable(1, _mode == "all")
        _menu.Enable(2, _mode in ["all", "mine_objects"])
        _menu.Enable(3, _mode in ["all", "mine_objects"])
        _menu.Enable(4, _mode in ["all", "mine_objects"])
        _menu.Enable(5, _mode in ["all", "stations"])
        _menu.Enable(6, _mode in ["all", "bore_holes"])

    def _on_change_mode(self, event):
        if self._view_choice.GetSelection() == 0:
            _mode = "all"
            self.tree.change_mode("all")
        elif self._view_choice.GetSelection() == 1:
            _mode = "mine_objects"
        elif self._view_choice.GetSelection() == 2:
            _mode = "stations"
        elif self._view_choice.GetSelection() == 3:
            _mode = "bore_holes"
        else:
            return
        self.tree.change_mode(_mode)
        self._current_mode = _mode
        self._update_controls_state()

    def _bind_all(self):
        self.tree.Bind(EVT_WIDGET_TREE_SEL_CHANGED, self._on_sel_changed)
        self.tree.Bind(EVT_TREE_OPEN_SELF_EDITOR, self._on_open_self_editor)

    def _on_open_self_editor(self, event):
        if event.target == None:
            return
        window = wx.GetApp().GetTopWindow().FindFocus().GetTopLevelParent()
        if isinstance(event.target, MineObject):
            dlg = DialogCreateMineObject(window, event.target, _type="UPDATE")
        elif isinstance(event.target, Station):
            dlg = DialogCreateStation(window, event.target, _type="UPDATE")
        elif isinstance(event.target, BoreHole):
            dlg = DialogCreateBoreHole(window, event.target, _type="UPDATE")
        elif isinstance(event.target, OrigSampleSet):
            dlg = DialogCreateCore(window, event.target, _type="UPDATE")
        else:
            return
        if dlg.ShowModal() == wx.ID_OK:
            self.tree.reload_object(event.target)

    def _on_sel_changed(self, event):
        if event.node == None:
            return
        _id = Identity(event.node.o, event.node.o)
        wx.PostEvent(self, ObjectSelectedEvent(target=self, identity=_id))

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()

    def _on_page_changed(self, event: wx.BookCtrlEvent):
        if self._notebook_configured:
            self._config_provider["notebook_page"] = self._notebook.GetSelection()
            self._config_provider.flush()

    def remove_selection(self, silence=False):
        self.tree._tree.UnselectAll()

    def select_by_identity(self, identity):
        if identity.rel_data_target != None:
            return
        if (
            not isinstance(identity.rel_data_o, MineObject)
            and not isinstance(identity.rel_data_o, Station)
            and not isinstance(identity.rel_data_o, BoreHole)
            and not isinstance(identity.rel_data_o, OrigSampleSet)
        ):
            return
        self.tree.select_by_identity(identity)
