import logging
from dataclasses import dataclass, field
from typing import Dict

import pubsub
import pubsub.pub
import wx
from pony.orm import commit, db_session, desc, select

from database import (
    OrigSampleSet,
    PmProperty,
    PMSample,
    PmSamplePropertyValue,
    PMSampleSet,
    PmSampleSetUsedProperties,
    PmTestEquipment,
    PmTestMethod,
)
from ui.class_config_provider import ClassConfigProvider
from ui.datetimeutil import decode_date
from ui.icon import get_icon
from ui.widgets.grid import (
    EVT_GRID_COLUMN_RESIZED,
    EVT_GRID_MODEL_STATE_CHANGED,
    Column,
    FloatCellType,
    Model,
    StringCellType,
)
from ui.windows.main.identity import Identity

from ..grid.base import BaseEditor
from ..grid.choice_cell_type import ChoiceCellType
from ..grid.date_cell_type import DateCellType
from .grid_samples_preview import GridSamplesPreview
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
        self.columns: Dict[str, Column] = {}

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
            init_width=_width_("EndPosition"),
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
            o = PmProperty.get(Code=code)
            prop = PropertyColumn(code, Column(code, FloatCellType(), o.Name, o.Name, _width_(code), optional=True), o, method, equipment)
            self.props[code] = prop

    def remove_prop(self, code):
        if code in self.props:
            del self.props[code]

    def get_columns(self):
        return list(self.columns.values()) + list(map(lambda c: c.column, self.props.values()))

    def to_string_value(self, column_id, value):
        if column_id in self.columns:
            return self.columns[column_id].cell_type.to_string(value)
        if column_id in self.props:
            return self.props[column_id].column.cell_type.to_string(value)
        logging.warning("cannot find column with id %s in ColumnCollection." % column_id)
        return ""

    @db_session
    def load_properties(self):
        for p in select(o for o in PmSampleSetUsedProperties):
            self.append_prop(p.pm_property.Code, p.pm_method, p.pm_equipment)

    @db_session
    def update_orig_sample_set_variants(self):
        data = select(core for core in OrigSampleSet if len(core.discharge_series) == 0 and core.mine_object.Type == "FIELD").order_by(
            lambda x: x.Name
        )
        fields = []
        for o in data:
            n = o.Number.split("@").__getitem__(0)
            fields.append(n)
        self.columns["@orig_sample_set"].cell_type.set_choices(fields)

    def get_column(self, column_id):
        if column_id in self.columns:
            return self.columns[column_id]
        if column_id in self.props:
            return self.props[column_id].column
        return None


@dataclass
class Row:
    o: PMSample
    fields: Dict[str, str] = field(default_factory=lambda: {})
    changed_fields: Dict[str, str] = field(default_factory=lambda: {})


