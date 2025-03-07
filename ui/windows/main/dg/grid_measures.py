from dataclasses import dataclass, field
from typing import Dict, Iterable

import wx
import wx.grid
from pony.orm import *

from database import DischargeMeasurement, OrigSampleSet
from ui.class_config_provider import ClassConfigProvider
from ui.widgets.grid import *
from ui.widgets.grid.widget import Column

from ..grid.base import BaseEditor

__CONFIG_VERSION__ = 1

import re

from wx.grid import (
    GridCellAutoWrapStringEditor,
    GridCellEditor,
    GridCellRenderer,
    GridCellStringRenderer,
)


@dataclass
class _Row:
    o: any
    fields: Dict = field(default_factory=lambda: {})
    changed_fields: Dict = field(default_factory=lambda: {})


class VecCellType(CellType):
    def __init__(self, item_type: CellType, min_count=0, max_count=-1):
        self._item_type = item_type

    def get_type_name(self) -> str:
        return "vec<%s>" % self._item_type.get_type_name()

    def get_type_descr(self) -> str:
        return "[Список] %s" % self._item_type.get_type_descr()

    def test_repr(self, value) -> bool:
        for item in re.split("[,;]\s*", value.strip()):
            if self._item_type.test_repr(item) == False:
                return False
        return True

    def to_string(self, value) -> str:
        if value == None:
            return ""
        return "; ".join(map(lambda x: self._item_type.to_string(x), value))

    def from_string(self, value: str):
        value = value.strip()
        if value == None or value.strip() == "":
            return []
        values = []
        for item in re.split("[,;]\s*", value.strip()):
            values.append(self._item_type.from_string(item))
        return values

    def get_grid_renderer(self) -> GridCellRenderer:
        return GridCellStringRenderer()

    def get_grid_editor(self) -> GridCellEditor:
        return GridCellAutoWrapStringEditor()

    def __eq__(self, o):
        return isinstance(o, VecCellType)


