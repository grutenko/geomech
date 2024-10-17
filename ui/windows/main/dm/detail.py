import pubsub.pub
import wx

from pony.orm import *
from database import *
import pubsub

from ..editor.widget import EditorNotebook
from ..editor.dm import DMEditor
from ui.icon import get_art, get_icon
from ui.windows.main.identity import Identity


class DischargeDetails(wx.Panel):
    @db_session
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent)
        self.Hide()

        self.menubar = menubar
        self.toolbar = toolbar
        self.statusbar = statusbar

        self.rid = None
        self.o = None
        self.discharge_o = None

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_list = wx.ImageList(16, 16)
        self._table_icon = self._image_list.Add(get_icon("data-sheet"))
        self._list = wx.ListCtrl(self, style=wx.LC_LIST)
        self._list.AssignImageList(self._image_list, wx.IMAGE_LIST_SMALL)
        self._list.AppendColumn("Элемент")
        self._list.InsertItem(1, "Замеры", self._table_icon)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated)
        self._list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_item_menu)
        self.SetSizer(main_sizer)

        pubsub.pub.subscribe(self._on_editor_saved, "editor.saved")

    def _on_item_menu(self, event):
        menu = wx.Menu()
        if event.GetIndex() == 0 and self.o != None:
            n = EditorNotebook.get_instance()
            index, page = n.get_by_identity(Identity(self.o, self.o, DischargeMeasurement))
            if index == -1:
                item = menu.Append(wx.ID_ANY, "Открыть")
                item.SetBitmap(get_icon("table"))
            else:
                item = menu.Append(wx.ID_ANY, "Перейти к открытому редактору")
                item.SetBitmap(get_icon("share"))
            menu.Bind(wx.EVT_MENU, self._open_editor, item)
        self.PopupMenu(menu, event.GetPoint())

    def _on_editor_saved(self, target, editor):
        _id = Identity(self.o, self.o, DischargeMeasurement)
        if editor != None and editor.get_identity() != None and editor.get_identity().__eq__(_id):
            self._render()

    def _on_item_activated(self, event: wx.ListEvent):
        if event.GetIndex() == 0:
            self._open_editor()

    def _open_editor(self, event=None):
        if self.o == None:
            return

        _id = Identity(self.o, self.o, DischargeMeasurement)
        n = EditorNotebook.get_instance()
        if not n.select_by_identity(_id):
            n.add_editor(
                DMEditor(
                    n,
                    _id,
                    self.menubar,
                    self.toolbar,
                    self.statusbar,
                )
            )

    @db_session
    def _render(self):
        if self.rid != None:
            measure_count = select(o for o in DischargeMeasurement if o.orig_sample_set == self.o).count()
            self._list.SetItemText(0, "Замеры (%d)" % measure_count)

    @db_session
    def start(self, rid):
        self.discharge_o = DischargeSeries[rid]
        self.o = OrigSampleSet[self.discharge_o.orig_sample_set.RID]
        self.rid = self.o.RID
        self._render()
        self.Show()

    def get_item_name(self):
        if self.discharge_o != None:
            return self.discharge_o.get_tree_name()
        return ""

    def end(self):
        self.o = None
        self.discharge_o = None
        self.rid = None
        self.Hide()