class GridSamplesModel(Model):
    @db_session
    def __init__(self, sample_set, config):
        self.sample_set = sample_set
        self._config_provider = config
        self.columns = ColumnCollection(config)
        self.columns.load_properties()
        self.rows = []
        self._deleted_rows = []
        self.load()

    @db_session
    def load(self):
        for o in select(o for o in PMSample if o.pm_sample_set == self.sample_set):
            fields = {
                "Number": self.columns.to_string_value("Number", o.Number),
                "@orig_sample_set": o.orig_sample_set.Number.split("@").__getitem__(0),
                "SetDate": self.columns.to_string_value("SetDate", decode_date(o.SetDate)),
                "StartPosition": self.columns.to_string_value("StartPosition", o.StartPosition),
                "EndPosition": self.columns.to_string_value("EndPosition", o.EndPosition),
                "BoxNumber": self.columns.to_string_value("BoxNumber", o.BoxNumber),
                "Length1": self.columns.to_string_value("Length1", o.Length1),
                "Length2": self.columns.to_string_value("Length2", o.Length2),
                "Height": self.columns.to_string_value("Height", o.Height),
                "MassAirDry": self.columns.to_string_value("MassAirDry", o.MassAirDry),
            }
            for used_prop in select(o for o in PmSampleSetUsedProperties):
                value = select(
                    v
                    for v in PmSamplePropertyValue
                    if v.pm_property == v.pm_property and v.pm_test_method == used_prop.pm_method or o in v.pm_samples
                ).first()
                if value != None:
                    fields[used_prop.pm_property.Code] = self.columns.to_string_value(used_prop.Code, value.Value)
                else:
                    fields[used_prop.pm_property.Code] = ""
            self.rows.append(Row(o, fields, {}))

    def get_columns(self):
        return self.columns.get_columns()

    @db_session
    def on_prop_add(self, prop, method, equipment):
        self.columns.append_prop(prop.Code, method, equipment)
        for row_index in range(self.get_rows_count()):
            if self.rows[row_index].o != None:
                value = select(
                    o for o in PmSamplePropertyValue if o.pm_property == prop and o.pm_test_method == method or self.rows[row_index].o in o.pm_samples
                ).first()
            else:
                value = None
            if value != None:
                self.rows[row_index].fields[prop.Code] = self.columns.to_string_value(prop.Code, value.Value)
            else:
                self.rows[row_index].fields[prop.Code] = ""

    def on_prop_remove(self, prop):
        self.columns.remove_prop(prop.Code)

    @db_session
    def _(self): ...

    def on_object_updated(self, o):
        if isinstance(o, OrigSampleSet):
            self.columns.update_orig_sample_set_variants()

    def get_value_at(self, col, row):
        _id = list(self.columns.get_columns()).__getitem__(col).id
        row = self.rows[row]
        return row.fields[_id] if _id not in row.changed_fields else row.changed_fields[_id]

    def set_value_at(self, col, row, value):
        _id = list(self.columns.get_columns()).__getitem__(col).id
        self.rows[row].changed_fields[_id] = value

    def get_rows_count(self):
        return len(self.rows)

    def total_rows(self):
        return len(self.rows)

    def insert_row(self, row):
        fields = {}
        for column in self.get_columns():
            fields[column.id] = ""
        self.rows.insert(row, Row(None, fields, {}))

    def restore_row(self, row, state):
        if state.o != None:
            self._deleted_rows.remove(state.o.RID)
        self.rows.insert(row, state)

    def delete_row(self, row: int):
        if self.rows[row].o != None:
            self._deleted_rows.append(self.rows[row].o.RID)
        self.rows.__delitem__(row)

    def get_row_state(self, row: int):
        return self.rows[row]

    def validate(self):
        errors = []
        for col in self.columns.get_columns():
            for row_index, row in enumerate(self.rows):
                if col.id in row.changed_fields:
                    value = row.changed_fields[col.id]
                else:
                    value = row.fields[col.id]
                if len(value) == 0:
                    if col.optional:
                        continue
                    else:
                        _msg = "Значение не должно быть пустым."
                        errors.append((col, row_index, _msg))
                if len(value) > 0 and not col.cell_type.test_repr(value):
                    _msg = 'Неподходящее значение для ячейки типа "%s"' % col.cell_type.get_type_descr()
                    errors.append((col, row_index, _msg))

        duplicates = {}
        for index, row in enumerate(self.rows):
            if "Number" in row.changed_fields:
                _v = row.changed_fields["Number"]
            else:
                _v = row.fields["Number"]
            if len(_v) == 0:
                continue
            if _v not in duplicates:
                duplicates[_v] = []
            duplicates[_v].append(index)
        col = self.columns.get_column("Number")
        for indexes in duplicates.values():
            if len(indexes) > 1:
                errors.append((col, indexes[0], "Номер должен быть уникален"))

        return errors


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
        )
        self.preview = GridSamplesPreview(self, sample_set)
        self.editor.Bind(EVT_GRID_COLUMN_RESIZED, self.on_editor_column_resized)
        self.editor.Bind(EVT_GRID_MODEL_STATE_CHANGED, self.on_model_state_changed)
        pubsub.pub.subscribe(self.on_object_updated, "object.added")
        pubsub.pub.subscribe(self.on_object_updated, "object.deleted")
        pubsub.pub.subscribe(self.on_object_updated, "object.updated")

    def on_editor_column_resized(self, event):
        if self._config_provider["column_width"] == None:
            self._config_provider["column_width"] = {}
        self._config_provider["column_width"][event.column.id] = event.size
        self._config_provider.flush()

    def on_model_state_changed(self, event):
        self.editor.validate(save_edit_control=False)

    def _on_open_props_editor(self, event):
        dlg = GridSamplePropertiesDialog(self, self.sample_set, self._on_prop_add, self._on_prop_remove)
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
        self.preview.Show()

    def on_deselect(self):
        self.toolbar.DeleteTool(ID_APPLEND_COLUMN)
        super().on_deselect()
        self.preview.Hide()

    def on_object_updated(self, o):
        self.editor._model.on_object_updated(o)
        self.editor.validate()
        self.editor._render()

    def on_after_close(self):
        print(self)
        pubsub.pub.unsubscribe(self.on_object_updated, "object.added")
        pubsub.pub.unsubscribe(self.on_object_updated, "object.deleted")
        pubsub.pub.unsubscribe(self.on_object_updated, "object.updated")
