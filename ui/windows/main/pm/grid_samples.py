from dataclasses import dataclass, field
from typing import Dict

import pubsub
import wx
from pony.orm import *

from database import *
from ui.class_config_provider import ClassConfigProvider
from ui.widgets.grid.widget import *

from ..grid.base import BaseEditor
from ..grid.choice_cell_type import ChoiceCellType
from ..grid.date_cell_type import DateCellType

__CONFIG_VERSION__ = 1


@dataclass
class _Row:
    o: any
    have_childs: bool = False
    fields: Dict = field(default_factory=lambda: {})
    changed_fields: Dict = field(default_factory=lambda: {})


class PmSamplesModel(Model):
    @db_session
    def __init__(self, o, config):
        self.o = o
        self._columns = {
            "Number": Column("Number", StringCellType(), "№", "Номер образца", init_width=70),
        }
        data = select(sample_set for sample_set in PMSampleSet if sample_set.pm_test_series == o).order_by(lambda x: x.Name)
        fields = []
        for o in data:
            fields.append(o.Name)
        self._columns["@pm_sample_set"] = Column("@pm_sample_set", ChoiceCellType(fields), "Проба №", "Проба №")

        data = select(
            core
            for core in BoreHole
            if len(core.orig_sample_sets) > 0
            and len(core.orig_sample_sets.discharge_series) == 0
            and core.mine_object.Type == "FIELD"
            and core.station == None
        ).order_by(lambda x: x.Name)
        fields = []
        for o in data:
            n = o.Number.split("@").__getitem__(0)
            fields.append(n)
        self._columns["@bore_hole"] = Column("@bore_hole", ChoiceCellType(fields), "Скважина №", "Скважина №")

        self._columns["SetDate"] = Column("SetDate", DateCellType(), "Дата отбора *", "Дата отбора *")
        self._columns["StartPosition"] = Column("StartPosition", FloatCellType(), "Начальная\nпозиция *", "Начальная позиция *")
        self._columns["EndPosition"] = Column("EndPosition", FloatCellType(), "Конечная\nпозиция", "Конечная позиция", optional=True)
        self._columns["BoxNumber"] = Column("BoxNumber", StringCellType(), "Ящик №", "Ящик №", optional=True)
        self._columns["Length1"] = Column("Length1", FloatCellType(), "Диаметр /\nсторона 1", "Диаметр / сторона 1", optional=True)
        self._columns["Length1"] = Column("Length1", FloatCellType(), "Сторона 2", "Сторона 2", optional=True)
        self._columns["Height"] = Column("Height", FloatCellType(), "Высота", "Высота", optional=True)

        self._rows = []
        self._deleted_objects = []

    @db_session
    def reload_bore_holes(self):
        data = select(
            core
            for core in BoreHole
            if len(core.orig_sample_sets) > 0
            and len(core.orig_sample_sets.discharge_series) == 0
            and core.mine_object.Type == "FIELD"
            and core.station == None
        ).order_by(lambda x: x.Name)
        fields = []
        for o in data:
            n = o.Number.split("@").__getitem__(0)
            fields.append(n)
        self._columns["@bore_hole"].cell_type.set_choices(fields)

    @db_session
    def reload_pm_sample_sets(self):
        data = select(sample_set for sample_set in PMSampleSet if sample_set.pm_test_series == self.o).order_by(lambda x: x.Name)
        fields = []
        for o in data:
            n = o.Number.split("@").__getitem__(0)
            fields.append(n)
        self._columns["@pm_sample_set"].cell_type.set_choices(fields)

    def get_columns(self):
        return list(self._columns.values())

    def insert_row(self, row):
        choices = self._columns["@pm_sample_set"].cell_type.choices
        if len(choices) > 0:
            sample_set = choices[0]
        else:
            sample_set = ""
        _fields = {
            "Number": "",
            "@pm_sample_set": sample_set,
            "@bore_hole": "",
            "SetDate": "",
            "StartPosition": "1",
            "EndPosition": "",
            "BoxNumber": "",
            "Length1": "",
            "Length2": "",
            "Height": "",
        }
        self._rows.insert(row, _Row(None, False, _fields))

    def delete_row(self, row):
        del self._rows[row]
        return True

    def get_row_state(self, row):
        return self._rows[row]

    def total_rows(self):
        return len(self._rows)

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

    def have_changes(self):
        for row in self._rows:
            if row.changed_fields or row.o == None:
                return True
        return len(self._deleted_objects) > 0

    def validate(self):
        errors = []
        for col in self._columns.values():
            for row_index, row in enumerate(self._rows):
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

        return errors


class PmSampleEditor(BaseEditor):
    @db_session
    def __init__(self, parent, identity, menubar, toolbar, statusbar):
        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)
        self._config_provider.flush()
        self.o = PMTestSeries[identity.o.RID]
        print(menubar, toolbar, statusbar)
        super().__init__(
            parent,
            "Образцы: " + self.o.Name,
            identity,
            PmSamplesModel(identity.rel_data_o, self._config_provider),
            menubar,
            toolbar,
            statusbar,
            header_height=30,
        )
        self.editor.show_errors_view()
        self.editor.Bind(EVT_GRID_COLUMN_RESIZED, self._on_editor_column_resized)
        self.editor.Bind(EVT_GRID_MODEL_STATE_CHANGED, self._on_model_state_changed)

        pubsub.pub.subscribe(self._on_object_added, "object.added")
        pubsub.pub.subscribe(self._on_object_deleted, "object.deleted")

    def _on_model_state_changed(self, event):
        self.editor.validate(save_edit_control=False)

    def _on_editor_column_resized(self, event):
        if self._config_provider["column_width"] == None:
            self._config_provider["column_width"] = {}
        self._config_provider["column_width"][event.column.id] = event.size
        self._config_provider.flush()

    def _on_object_added(self, o):
        if isinstance(o, BoreHole):
            self._on_bore_holes_changed()

    def _on_object_deleted(self, o, topic=None):
        if isinstance(o, BoreHole):
            self._on_bore_holes_changed()

    def _on_bore_holes_changed(self):
        self.editor._model.reload_bore_holes()
        self.editor._render()
        self.editor.validate()

    def on_after_close(self):
        pubsub.pub.unsubscribe(self._on_object_added, "object.added")
