from dataclasses import dataclass, field
from typing import Dict

import pubsub
import pubsub.pub
import wx
from pony.orm import *

from database import MineObject, Petrotype, PetrotypeStruct, PMSampleSet, PMTestSeries
from ui.class_config_provider import ClassConfigProvider
from ui.datetimeutil import *
from ui.widgets.grid import (
    EVT_GRID_COLUMN_RESIZED,
    EVT_GRID_MODEL_STATE_CHANGED,
    Column,
    Model,
    StringCellType,
)

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


class PmSampleSetModel(Model):
    @db_session
    def __init__(self, o, config):
        self.o = o
        self._config_provider = config
        self._columns = {
            "Name": Column("Name", StringCellType(), "Название *", "(Обязат.) Название пробы", init_width=self._get_column_width("Name")),
            "Comment": Column(
                "Comment", StringCellType(multiline=True), "Комментарий", "Комментарий", init_width=self._get_column_width("Comment"), optional=True
            ),
        }
        data = select(o for o in MineObject if o.Type == "FIELD").order_by(lambda x: desc(x.RID))
        fields = []
        for o in data:
            fields.append(o.Name)
        self._columns["@mine_object"] = Column(
            "@mine_object", ChoiceCellType(fields), "Месторождение *", "(Обязат.) Месторождение", init_width=self._get_column_width("@mine_object")
        )
        data = select(o for o in Petrotype).order_by(lambda x: x.Name)
        fields = []
        for o in data:
            fields.append(o.Name)
        self._columns["@petrotype"] = Column(
            "@petrotype",
            ChoiceCellType(fields, allow_other=True),
            "Петротип *",
            "(Обязат.) Петротип",
            init_width=self._get_column_width("@petrotype"),
        )
        self._columns["@petrotype_struct"] = Column(
            "@petrotype_struct",
            StringCellType(),
            "Описание структуры\nпетротипа",
            "Описание структуры петротипа",
            init_width=self._get_column_width("@petrotype_struct"),
            optional=True,
        )
        self._columns["SetDate"] = Column("SetDate", DateCellType(), "Дата отбора", "Дата отбора", self._get_column_width("SetDate"), True)
        self._columns["TestDate"] = Column("TestDate", DateCellType(), "Дата испытания", "Дата испытания", self._get_column_width("TestDate"), True)
        self._columns["CrackDescr"] = Column(
            "CrackDescr", StringCellType(multiline=True), "Описание трещин", "Описание трещин", self._get_column_width("CrackDescr"), True
        )

        self._deleted_objects = []
        self._rows = []

        self._load()

    def _get_column_width(self, name):
        column_width = self._config_provider["column_width"]
        if column_width != None and name in column_width:
            return column_width[name]
        return -1

    @db_session
    def _load(self):
        data = select(o for o in PMSampleSet if o.pm_test_series == self.o).order_by(lambda x: x.RID)
        for o in data:
            _fields = {
                "Name": o.Name,
                "Comment": o.Comment if o.Comment != None else "",
                "@mine_object": o.mine_object.Name,
                "@petrotype": o.petrotype_struct.petrotype.Name,
                "@petrotype_struct": o.petrotype_struct.Name,
                "CrackDescr": o.CrackDescr if o.CrackDescr != None else "",
                "SetDate": "",
                "TestDate": "",
            }

            if o.SetDate != None:
                _fields["SetDate"] = decode_date(o.SetDate).strftime("%d.%m.%Y")
            if o.TestDate != None:
                _fields["TestDate"] = decode_date(o.TestDate).strftime("%d.%m.%Y")

            _have_childs = len(o.pm_samples) > 0
            self._rows.append(_Row(o, _have_childs, _fields))

    @db_session
    def reload_mine_objects(self):
        data = select(o for o in MineObject if o.Type == "FIELD").order_by(lambda x: desc(x.RID))
        fields = []
        for o in data:
            fields.append(o.Name)
        self._columns["@mine_object"].cell_type.set_choices(fields)

    def get_columns(self):
        return list(self._columns.values())

    def insert_row(self, row):
        choices = self._columns["@mine_object"].cell_type.choices
        if len(choices) > 0:
            mine_object = choices[0]
        else:
            mine_object = ""
        _fields = {
            "Name": "",
            "Comment": "",
            "@mine_object": mine_object,
            "@petrotype": "",
            "@petrotype_struct": "",
            "SetDate": "",
            "TestDate": "",
            "CrackDescr": "",
        }
        self._rows.insert(row, _Row(None, False, _fields))

    def delete_row(self, row):
        if self._rows[row].o != None and self._rows[row].have_childs:
            wx.MessageBox("Удаление этой пробы запрещено. Проба: " % (row + 1), "Ошибка удаления")
            return False
        if self._rows[row].o != None:
            self._deleted_objects.append(self._rows[row].o)
        del self._rows[row]
        return True

    def get_row_state(self, row):
        return self._rows[row]

    def restore_row(self, row, state):
        if state.o != None:
            for index, o in enumerate(self._deleted_objects):
                if o.RID == state.o:
                    del self._deleted_objects[index]
                    break
        self._rows.insert(row, state)

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
        if self._rows[row].o != None and self._rows[row].have_childs and col_id == "Name":
            wx.MessageBox("Нельзя менять номер пробы если к нему есть связаные данные.", "Ошибка записи")
            return False
        if self.get_value_at(col, row) != value:
            self._rows[row].changed_fields[col_id] = value

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

    def have_changes(self):
        for row in self._rows:
            if row.changed_fields or row.o == None:
                return True
        return len(self._deleted_objects) > 0

    @db_session
    def save(self):
        if len(self.validate()) > 0:
            wx.MessageBox("В таблице обнаружены ошибки. Сохранение невозможно.", "Ошибка сохранения.", style=wx.OK | wx.ICON_ERROR)
            return False

        _created = {}
        _updated = {}
        _petrotypes = {}
        for o in self._deleted_objects:
            PMSampleSet[o.RID].delete()

        for index, row in enumerate(self._rows):
            _fields = {**row.fields, **row.changed_fields}
            _out = {}

            _p_name = _fields["@petrotype"].title()
            if len(_fields["@petrotype_struct"]) == 0:
                _fields["@petrotype_struct"] = "-"
            _p_struct_name = _fields["@petrotype_struct"]

            _p = None
            _p_struct = None
            if _p_name in _petrotypes:
                _p = _petrotypes[_p_name][0]
            else:
                _p = select(o for o in Petrotype if o.Name.upper() == _p_name.upper()).first()
                if _p == None:
                    _p = Petrotype(Name=_p_name)
                _petrotypes[_p_name] = (_p, {})

            if _p_struct_name in _petrotypes[_p_name][1]:
                _p_struct = _petrotypes[_p_name][1][_p_struct_name]
            else:
                _p_struct = select(o for o in PetrotypeStruct if o.petrotype == _p and _p_struct_name.upper() == o.Name.upper()).first()
                if _p_struct == None:
                    _p_struct = PetrotypeStruct(Name=_p_struct_name, petrotype=_p)
                _petrotypes[_p_name][1][_p_struct_name] = _p_struct

            _out["petrotype_struct"] = _p_struct
            mine_object = select(o for o in MineObject if o.Name == _fields["@mine_object"]).first()
            _out["mine_object"] = mine_object
            _out["pm_test_series"] = PMTestSeries[self.o.RID]
            _out["Number"] = _fields["Name"]
            _out["Name"] = _fields["Name"]

            if len(_fields["Comment"]) > 0:
                _out["Comment"] = _fields["Comment"]
            if len(_fields["SetDate"]) > 0:
                _out["SetDate"] = encode_date(_fields["SetDate"])
            else:
                _out["SetDate"] = None
            if len(_fields["TestDate"]) > 0:
                _out["TestDate"] = encode_date(_fields["TestDate"])
            else:
                _out["TestDate"] = None
            if len(_fields["CrackDescr"]) > 0:
                _out["CrackDescr"] = encode_date(_fields["CrackDescr"])
            else:
                _out["CrackDescr"] = ""
            _out["RealDetails"] = True

            if row.o == None:
                _created[index] = PMSampleSet(**_out)
            else:
                o = PMSampleSet[row.o.RID]
                o.set(**_out)
                _updated[index] = o

        commit()

        for row_index, entity in _created.items():
            self._rows[row_index].o = entity
            self._rows[row_index].fields = {**self._rows[row_index].fields, **self._rows[row_index].changed_fields}
            self._rows[row_index].changed_fields = {}
        for row_index, entity in _updated.items():
            self._rows[row_index].fields = {**self._rows[row_index].fields, **self._rows[row_index].changed_fields}
            self._rows[row_index].changed_fields = {}

        self._deleted_objects = []

        return True


class PmSampleSetsEditor(BaseEditor):
    @db_session
    def __init__(self, parent, identity, menubar, toolbar, statusbar):
        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)
        self._config_provider.flush()
        self.o = PMTestSeries[identity.o.RID]
        super().__init__(
            parent,
            "Пробы: " + self.o.Name,
            identity,
            PmSampleSetModel(identity.rel_data_o, self._config_provider),
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
        if isinstance(o, MineObject) and o.Type == "FIELD":
            self._on_mine_objects_changed()

    def _on_object_deleted(self, o, topic=None):
        if isinstance(o, MineObject) and o.Type == "FIELD":
            self._on_mine_objects_changed()

    def _on_mine_objects_changed(self):
        self.editor._model.reload_mine_objects()
        self.editor._render()
        self.editor.validate()

    def on_after_close(self):
        pubsub.pub.unsubscribe(self._on_object_added, "object.added")
