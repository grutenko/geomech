from dataclasses import dataclass, field
from typing import Dict

import wx
from pony.orm import *
from pubsub import pub

from database import PmProperty, PMSample, PmTestEquipment, PmTestMethod
from ui.widgets.grid.widget import Column, FloatCellType, Model

from ..grid.base import BaseEditor
from ..grid.choice_cell_type import ChoiceCellType


@dataclass
class _Row:
    o: any
    fields: Dict = field(default_factory=lambda: {})
    changed_fields: Dict = field(default_factory=lambda: {})


class _Model(Model):
    @db_session
    def __init__(self, o):
        super().__init__()
        self.o = o
        self._columns = {}
        _samples = []
        for o in select(o for o in PMSample if o.pm_sample_set.pm_test_series == self.o):
            _samples.append(o.Number)
        self._columns["@sample"] = Column("@sample", ChoiceCellType(_samples), "Образец № *", "Образец №", init_width=100)
        _property = []
        for o in select(o for o in PmProperty):
            _property.append(o.Name)
        self._columns["@property"] = Column("@property", ChoiceCellType(_property), "Свойство *", "Свойство", init_width=250)
        _methods = []
        for o in select(o for o in PmTestMethod):
            _methods.append(o.Name)
        self._columns["@method"] = Column("@method", ChoiceCellType(_methods), "Метод *", "Метод испытаний", init_width=250)
        _equipment = []
        for o in select(o for o in PmTestEquipment):
            _equipment.append(o.Name)
        self._columns["@equipment"] = Column("@equipment", ChoiceCellType(_equipment), "Оборудование *", "Оборудование", init_width=250)
        self._columns["@value"] = Column("@value", FloatCellType(), "Значение *", "Значение")

        self._deleted_objects = []
        self._rows = []

    @db_session
    def reload_samples(self):
        data = select(o for o in PMSample if o.pm_sample_set.pm_test_series == self.o)
        fields = []
        for o in data:
            fields.append(o.Number)
        self._columns["@sample"].cell_type.set_choices(fields)

    @db_session
    def reload_properties(self):
        data = select(o for o in PmProperty)
        _property = []
        for o in select(o for o in PmProperty):
            _property.append(o.Name)
        self._columns["@property"].cell_type.set_choices(_property)

    @db_session
    def reload_methods(self):
        _methods = []
        for o in select(o for o in PmTestMethod):
            _methods.append(o.Name)
        self._columns["@method"].cell_type.set_choices(_methods)

    @db_session
    def reload_equipment(self):
        _equipment = []
        for o in select(o for o in PmTestEquipment):
            _equipment.append(o.Name)
        self._columns["@equipment"].cell_type.set_choices(_equipment)

    def insert_row(self, row):
        _fields = {
            "@sample": "",
            "@method": "",
            "@equipment": "",
            "@property": "",
            "@value": "",
        }
        self._rows.insert(row, _Row(None, _fields))

    def delete_row(self, row):
        if self._rows[row].o != None:
            self._deleted_objects.append(self._rows[row].o.RID)
        self._rows.__delitem__(row)
        return True

    def restore_row(self, row, state):
        if state.o != None:
            for index, o in enumerate(self._deleted_objects):
                if o.RID == state.o:
                    del self._deleted_objects[index]
                    break
        self._rows.insert(row, state)

    def get_columns(self):
        return list(self._columns.values())

    def total_rows(self):
        return len(self._rows)

    def get_row_state(self, row):
        return self._rows[row]

    def get_value_at(self, col, row):
        col_id = list(self._columns.keys()).__getitem__(col)
        if col_id not in self._rows[row].changed_fields:
            return self._rows[row].fields[col_id]
        else:
            return self._rows[row].changed_fields[col_id]

    def set_value_at(self, col, row, value):
        col_id = list(self._columns.keys())[col]
        if col_id in self._rows[row].changed_fields and self._rows[row].fields[col_id] == value:
            del self._rows[row].changed_fields[col_id]
        elif self.get_value_at(col, row) != value:
            self._rows[row].changed_fields[col_id] = value


class GridSampleTests(BaseEditor):
    def __init__(self, parent, _id, series, menubar, toolbar, statusbar):
        super().__init__(parent, "Испытания: " + series.Name, _id, _Model(_id.rel_data_o), menubar, toolbar, statusbar, header_height=25)
        pub.subscribe(self._on_entity_mass_changed, "entity.mass_changed")
        pub.subscribe(self._on_entity_changed, "object")

    def _on_entity_changed(self, o, topic=None):
        if isinstance(o, PmTestMethod):
            self.editor._model.reload_methods()
        elif isinstance(o, PmProperty):
            self.editor._model.reload_properties()
        elif isinstance(o, PmTestEquipment):
            self.editor._model.reload_equipment()
        else:
            return
        self.editor._render()

    def _on_entity_mass_changed(self, entity_class, bounds):
        if bounds.__class__ == self.o.__class__ and bounds.RID == self.o.RID and entity_class == PMSample:
            self.editor._model.reload_samples()
            self.editor._render()

    def on_after_close(self):
        pub.unsubscribe(self._on_entity_mass_changed, "entity.mass_changed")
        pub.unsubscribe(self._on_entity_changed, "object")
