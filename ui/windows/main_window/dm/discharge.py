import wx

from pony.orm import *
from database import *

from ui.windows.main_window.editor.widget import EditorNotebook
from ui.windows.main_window.editor.dm import DMEditor
from ui.icon import get_art, get_icon
from ui.windows.main_window.identity import Identity


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

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_list = wx.ImageList(16, 16)
        self._link_icon = self._image_list.Add(get_icon("link"))
        self._info_icon = self._image_list.Add(get_art(wx.ART_INFORMATION))
        self._help_page_icon = self._image_list.Add(get_art(wx.ART_HELP_PAGE))
        self._info_icon = self._image_list.Add(get_art(wx.ART_INFORMATION))
        self._table_icon = self._image_list.Add(get_art(wx.ART_REPORT_VIEW))
        self._list = wx.ListCtrl(self, style=wx.LC_LIST)
        self._list.AssignImageList(self._image_list, wx.IMAGE_LIST_SMALL)
        self._list.AppendColumn("Элемент")
        self._list.InsertItem(0, "[Керн]", self._link_icon)
        self._list.InsertItem(1, "[Набор замеров]", self._info_icon)
        self._list.InsertItem(2, "Ящики", self._table_icon)
        self._list.InsertItem(3, "Замеры", self._table_icon)
        main_sizer.Add(self._list, 1, wx.EXPAND)
        self._list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self._on_item_activated)
        self.SetSizer(main_sizer)

    def _on_item_activated(self, event: wx.ListEvent):
        if event.GetIndex() == 3:
            if self.o != None:
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
    def start(self, rid):
        o = DischargeSeries[rid]
        self.o = OrigSampleSet[o.orig_sample_set.RID]
        measure_count = select(o for o in DischargeMeasurement if o.orig_sample_set == self.o).count()
        self._list.SetItemText(3, "Замеры (%d)" % measure_count)
        self.rid = self.o.RID
        self.Show()

    def end(self):
        self.rid = None
        self.Hide()
