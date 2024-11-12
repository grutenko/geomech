from dataclasses import dataclass, field
from typing import Dict

import pubsub
import pubsub.pub
import wx
from pony.orm import *

from database import *
from ui.class_config_provider import ClassConfigProvider
from ui.datetimeutil import decode_date, encode_date
from ui.widgets.grid.widget import *

from ..grid.base import BaseEditor
from ..grid.choice_cell_type import ChoiceCellType
from ..grid.date_cell_type import DateCellType

__CONFIG_VERSION__ = 1


@dataclass
class _Row:
    o: any
    fields: Dict = field(default_factory=lambda: {})
    changed_fields: Dict = field(default_factory=lambda: {})


class PmSamplesModel(Model):
    @db_session
    def __init__(self, o, config):
        self.o = o
        self._config_provider = config
        self._columns = {
            "Number": Column("Number", StringCellType(), "№*", "Номер образца*", init_width=self._get_column_width("Number")),
        }
        data = select(sample_set for sample_set in PMSampleSet if sample_set.pm_test_series == o).order_by(lambda x: x.Name)
        fields = []
        for o in data:
            fields.append(o.Name)
        self._columns["@pm_sample_set"] = Column(
            "@pm_sample_set", ChoiceCellType(fields), "Проба №*", "Проба №*", init_width=self._get_column_width("@pm_sample_set")
        )

        data = select(core for core in OrigSampleSet if len(core.discharge_series) == 0 and core.mine_object.Type == "FIELD").order_by(
            lambda x: x.Name
        )
        fields = []
        for o in data:
            n = o.Number.split("@").__getitem__(0)
            fields.append(n)
        self._columns["@orig_sample_set"] = Column(
            "@orig_sample_set", ChoiceCellType(fields), "Набор образцов*", "Набор образцов*", init_width=self._get_column_width("@orig_sample_set")
        )

        self._columns["SetDate"] = Column("SetDate", DateCellType(), "Дата отбора *", "Дата отбора *")
        self._columns["StartPosition"] = Column(
            "StartPosition", FloatCellType(), "Начальная\nпозиция, м*", "Начальная позиция, м*", init_width=self._get_column_width("StartPosition")
        )
        self._columns["EndPosition"] = Column(
            "EndPosition",
            FloatCellType(),
            "Конечная\nпозиция, м",
            "Конечная позиция, м",
            optional=True,
            init_width=self._get_column_width("@pm_sample_set"),
        )
        self._columns["BoxNumber"] = Column(
            "BoxNumber", StringCellType(), "Ящик №", "Ящик №", optional=True, init_width=self._get_column_width("BoxNumber")
        )
        self._columns["Length1"] = Column(
            "Length1",
            FloatCellType(),
            "Диаметр /\nсторона 1, см",
            "Диаметр / сторона 1, см",
            optional=True,
            init_width=self._get_column_width("Length1"),
        )
        self._columns["Length2"] = Column(
            "Length2", FloatCellType(), "Сторона 2, см", "Сторона 2, см", optional=True, init_width=self._get_column_width("Length2")
        )
        self._columns["Height"] = Column(
            "Height", FloatCellType(), "Высота, см", "Высота, см", optional=True, init_width=self._get_column_width("Height")
        )
        self._columns["MassAirDry"] = Column(
            "MassAirDry",
            FloatCellType(),
            "Масса в воздушно\nсухом состоянии, г",
            "Масса в воздушно-сухом состоянии",
            optional=True,
            init_width=self._get_column_width("MassAirDry"),
        )
        self._columns["MassNatMoist"] = Column(
            "MassNatMoist",
            FloatCellType(),
            "Масса в естественно\nвлажном состоянии, г",
            "Измерение: масса в естественно-влажном состоянии",
            optional=True,
            init_width=self._get_column_width("MassNatMoist"),
        )
        self._columns["MassWater"] = Column(
            "MassWater",
            FloatCellType(),
            "Масса в воде, г",
            "Измерение: масса в воде",
            optional=True,
            init_width=self._get_column_width("MassWater"),
        )
        self._columns["MassWaterSatur"] = Column(
            "MassWaterSatur",
            FloatCellType(),
            "Масса в водонасыщенном\nсостоянии, г",
            "Измерение: масса в водонасыщенном состоянии",
            optional=True,
            init_width=self._get_column_width("MassWaterSatur"),
        )
        self._columns["MassWaterSatWater"] = Column(
            "MassWaterSatWater",
            FloatCellType(),
            "Масса в водонасыщенном\nсостоянии\nв воде, г",
            "Измерение: масса в водонасыщенном состоянии в воде, г",
            optional=True,
            init_width=self._get_column_width("MassWaterSatWater"),
        )
        self._columns["MassDry"] = Column(
            "MassDry",
            FloatCellType(),
            "Масса в сухом\nсостоянии, г",
            "Измерение: Масса в сухом состоянии, г",
            optional=True,
            init_width=self._get_column_width("MassDry"),
        )
        self._columns["UniAxCompDistort"] = Column(
            "UniAxCompDistort",
            FloatCellType(),
            "Разрушающая нагрузка\nпри одноосном\nсжатии, кН",
            "Измерение: разрушающая нагрузка при одноосном сжатии, кН",
            optional=True,
            init_width=self._get_column_width("UniAxCompDistort"),
        )
        self._columns["UniAxTensDistort"] = Column(
            "UniAxTensDistort",
            FloatCellType(),
            "Разрушающая нагрузка\nпри одноосном\nрастяжении, кН",
            "Измерение: разрушающая нагрузка при одноосном растяжении, кН",
            optional=True,
            init_width=self._get_column_width("UniAxTensDistort"),
        )
        self._columns["ElasticityModulus"] = Column(
            "ElasticityModulus",
            FloatCellType(),
            "Модуль упругости",
            "Измерение: Модуль упругости",
            optional=True,
            init_width=self._get_column_width("ElasticityModulus"),
        )
        self._columns["DeclineModulus"] = Column(
            "ElasticityModulus",
            FloatCellType(),
            "Модуль спада",
            "Измерение: Модуль спада",
            optional=True,
            init_width=self._get_column_width("DeclineModulus"),
        )
        self._columns["PuassonCoeff"] = Column(
            "PuassonCoeff",
            FloatCellType(),
            "Пуассон",
            "Измерение: Коэффициент Пуассона",
            optional=True,
            init_width=self._get_column_width("PuassonCoeff"),
        )
        self._columns["DiffStrength"] = Column(
            "DiffStrength",
            FloatCellType(),
            "Дифф. прочность",
            "Измерение: дифференциальная прочность",
            optional=True,
            init_width=self._get_column_width("DiffStrength"),
        )
        self._rows = []
        self._deleted_objects = []
        self._load()

    @db_session
    def _load(self):
        data = select(o for o in PMSample if o.pm_sample_set.pm_test_series == self.o).order_by(lambda x: x.RID)
        _c = self._columns
        for o in data:
            _fields = {
                "Number": o.Number,
                "@pm_sample_set": o.pm_sample_set.Number,
                "@orig_sample_set": o.orig_sample_set.Number.split("@")[0],
                "SetDate": str(decode_date(o.SetDate)),
                "StartPosition": _c["StartPosition"].cell_type.to_string(o.StartPosition),
                "EndPosition": _c["EndPosition"].cell_type.to_string(o.EndPosition) if o.EndPosition != None else "",
                "BoxNumber": _c["BoxNumber"].cell_type.to_string(o.BoxNumber) if o.BoxNumber != None else "",
                "Length1": _c["Length1"].cell_type.to_string(o.Length1) if o.Length1 != None else "",
                "Length2": _c["Length2"].cell_type.to_string(o.Length2) if o.Length2 != None else "",
                "Height": _c["Height"].cell_type.to_string(o.Height) if o.Height != None else "",
                "MassAirDry": _c["MassAirDry"].cell_type.to_string(o.MassAirDry) if o.MassAirDry != None else "",
                "MassNatMoist": _c["MassNatMoist"].cell_type.to_string(o.MassNatMoist) if o.MassNatMoist != None else "",
                "MassWater": _c["MassWater"].cell_type.to_string(o.MassWater) if o.MassWater != None else "",
                "MassWaterSatur": _c["MassWaterSatur"].cell_type.to_string(o.MassWaterSatur) if o.MassWaterSatur != None else "",
                "MassWaterSatWater": _c["MassWaterSatWater"].cell_type.to_string(o.MassWaterSatWater) if o.MassWaterSatWater != None else "",
                "MassDry": _c["MassDry"].cell_type.to_string(o.MassDry) if o.MassDry != None else "",
                "UniAxCompDistort": _c["UniAxCompDistort"].cell_type.to_string(o.UniAxCompDistort) if o.UniAxCompDistort != None else "",
                "UniAxTensDistort": _c["UniAxTensDistort"].cell_type.to_string(o.UniAxTensDistort) if o.UniAxTensDistort != None else "",
                "ElasticityModulus": _c["ElasticityModulus"].cell_type.to_string(o.ElasticityModulus) if o.ElasticityModulus != None else "",
                "DeclineModulus": _c["DeclineModulus"].cell_type.to_string(o.DeclineModulus) if o.DeclineModulus != None else "",
                "PuassonCoeff": _c["PuassonCoeff"].cell_type.to_string(o.PuassonCoeff) if o.PuassonCoeff != None else "",
                "DiffStrength": _c["DiffStrength"].cell_type.to_string(o.DiffStrength) if o.DiffStrength != None else "",
            }

            self._rows.append(_Row(o, _fields))

    def _get_column_width(self, name):
        column_width = self._config_provider["column_width"]
        if column_width != None and name in column_width:
            return column_width[name]
        return -1

    @db_session
    def reload_orig_sample_sets(self):
        data = select(core for core in OrigSampleSet if len(core.discharge_series) == 0 and core.mine_object.Type == "FIELD").order_by(
            lambda x: x.Name
        )
        fields = []
        for o in data:
            n = o.Number.split("@").__getitem__(0)
            fields.append(n)
        self._columns["@orig_sample_set"].cell_type.set_choices(fields)

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
        _fields = {
            "Number": "",
            "@pm_sample_set": "",
            "@orig_sample_set": "",
            "SetDate": "",
            "StartPosition": "",
            "EndPosition": "",
            "BoxNumber": "",
            "Length1": "",
            "Length2": "",
            "Height": "",
            "MassAirDry": "",
            "MassNatMoist": "",
            "MassWater": "",
            "MassWaterSatur": "",
            "MassWaterSatWater": "",
            "MassDry": "",
            "UniAxCompDistort": "",
            "UniAxTensDistort": "",
            "ElasticityModulus": "",
            "DeclineModulus": "",
            "PuassonCoeff": "",
            "DiffStrength": "",
        }
        self._rows.insert(row, _Row(None, _fields))

    def delete_row(self, row):
        if self._rows[row].o != None:
            self._deleted_objects.append(self._rows[row].o.RID)
        self._rows.__delitem__(row)
        return True

    def restore_row(self, row, state):
        if state.o != None:
            self._deleted_rows.remove(state.o.RID)
        self._rows.insert(row, state)

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

        duplicates = {}
        for index, row in enumerate(self._rows):
            if "Number" in row.changed_fields:
                _v = row.changed_fields["Number"]
            else:
                _v = row.fields["Number"]
            if len(_v) == 0:
                continue
            if _v not in duplicates:
                duplicates[_v] = []
            duplicates[_v].append(index)
        col = self._columns["Number"]
        for indexes in duplicates.values():
            if len(indexes) > 1:
                errors.append((col, indexes[0], "Номер образца должен быть уникален"))

        return errors

    @db_session
    def save(self):
        if len(self.validate()) > 0:
            wx.MessageBox("В таблице обнаружены ошибки. Сохранение невозможно.", "Ошибка сохранения.", style=wx.OK | wx.ICON_ERROR)
            return False

        _created = {}
        _updated = {}
        _available_sample_sets = []
        _available_numbers = []

        for index, row in enumerate(self._rows):
            if len(row.changed_fields.keys()) == 0:
                # Просукаем строки которые не были изменены
                continue

            _in = {**row.fields, **row.changed_fields}
            _out = {}
            _c = self._columns
            _out["Number"] = _in["Number"].strip()
            _o = select(o for o in PMSample if o.Number == _out["Number"]).first()
            _op_create = _o == None
            _op_update = _o != None

            _out["pm_sample_set"] = select(o for o in PMSampleSet if o.Number == _in["@pm_sample_set"].strip() and o.pm_test_series == self.o).first()
            _available_sample_sets.append(_out["pm_sample_set"])
            _out["orig_sample_set"] = select(
                o for o in OrigSampleSet if _in["@orig_sample_set"] in o.Number and o.mine_object == _out["pm_sample_set"].mine_object
            ).first()
            _out["SetDate"] = encode_date(_in["SetDate"])
            _out["StartPosition"] = _c["StartPosition"].cell_type.from_string(_in["StartPosition"])
            if len(_in["EndPosition"]) > 0:
                _out["EndPosition"] = _c["EndPosition"].cell_type.from_string(_in["EndPosition"])
            else:
                if _op_update:
                    _out["EndPosition"] = None

            if len(_in["BoxNumber"]) > 0:
                _out["BoxNumber"] = _c["BoxNumber"].cell_type.from_string(_in["BoxNumber"])
            else:
                if _op_update:
                    _out["BoxNumber"] = None

            if len(_in["Length1"]) > 0:
                _out["Length1"] = _c["Length1"].cell_type.from_string(_in["Length1"])
            else:
                if _op_update:
                    _out["Length1"] = None

            if len(_in["Length2"]) > 0:
                _out["Length2"] = _c["Length2"].cell_type.from_string(_in["Length2"])
            else:
                if _op_update:
                    _out["Length2"] = None

            if len(_in["Height"]) > 0:
                _out["Height"] = _c["Height"].cell_type.from_string(_in["Height"])
            else:
                if _op_update:
                    _out["Height"] = None

            if len(_in["MassAirDry"]) > 0:
                _out["MassAirDry"] = _c["MassAirDry"].cell_type.from_string(_in["MassAirDry"])
            else:
                if _op_update:
                    _out["MassAirDry"] = None

            if len(_in["MassNatMoist"]) > 0:
                _out["MassNatMoist"] = _c["MassNatMoist"].cell_type.from_string(_in["MassNatMoist"])
            else:
                if _op_update:
                    _out["MassNatMoist"] = None

            if len(_in["MassWater"]) > 0:
                _out["MassWater"] = _c["MassWater"].cell_type.from_string(_in["MassWater"])
            else:
                if _op_update:
                    _out["MassWater"] = None

            if len(_in["MassWaterSatur"]) > 0:
                _out["MassWaterSatur"] = _c["MassWaterSatur"].cell_type.from_string(_in["MassWaterSatur"])
            else:
                if _op_update:
                    _out["MassWaterSatur"] = None

            if len(_in["MassWaterSatWater"]) > 0:
                _out["MassWaterSatWater"] = _c["MassWaterSatWater"].cell_type.from_string(_in["MassWaterSatWater"])
            else:
                if _op_update:
                    _out["MassWaterSatWater"] = None

            if len(_in["MassDry"]) > 0:
                _out["MassDry"] = _c["MassDry"].cell_type.from_string(_in["MassDry"])
            else:
                if _op_update:
                    _out["MassDry"] = None

            if len(_in["UniAxCompDistort"]) > 0:
                _out["UniAxCompDistort"] = _c["UniAxCompDistort"].cell_type.from_string(_in["UniAxCompDistort"])
            else:
                if _op_update:
                    _out["UniAxCompDistort"] = None

            if len(_in["UniAxTensDistort"]) > 0:
                _out["UniAxTensDistort"] = _c["UniAxTensDistort"].cell_type.from_string(_in["UniAxTensDistort"])
            else:
                if _op_update:
                    _out["UniAxTensDistort"] = None

            if len(_in["ElasticityModulus"]) > 0:
                _out["ElasticityModulus"] = _c["ElasticityModulus"].cell_type.from_string(_in["ElasticityModulus"])
            else:
                if _op_update:
                    _out["ElasticityModulus"] = None

            if len(_in["DeclineModulus"]) > 0:
                _out["DeclineModulus"] = _c["DeclineModulus"].cell_type.from_string(_in["DeclineModulus"])
            else:
                if _op_update:
                    _out["DeclineModulus"] = None

            if len(_in["PuassonCoeff"]) > 0:
                _out["PuassonCoeff"] = _c["PuassonCoeff"].cell_type.from_string(_in["PuassonCoeff"])
            else:
                if _op_update:
                    _out["PuassonCoeff"] = None

            if len(_in["DiffStrength"]) > 0:
                _out["DiffStrength"] = _c["DiffStrength"].cell_type.from_string(_in["DiffStrength"])
            else:
                if _op_update:
                    _out["DiffStrength"] = None

            _available_numbers.append(_out["Number"])

            if _o != None:
                _o.set(**_out)
                _updated[index] = _o
            else:
                _created[index] = PMSample(**_out)

        _objects_to_delete = select(o for o in PMSample if o.Number not in _available_numbers and o.pm_sample_set.pm_test_series == self.o)
        if len(_objects_to_delete) > 0:
            ret = wx.MessageBox(
                "Из базы данных будут удалены следующие образцы: " + ", ".join(map(lambda x: x.Number, _objects_to_delete)) + ".\nПродолжить?",
                "Подтвердите удаление",
                style=wx.YES | wx.NO | wx.CANCEL | wx.NO_DEFAULT | wx.ICON_INFORMATION,
            )
            if ret == wx.YES:
                for o in _objects_to_delete:
                    o.delete()

        commit()

        for row_index, entity in _created.items():
            self._rows[row_index].o = entity
            self._rows[row_index].fields = {**self._rows[row_index].fields, **self._rows[row_index].changed_fields}
            self._rows[row_index].changed_fields = {}
        for row_index, entity in _updated.items():
            self._rows[row_index].fields = {**self._rows[row_index].fields, **self._rows[row_index].changed_fields}
            self._rows[row_index].changed_fields = {}

        self._deleted_objects = []
        pubsub.pub.sendMessage("entity.mass_changed", entity_class=PMSample, bounds=self.o)
        return True


class PmSampleEditor(BaseEditor):
    @db_session
    def __init__(self, parent, identity, menubar, toolbar, statusbar):
        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)
        self._config_provider.flush()
        self.o = PMTestSeries[identity.o.RID]
        super().__init__(
            parent,
            "Образцы: " + self.o.Name,
            identity,
            PmSamplesModel(identity.rel_data_o, self._config_provider),
            menubar,
            toolbar,
            statusbar,
            header_height=50,
            freezed_cols=1,
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

    def _on_object_added(self, o, topic=None):
        if isinstance(o, OrigSampleSet):
            self._on_orig_sample_set_changed()

    def _on_object_deleted(self, o, topic=None):
        if isinstance(o, BoreHole):
            self._on_bore_holes_changed()

    def _on_orig_sample_set_changed(self):
        self.editor._model.reload_orig_sample_sets()
        self.editor._render()
        self.editor.validate()

    def on_after_close(self):
        pubsub.pub.unsubscribe(self._on_object_added, "object.added")
        pubsub.pub.unsubscribe(self._on_object_deleted, "object.deleted")
