from typing import Iterable, Dict
from dataclasses import dataclass, field
import wx

from database import DischargeMeasurement
from ui.widgets.grid import *
from ui.widgets.grid.controller import EVT_GRID_COLUMN_RESIZED
from ui.widgets.grid.column import Column
from ui.windows.main_window.notebook import NotebookPageIdentity
from ui.class_config_provider import ClassConfigProvider
from .base_grid import BaseGrid
from .vec_cell_type import VecCellType


@dataclass
class _Row:
    o: any
    changed_fields: Dict = field(default_factory=lambda: {})


class _Model(ModelProto):
    def __init__(self, config_provider) -> None:
        super().__init__()
        self._config_provider = config_provider
        self._rows = []
        self._columns = self._build_columns()

    def _get_column_width(self, name):
        column_width = self._config_provider["column_width"]
        if column_width != None and name in column_width:
            return column_width[name]
        return -1
    
    '''
    Column(
                "Diameter",
                FloatCellType(),
                "Диаметр",
                "Диаметр образца керна",
                self._get_column_width("Diameter"),
            ),
            Column(
                "Length",
                FloatCellType(),
                "Длина",
                "Длина образца керна",
                self._get_column_width("Length"),
            ),
            Column(
                "Weight",
                FloatCellType(),
                "Вес",
                "Вес образца керна",
                self._get_column_width("Weight"),
            ),
            Column(
                "CoreDepth",
                FloatCellType(),
                "Глубина взятия",
                "Глубина взятия образца керна",
                self._get_column_width("CoreDepth"),
            ),
    '''

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
                "E",
                VecCellType(FloatCellType(), min_count=1, max_count=4),
                "Относит. деформ",
                "Относительная деформация образца",
                self._get_column_width("E"),
            ),
            Column(
                "Rotate",
                FloatCellType(),
                "Угол корр. напряж.",
                "Угол коррекции направления напряжений",
                self._get_column_width("Rotate"),
            ),
            Column(
                "PartNumber",
                StringCellType(),
                "№ партии тензодат",
                "Номер партии тензодатчиков",
                self._get_column_width("PartNumber"),
            ),
            Column(
                "RTens",
                FloatCellType(),
                "Сопрот. Тезодат.",
                "Сопротивление тензодатчиков",
                self._get_column_width("RTens"),
            ),
            Column(
                "Sensitivity",
                FloatCellType(),
                "Чувств. Тезодат.",
                "Коэффициент чувствительности тензодатчиков",
                self._get_column_width("Sensitivity"),
            ),
            Column(
                "TP1",
                VecCellType(FloatCellType(), 0, 2),
                "Время продоль.",
                "Замер времени прохождения продольных волн (ультразвуковое профилирование или др.)",
                self._get_column_width("TP1"),
            ),
            Column(
                "TP2",
                VecCellType(FloatCellType(), 0, 2),
                "Время продоль. (торц.)",
                "Замер времени прохождения продольных волн (торц.)",
                self._get_column_width("TP2"),
            ),
            Column(
                "PWSpeed",
                FloatCellType(),
                "Скорость продоль.",
                "Коэффициент чувствительности тензодатчиков",
                self._get_column_width("PWSpeed"),
            ),
            Column(
                "TR",
                VecCellType(FloatCellType(), 0, 2),
                "Время поверхност.",
                "Замер времени прохождения поверхностных волн",
                self._get_column_width("TR"),
            ),
            Column(
                "RWSpeed",
                FloatCellType(),
                "Скорость поверхност.",
                "Скорость поверхностны волн",
                self._get_column_width("RWSpeed"),
            ),
            Column(
                "TS",
                VecCellType(FloatCellType(), 0, 2),
                "t попереч.",
                "Замер времени прохождения поперечных волн",
                self._get_column_width("TS"),
            ),
            Column(
                "SWSpeed",
                FloatCellType(),
                "Скорость попереч.",
                "Скорость поперечных волн",
                self._get_column_width("SWSpeed"),
            ),
            Column(
                "PuassonStatic",
                FloatCellType(),
                "Пуассон статич.",
                "Статический коэффициент Пуассона",
                self._get_column_width("PuassonStatic"),
            ),
            Column(
                "YungStatic",
                FloatCellType(),
                "Юнг статич.",
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

    def delete_row(self, row: int):
        self._rows.__delitem__(row)

    def total_rows(self) -> int:
        return len(self._rows)

    def have_changes(self) -> bool:
        for row in self._rows:
            if len(row.changed_fields.keys()) > 0:
                return True

        return False


__CONFIG_VERSION__ = 1


class DischargeMeasurementsEditor(BaseGrid):
    @classmethod
    def make_identity(self, o):
        return NotebookPageIdentity(o, (o, DischargeMeasurement))

    def __init__(self, parent, o, menubar, statusbar):
        super().__init__(parent, menubar, statusbar, self.__class__.make_identity(o))
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )
        self._config_provider.flush()
        self.o = o
        self.set_title("Редактор: [Разгрузка] замеры для " + o.Name)
        self._model = _Model(self._config_provider)
        self.start(self._model)

        self.Layout()

        self.grid.Bind(EVT_GRID_COLUMN_RESIZED, self._on_column_resized)

    def _on_column_resized(self, event):
        if self._config_provider["column_width"] == None:
            self._config_provider["column_width"] = {}
        self._config_provider["column_width"][event.column.id] = event.size
        self._config_provider.flush()