class DMModel(Model):
    def __init__(self, core, config_provider) -> None:
        super().__init__()
        self._core = core
        self._config_provider = config_provider
        self._rows = []
        self._columns = self._build_columns()
        self._changed_columns = 0
        self._deleted_rows = []
        self.load()

    def _prepare_o(self, o):
        r = _Row(o)
        fields = {
            "SampleNumber": str(o.SampleNumber),
            "Diameter": str(o.Diameter),
            "Length": str(o.Length),
            "Weight": str(int(o.Weight)),
            "CoreDepth": str(o.CoreDepth),
        }
        columns = self._columns
        e = []
        e.append(str(int(o.E1)))
        e.append(str(int(o.E2)))
        e.append(str(int(o.E3)))
        e.append(str(int(o.E4)))
        fields["E"] = "; ".join(e)
        fields["Rotate"] = str(o.Rotate)
        fields["PartNumber"] = o.PartNumber
        fields["RTens"] = str(o.RTens)
        fields["Sensitivity"] = str(o.Sensitivity)
        fields["RockType"] = str(o.RockType) if o.RockType != None else ""
        tp1 = []
        if o.TP1_1 != None:
            tp1.append(str(float(o.TP1_1)))
        if o.TP1_2 != None:
            tp1.append(str(float(o.TP1_2)))
        fields["TP1"] = "; ".join(tp1)
        tp2 = []
        if o.TP2_1 != None:
            tp2.append(str(float(o.TP2_1)))
        if o.TP2_2 != None:
            tp2.append(str(float(o.TP2_2)))
        fields["TP2"] = "; ".join(tp2)
        tr = []
        if o.TR_1 != None:
            tr.append(str(float(o.TR_1)))
        if o.TR_2 != None:
            tr.append(str(float(o.TR_2)))
        fields["TR"] = "; ".join(tr)
        ts = []
        if o.TS_1 != None:
            ts.append(str(float(o.TS_1)))
        if o.TS_2 != None:
            ts.append(str(float(o.TS_2)))
        fields["TS"] = "; ".join(ts)
        fields["PWSpeed"] = str(int(o.PWSpeed)) if o.PWSpeed != None else ""
        fields["RWSpeed"] = str(int(o.RWSpeed)) if o.RWSpeed != None else ""
        fields["SWSpeed"] = str(int(o.SWSpeed)) if o.SWSpeed != None else ""
        fields["PuassonStatic"] = str(o.PuassonStatic) if o.PuassonStatic != None else ""
        fields["YungStatic"] = str(o.YungStatic) if o.YungStatic != None else ""
        r.fields = fields
        return r

    @db_session
    def load(self):
        self._rows = []
        dm = select(o for o in DischargeMeasurement if o.orig_sample_set == self._core).order_by(lambda p: int(p.DschNumber))
        o: DischargeMeasurement
        for o in dm:
            self._rows.append(self._prepare_o(o))

    def _get_column_width(self, name):
        column_width = self._config_provider["column_width"]
        if column_width != None and name in column_width:
            return column_width[name]
        return -1

    def _build_columns(self):
        return {
            "SampleNumber": Column(
                "SampleNumber",
                StringCellType(),
                "* № Образца",
                "Регистрационный номер образца керна",
                self._get_column_width("SampleNumber"),
            ),
            "Diameter": Column(
                "Diameter",
                FloatCellType(prec=1),
                "* Диаметр\n(мм)",
                "Диаметр образца керна",
                self._get_column_width("Diameter"),
            ),
            "Length": Column(
                "Length",
                FloatCellType(prec=1),
                "* Длина\n(см)",
                "Длина образца керна",
                self._get_column_width("Length"),
            ),
            "Weight": Column(
                "Weight",
                NumberCellType(),
                "* Вес\n(г)",
                "Вес образца\nкерна",
                self._get_column_width("Weight"),
            ),
            "CoreDepth": Column(
                "CoreDepth",
                FloatCellType(),
                "* Глубина\nвзятия (м)",
                "Глубина взятия образца керна",
                self._get_column_width("CoreDepth"),
            ),
            "RockType": Column(
                "RockType",
                StringCellType(),
                "* Тип породы",
                "Тип породы",
                self._get_column_width("RockType"),
            ),
            "E": Column(
                "E",
                VecCellType(NumberCellType(), min_count=1, max_count=4),
                "* Относит.\nдеформ. (усл. ед.)",
                "Относительная деформация образца (усл. ед.)",
                self._get_column_width("E"),
            ),
            "Rotate": Column(
                "Rotate",
                FloatCellType(),
                "* Угол корр.\nнапряж.\n(град.)",
                "Угол коррекции направления напряжений",
                self._get_column_width("Rotate"),
            ),
            "PartNumber": Column(
                "PartNumber",
                StringCellType(),
                "* № партии\nтензодат",
                "Номер партии тензодатчиков",
                self._get_column_width("PartNumber"),
            ),
            "RTens": Column(
                "RTens",
                FloatCellType(prec=1),
                "* Сопрот.\nТезодат. (Ом)",
                "Сопротивление тензодатчиков",
                self._get_column_width("RTens"),
            ),
            "Sensitivity": Column(
                "Sensitivity",
                FloatCellType(),
                "* Чувств.\nТезодат.",
                "Коэффициент чувствительности тензодатчиков",
                self._get_column_width("Sensitivity"),
            ),
            "TP1": Column(
                "TP1",
                VecCellType(FloatCellType(prec=1), 0, 2),
                "Время\nпродоль.\n(мс)",
                "Замер времени прохождения продольных волн (ультразвуковое профилирование или др.)",
                self._get_column_width("TP1"),
                optional=True,
            ),
            "TP2": Column(
                "TP2",
                VecCellType(FloatCellType(prec=1), 0, 2),
                "Время продоль.\n(торц.) (мс)",
                "Замер времени прохождения продольных волн (торц.)",
                self._get_column_width("TP2"),
                optional=True,
            ),
            "PWSpeed": Column(
                "PWSpeed",
                NumberCellType(),
                "Скорость\nпродоль.\n(м/с)",
                "Коэффициент чувствительности тензодатчиков",
                self._get_column_width("PWSpeed"),
                optional=True,
            ),
            "TR": Column(
                "TR",
                VecCellType(FloatCellType(prec=2), 0, 2),
                "Время\nповерхност.\n(мс)",
                "Замер времени прохождения поверхностных волн",
                self._get_column_width("TR"),
                optional=True,
            ),
            "RWSpeed": Column(
                "RWSpeed",
                NumberCellType(),
                "Скорость\nповерхност.\n(м/с)",
                "Скорость поверхностны волн",
                self._get_column_width("RWSpeed"),
                optional=True,
            ),
            "TS": Column(
                "TS",
                VecCellType(NumberCellType(), 0, 2),
                "t попереч.\n(мс)",
                "Замер времени прохождения поперечных волн",
                self._get_column_width("TS"),
                optional=True,
            ),
            "SWSpeed": Column(
                "SWSpeed", NumberCellType(), "Скорость\nпопереч.\n(м/с)", "Скорость поперечных волн", self._get_column_width("SWSpeed"), optional=True
            ),
            "PuassonStatic": Column(
                "PuassonStatic",
                FloatCellType(),
                "Пуассон\nдинамич.",
                "Динамический коэффициент Пуассона",
                self._get_column_width("PuassonStatic"),
                optional=True,
            ),
            "YungStatic": Column(
                "YungStatic",
                FloatCellType(),
                "Юнг\nдинамич.",
                "Динамический модуль Юнга",
                self._get_column_width("YungStatic"),
                optional=True,
            ),
        }

    def get_columns(self) -> Iterable[Column]:
        return list(self._columns.values())

    def get_row_state(self, row: int):
        return self._rows[row]

    def get_value_at(self, col: int, row: int) -> str:
        _id = list(self._columns.keys()).__getitem__(col)
        row = self._rows[row]
        return row.fields[_id] if _id not in row.changed_fields else row.changed_fields[_id]

    def set_value_at(self, col: int, row: int, value: str):
        if self.get_value_at(col, row) != value:
            _id = list(self._columns.keys()).__getitem__(col)
            self._rows[row].changed_fields[_id] = value

    def insert_row(self, row: int):
        fields = {
            "Diameter": "0.0",
            "Length": "0.0",
            "Weight": "0",
            "CoreDepth": "0.0",
            "E": "0, 0, 0, 0",
            "Rotate": "0.0",
            "PartNumber": "",
            "RTens": "0.0",
            "Sensitivity": "0.0",
            "TP1": "",
            "TP2": "",
            "PWSpeed": "",
            "TR": "",
            "RWSpeed": "",
            "TS": "",
            "SWSpeed": "",
            "PuassonStatic": "",
            "YungStatic": "",
            "SampleNumber": "",
            "RockType": "",
        }
        self._rows.insert(row, _Row(None, fields, fields))

    def restore_row(self, row, state):
        if state.o != None:
            self._deleted_rows.remove(state.o.RID)
        self._rows.insert(row, state)

    def delete_row(self, row: int):
        if self._rows[row].o != None:
            self._deleted_rows.append(self._rows[row].o.RID)
        self._rows.__delitem__(row)

    def total_rows(self) -> int:
        return len(self._rows)

    def have_changes(self) -> bool:
        for row in self._rows:
            if row.changed_fields:
                return True
        return len(self._deleted_rows) > 0

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
            if "SampleNumber" in row.changed_fields:
                _v = row.changed_fields["SampleNumber"]
            else:
                _v = row.fields["SampleNumber"]
            if len(_v) == 0:
                continue
            if _v not in duplicates:
                duplicates[_v] = []
            duplicates[_v].append(index)
        col = self._columns["SampleNumber"]
        for indexes in duplicates.values():
            if len(indexes) > 1:
                errors.append((col, indexes[0], "Номер замера должен быть уникален"))

        return errors

    @db_session
    def save(self):
        if len(self.validate()) > 0:
            wx.MessageBox("В таблице обнаружены ошибки. Сохранение невозможно.", "Ошибка сохранения.", style=wx.OK | wx.ICON_ERROR)
            return False

        for _id in self._deleted_rows:
            DischargeMeasurement[_id].delete()

        self._deleted_rows = []
        columns = self._columns
        sample_set = OrigSampleSet[self._core.RID]
        new_rows = []
        max_dsch_number = 0
        for row in self._rows:
            if row.o != None and max_dsch_number < int(row.o.DschNumber):
                max_dsch_number = int(row.o.DschNumber)
        for index, row in enumerate(self._rows):
            f = {**row.fields, **row.changed_fields}
            fields = {}
            fields["orig_sample_set"] = sample_set
            fields["SampleNumber"] = f["SampleNumber"]
            fields["Diameter"] = columns["Diameter"].cell_type.from_string(f["Diameter"])
            fields["Length"] = columns["Length"].cell_type.from_string(f["Length"])
            fields["Weight"] = columns["Weight"].cell_type.from_string(f["Weight"])
            fields["RockType"] = f["RockType"]
            fields["PartNumber"] = f["PartNumber"]
            fields["RTens"] = columns["RTens"].cell_type.from_string(f["RTens"])
            fields["Sensitivity"] = columns["Sensitivity"].cell_type.from_string(f["Sensitivity"])
            tp = [None, None]
            d = columns["TP1"].cell_type.from_string(f["TP1"])
            tp[: len(d)] = d
            fields["TP1_1"] = tp[0]
            fields["TP1_2"] = tp[1]
            tp = [None, None]
            d = columns["TP2"].cell_type.from_string(f["TP2"])
            tp[: len(d)] = d
            fields["TP2_1"] = tp[0]
            fields["TP2_2"] = tp[1]
            tr = [None, None]
            d = columns["TR"].cell_type.from_string(f["TR"])
            tr[: len(d)] = d
            fields["TR_1"] = tr[0]
            fields["TR_2"] = tr[1]
            ts = [None, None]
            d = columns["TS"].cell_type.from_string(f["TS"])
            ts[: len(d)] = d
            fields["TS_1"] = ts[0]
            fields["TS_2"] = ts[1]
            fields["PWSpeed"] = columns["PWSpeed"].cell_type.from_string(f["PWSpeed"])
            fields["RWSpeed"] = columns["RWSpeed"].cell_type.from_string(f["RWSpeed"])
            fields["SWSpeed"] = columns["SWSpeed"].cell_type.from_string(f["SWSpeed"])
            fields["PuassonStatic"] = columns["PuassonStatic"].cell_type.from_string(f["PuassonStatic"])
            fields["YungStatic"] = columns["YungStatic"].cell_type.from_string(f["YungStatic"])
            fields["CoreDepth"] = columns["CoreDepth"].cell_type.from_string(f["CoreDepth"])
            e0 = [0.0, None, None, None]
            e = columns["E"].cell_type.from_string(f["E"])
            for i, v in enumerate(e):
                e0[i] = float(v)
            fields["E1"] = e0[0]
            fields["E2"] = e0[1]
            fields["E3"] = e0[2]
            fields["E4"] = e0[3]
            fields["Rotate"] = columns["Rotate"].cell_type.from_string(f["Rotate"])
            if row.o != None:
                o = DischargeMeasurement[row.o.RID]
                o.set(**fields)
                new_rows.append(self._prepare_o(o))
            else:
                max_dsch_number += 1
                fields["DschNumber"] = str(max_dsch_number)
                o = DischargeMeasurement(**fields)
                new_rows.append(self._prepare_o(o))
        self._rows = new_rows
        commit()
        return True


class DMEditor(BaseEditor):
    @db_session
    def __init__(self, parent, identity, menubar, toolbar, statusbar):
        self._config_provider = ClassConfigProvider(__name__ + "." + self.__class__.__name__, __CONFIG_VERSION__)
        self._config_provider.flush()
        self.o = OrigSampleSet[identity.o.RID]
        super().__init__(
            parent,
            "Замеры: " + self.o.Name,
            identity,
            DMModel(identity.rel_data_o, self._config_provider),
            menubar,
            toolbar,
            statusbar,
            header_height=50,
        )
        self.editor.Bind(EVT_GRID_COLUMN_RESIZED, self._on_editor_column_resized)
        self.editor.Bind(EVT_GRID_MODEL_STATE_CHANGED, self._on_model_state_changed)

    def _on_model_state_changed(self, event):
        self.editor.validate(save_edit_control=False)

    def _on_editor_column_resized(self, event):
        if self._config_provider["column_width"] == None:
            self._config_provider["column_width"] = {}
        self._config_provider["column_width"][event.column.id] = event.size
        self._config_provider.flush()
