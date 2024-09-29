from typing import List, Iterable, Dict
import wx

from ui.widgets.grid_new import *
from ui.widgets.grid_new.widget import Column
from ui.windows.main_window.identity import Identity
from ui.class_config_provider import ClassConfigProvider
from ui.icon import get_art
from .widget import *
from dataclasses import dataclass, field

from .base_editor import BaseEditor

__CONFIG_VERSION__ = 1

import re
from wx.grid import (
    GridCellStringRenderer,
    GridCellAutoWrapStringEditor,
    GridCellRenderer,
    GridCellEditor,
)


@dataclass
class _Row:
    o: any
    changed_fields: Dict = field(default_factory=lambda: {})
    is_changed: bool = False


class VecCellType(CellType):
    def __init__(self, item_type: CellType, min_count=0, max_count=-1):
        self._item_type = item_type
        self.GRID_CELL_STRING_RENDERER = GridCellStringRenderer()
        self.GRID_CELL_STRING_EDITOR = GridCellAutoWrapStringEditor()

    def get_type_name(self) -> str:
        return "vec<%s>" % self._item_type.get_type_name()

    def get_type_descr(self) -> str:
        return "[Список] %s" % self._item_type.get_type_descr()

    def test_repr(self, value) -> bool:
        return super().test_repr(value)

    def to_string(self, value) -> str:
        return ";".join(map(lambda x: self._item_type.to_string(x), value))

    def from_string(self, value: str):
        values = []
        for item in re.split("\s*;\s*", value):
            values.append(self._item_type.from_string(item))
        return values

    def get_grid_renderer(self) -> GridCellRenderer:
        self.GRID_CELL_STRING_RENDERER.IncRef()
        return self.GRID_CELL_STRING_RENDERER

    def get_grid_editor(self) -> GridCellEditor:
        self.GRID_CELL_STRING_EDITOR.IncRef()
        return self.GRID_CELL_STRING_EDITOR

    def __eq__(self, o):
        return isinstance(o, VecCellType)


