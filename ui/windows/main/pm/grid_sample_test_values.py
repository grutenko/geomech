from dataclasses import dataclass

import wx
from pony.orm import *

from database import PmProperty, PmTestEquipment, PmTestMethod
from ui.widgets.grid.widget import Column, FloatCellType, GridEditor, Model

from ..grid.choice_cell_type import ChoiceCellType
from ..notebook.widget import BasicEditor


@dataclass
class _Row: ...


class _Model(Model):
    @db_session
    def __init__(self):
        super().__init__()
        self._columns = {}
        _methods = []
        for o in select(o for o in PmTestMethod):
            _methods.append(o.Name)
        self._columns["@method"] = Column("@method", ChoiceCellType(_methods), "Метод", "Метод испытаний", init_width=250)
        _equipment = []
        for o in select(o for o in PmTestEquipment):
            _equipment.append(o.Name)
        self._columns["@equipment"] = Column("@equipment", ChoiceCellType(_equipment), "Оборудование", "Оборудование", init_width=250)
        _property = []
        for o in select(o for o in PmProperty):
            _property.append(o.Name)
        self._columns["@property"] = Column("@property", ChoiceCellType(_property), "Свойство", "Свойство", init_width=250)
        self._columns["@value"] = Column("@value", FloatCellType(), "Значение", "Значение")

    def get_columns(self):
        return list(self._columns.values())


class GridSampleTests(BasicEditor):
    def __init__(self, parent, _id, series, menubar, toolbar, statusbar):
        super().__init__(parent, "Испытания: " + series.Name, _id)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.splitter.SetSashGravity(0)
        self.splitter.SetMinimumPaneSize(200)
        main_sizer.Add(self.splitter, 1, wx.EXPAND)

        self.list = wx.ListCtrl(self.splitter, style=wx.LC_LIST | wx.LC_SINGLE_SEL)
        self.table_container = wx.Panel(self.splitter)
        self.table_container_sz = wx.BoxSizer(wx.VERTICAL)
        self.table_container.SetSizer(self.table_container_sz)

        self.table_deputy = wx.Panel(self.table_container)
        table_deputy_sz = wx.BoxSizer(wx.VERTICAL)
        self.table_deputy.SetSizer(table_deputy_sz)
        label = wx.StaticText(self.table_deputy, label="Выберите образец в списке.")
        table_deputy_sz.Add(label, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=20)
        self.table_deputy.Layout()

        self.table_container_sz.Add(self.table_deputy)
        self.splitter.SplitVertically(self.list, self.table_container, 250)

        self.SetSizer(main_sizer)
        self.Layout()

        self.tables = {}
        self.current_table = self.table_deputy
