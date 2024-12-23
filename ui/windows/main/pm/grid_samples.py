from dataclasses import dataclass
from typing import Dict

import wx
from pony.orm import *

from database import *
from ui.class_config_provider import ClassConfigProvider
from ui.icon import get_icon
from ui.widgets.grid.widget import Column, FloatCellType, Model, StringCellType
from ui.windows.main.identity import Identity

from ..grid.base import BaseEditor
from ..grid.choice_cell_type import ChoiceCellType
from ..grid.date_cell_type import DateCellType
from .grid_samples_properties_dialog import GridSamplePropertiesDialog

__CONFIG_VERSION__ = 1


@dataclass
class PropertyColumn:
    code: str
    column: Column
    prop: PmProperty
    method: PmTestMethod
    equipment: PmTestEquipment


class ColumnCollection:
    @db_session
    def __init__(self, config):
        self._config_provider = config
        self.columns = {}

        def _width_(name):
            w = config["column_width"]
            if w != None and name in w:
                return w[name]
            return -1

        self.columns["Number"] = Column("Number", StringCellType(), "№*", "Номер образца*", init_width=_width_("Number"))

        data = select(core for core in OrigSampleSet if len(core.discharge_series) == 0 and core.mine_object.Type == "FIELD").order_by(
            lambda x: x.Name
        )

        fields = []
        for o in data:
            n = o.Number.split("@").__getitem__(0)
            fields.append(n)
        self.columns["@orig_sample_set"] = Column(
            "@orig_sample_set", ChoiceCellType(fields), "Набор образцов*", "Набор образцов*", init_width=_width_("@orig_sample_set")
        )

        self.columns["SetDate"] = Column("SetDate", DateCellType(), "Дата отбора *", "Дата отбора *")
        self.columns["StartPosition"] = Column(
            "StartPosition", FloatCellType(), "Начальная\nпозиция, м*", "Начальная позиция, м*", init_width=_width_("StartPosition")
        )
        self.columns["EndPosition"] = Column(
            "EndPosition",
            FloatCellType(),
            "Конечная\nпозиция, м",
            "Конечная позиция, м",
            optional=True,
            init_width=_width_("@pm_sample_set"),
        )
        self.columns["BoxNumber"] = Column("BoxNumber", StringCellType(), "Ящик №", "Ящик №", optional=True, init_width=_width_("BoxNumber"))
        self.columns["Length1"] = Column(
            "Length1",
            FloatCellType(),
            "Диаметр /\nсторона 1, см",
            "Диаметр / сторона 1, см",
            optional=True,
            init_width=_width_("Length1"),
        )
        self.columns["Length2"] = Column("Length2", FloatCellType(), "Сторона 2, см", "Сторона 2, см", optional=True, init_width=_width_("Length2"))
        self.columns["Height"] = Column("Height", FloatCellType(), "Высота, см", "Высота, см", optional=True, init_width=_width_("Height"))
        self.columns["MassAirDry"] = Column(
            "MassAirDry",
            FloatCellType(),
            "Масса в воздушно\nсухом состоянии, г",
            "Масса в воздушно-сухом состоянии",
            optional=True,
            init_width=_width_("MassAirDry"),
        )

        self.props: Dict[str, PropertyColumn] = {}

    @db_session
    def append_prop(self, code, method, equipment):
        def _width_(name):
            w = self._config_provider["column_width"]
            if w != None and name in w:
                return w[name]
            return -1

        if code not in self.props:
            o = PmProperty.get(code=code)
            prop = PropertyColumn(code, Column(code, FloatCellType(), o.Name, o.Name, _width_(code)), method, equipment)
            self.props[code] = prop

    def remove_prop(self, code):
        if code in self.props:
            del self.props[code]

    def get_columns(self):
        return list(self.columns.values()) + list(map(lambda c: c.column, self.props.values()))


class GridSamplesModel(Model):
    @db_session
    def __init__(self, sample_set, config):
        self.sample_set = sample_set
        self._config_provider = config
        self.columns = ColumnCollection(config)

    def get_columns(self):
        return self.columns.get_columns()

    def on_prop_add(self, prop, method, equipment):
        self.columns.append_prop(prop.Code, method, equipment)

    def on_prop_remove(self, prop):
        self.columns.remove_prop(prop.Code)

    def on_object_updated(self, o): ...


ID_APPLEND_COLUMN = wx.ID_HIGHEST + 384


class GridSamples(BaseEditor):
    @db_session
    def __init__(self, parent, sample_set, menubar, toolbar, statusbar):
        sample_set = PMSampleSet[sample_set.RID]
        self.sample_set = sample_set
        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)
        self._config_provider.flush()
        self.menubar: wx.MenuBar = menubar
        self.toolbar: wx.ToolBar = toolbar
        self.statusbar: wx.StatusBar = statusbar
        super().__init__(
            parent,
            "Образцы: Проба %s, Дог. %s" % (sample_set.Number, sample_set.pm_test_series.Name),
            Identity(sample_set, sample_set, PMSample),
            GridSamplesModel(sample_set, self._config_provider),
            menubar,
            toolbar,
            statusbar,
            header_height=40,
            freezed_cols=1,
        )

    def _on_open_props_editor(self, event):
        dlg = GridSamplePropertiesDialog(self, [], self._on_prop_add, self._on_prop_remove)
        dlg.ShowModal()

    def _on_prop_add(self, prop, method, equipment):
        self.editor._model.on_prop_add(prop, method, equipment)
        self.editor._render()

    def _on_prop_remove(self, prop):
        self.editor._model.on_prop_remove(prop)
        self.editor._render()

    def on_select(self):
        self._tool_1 = self.toolbar.AddTool(ID_APPLEND_COLUMN, "Настроить свойства", get_icon("column"))
        self.toolbar.Bind(wx.EVT_TOOL, self._on_open_props_editor, id=ID_APPLEND_COLUMN)
        super().on_select()

    def on_deselect(self):
        self.toolbar.DeleteTool(ID_APPLEND_COLUMN)
        super().on_deselect()