class DMModel(Model):
    def __init__(self, config_provider) -> None:
        super().__init__()
        self._config_provider = config_provider
        self._rows = []
        self._columns = self._build_columns()
        self._changed_columns = 0

    def _get_column_width(self, name):
        column_width = self._config_provider["column_width"]
        if column_width != None and name in column_width:
            return column_width[name]
        return -1

    def _build_columns(self):
        return [
            Column(
                "SampleNumber",
                StringCellType(),
                "№ Образца",
                "Регистрационный номер образца керна",
                self._get_column_width("SampleNumber"),
            ),
            Column(
                "Diameter",
                FloatCellType(),
                "Диаметр\n(м)",
                "Диаметр образца керна",
                self._get_column_width("Diameter"),
            ),
            Column(
                "Length",
                FloatCellType(),
                "Длина\n(м)",
                "Длина образца керна",
                self._get_column_width("Length"),
            ),
            Column(
                "Weight",
                FloatCellType(),
                "Вес\n(г)",
                "Вес образца\nкерна",
                self._get_column_width("Weight"),
            ),
            Column(
                "CoreDepth",
                FloatCellType(),
                "Глубина\nвзятия (м)",
                "Глубина взятия образца керна",
                self._get_column_width("CoreDepth"),
            ),
            Column(
                "E",
                VecCellType(FloatCellType(), min_count=1, max_count=4),
                "Относит.\nдеформ",
                "Относительная деформация образца",
                self._get_column_width("E"),
            ),
            Column(
                "Rotate",
                FloatCellType(),
                "Угол корр.\nнапряж.\n(град.)",
                "Угол коррекции направления напряжений",
                self._get_column_width("Rotate"),
            ),
            Column(
                "PartNumber",
                StringCellType(),
                "№ партии\nтензодат",
                "Номер партии тензодатчиков",
                self._get_column_width("PartNumber"),
            ),
            Column(
                "RTens",
                FloatCellType(),
                "Сопрот.\nТезодат. (Ом)",
                "Сопротивление тензодатчиков",
                self._get_column_width("RTens"),
            ),
            Column(
                "Sensitivity",
                FloatCellType(),
                "Чувств.\nТезодат.",
                "Коэффициент чувствительности тензодатчиков",
                self._get_column_width("Sensitivity"),
            ),
            Column(
                "TP1",
                VecCellType(FloatCellType(), 0, 2),
                "Время\nпродоль.\n(мс)",
                "Замер времени прохождения продольных волн (ультразвуковое профилирование или др.)",
                self._get_column_width("TP1"),
            ),
            Column(
                "TP2",
                VecCellType(FloatCellType(), 0, 2),
                "Время продоль.\n(торц.) (мс)",
                "Замер времени прохождения продольных волн (торц.)",
                self._get_column_width("TP2"),
            ),
            Column(
                "PWSpeed",
                FloatCellType(),
                "Скорость\nпродоль.\n(м/с)",
                "Коэффициент чувствительности тензодатчиков",
                self._get_column_width("PWSpeed"),
            ),
            Column(
                "TR",
                VecCellType(FloatCellType(), 0, 2),
                "Время\nповерхност.",
                "Замер времени прохождения поверхностных волн",
                self._get_column_width("TR"),
            ),
            Column(
                "RWSpeed",
                FloatCellType(),
                "Скорость\nповерхност.\n(мс)",
                "Скорость поверхностны волн",
                self._get_column_width("RWSpeed"),
            ),
            Column(
                "TS",
                VecCellType(FloatCellType(), 0, 2),
                "t попереч.\n(мс)",
                "Замер времени прохождения поперечных волн",
                self._get_column_width("TS"),
            ),
            Column(
                "SWSpeed",
                FloatCellType(),
                "Скорость\nпопереч.\n(м/с)",
                "Скорость поперечных волн",
                self._get_column_width("SWSpeed"),
            ),
            Column(
                "PuassonStatic",
                FloatCellType(),
                "Пуассон\nстатич.",
                "Статический коэффициент Пуассона",
                self._get_column_width("PuassonStatic"),
            ),
            Column(
                "YungStatic",
                FloatCellType(),
                "Юнг\nстатич.",
                "Статический модуль Юнга",
                self._get_column_width("YungStatic"),
            ),
        ]

    def get_columns(self) -> Iterable[Column]:
        return self._columns

    def get_row_state(self, row: int):
        return self._rows[row]

    def get_value_at(self, col: int, row: int) -> str:
        row = self._rows[row]
        _id = self._columns[col].id
        return (
            getattr(row.e, _id)
            if _id not in row.changed_fields
            else row.changed_fields[_id]
        )

    def set_value_at(self, col: int, row: int, value: str):
        if self.get_value_at(col, row) != value:
            self._rows[row].changed_fields[self._columns[col].id] = value

    def insert_row(self, row: int):
        fields = {}
        for col in self._columns:
            fields[col.id] = ""
        self._rows.insert(row, _Row(None, fields))

    def restore_row(self, row, state):
        self._rows.insert(row, state)

    def delete_row(self, row: int):
        self._rows.__delitem__(row)

    def total_rows(self) -> int:
        return len(self._rows)

    def have_changes(self) -> bool:
        for row in self._rows:
            if row.changed_fields:
                return True

        return False


class DMEditor(BaseEditor):
    def __init__(self, parent, identity, menubar, toolbar, statusbar):
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )
        self._config_provider.flush()
        super().__init__(
            parent,
            "Редактор: [Разгрузка] замеры для " + identity.o.Name,
            identity,
            DMModel(self._config_provider),
            menubar,
            toolbar,
            statusbar,
        )
        self.editor.Bind(EVT_GRID_COLUMN_RESIZED, self._on_editor_column_resized)

    def _on_editor_column_resized(self, event):
        if self._config_provider["column_width"] == None:
            self._config_provider["column_width"] = {}
        self._config_provider["column_width"][event.column.id] = event.size
        self._config_provider.flush()