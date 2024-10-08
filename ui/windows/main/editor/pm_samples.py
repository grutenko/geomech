import wx
from typing import Dict, List, Iterable
from dataclasses import dataclass, field

from ui.widgets.grid.widget import Column, Model, StringCellType, FloatCellType
from ui.class_config_provider import ClassConfigProvider
from .base_editor import BaseEditor
from ui.widgets.grid.widget import EVT_GRID_COLUMN_RESIZED


@dataclass
class _Row:
    o: any
    changed_fields: Dict = field(default_factory=lambda: {})
    is_changed: bool = False

class PmSamplesModel(Model):
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
                "№ Образца *",
                "Регистрационный номер образца керна",
                self._get_column_width("SampleNumber"),
            ),
            Column(
                "SSID",
                StringCellType(),
                "Проба *",
                "Проба",
                self._get_column_width("SSID"),
            ),
            Column(
                "SetDate",
                StringCellType(),
                "Дата\nотбора *",
                "Дата отбора образца в пробу",
                self._get_column_width("SetDate"),
            ),
            Column(
                "StartPosition",
                FloatCellType(),
                "Начальная\nпозиция *",
                "Начальная позиция",
                self._get_column_width("StartPosition"),
            ),
            Column(
                "EndPosition",
                FloatCellType(),
                "Конечная\nпозиция",
                "Конечная позиция",
                self._get_column_width("EndPosition"),
            ),
            Column(
                "BoxNumber",
                StringCellType(),
                "Ящик №",
                "Номер ящика",
                self._get_column_width("BoxNumber"),
            ),
            Column(
                "Length1",
                FloatCellType(),
                "Длина 1\n(м)",
                "Измерение: диаметр / сторона 1",
                self._get_column_width("Length1"),
            ),
            Column(
                "Length2",
                FloatCellType(),
                "Длина 2\n(м)",
                "Измерение: сторона 2",
                self._get_column_width("Length1"),
            ),
            Column(
                "Height",
                FloatCellType(),
                "Высота (м)",
                "Измерение: высота",
                self._get_column_width("Height"),
            ),
            Column(
                "MassAirDry",
                FloatCellType(),
                "масса в\nвоздушно-сухом\nсостоянии (г)",
                "Измерение: масса в воздушно-сухом состоянии",
                self._get_column_width("MassAirDry"),
            ),
            Column(
                "MassNatMoist",
                FloatCellType(),
                "масса в\nестественно-влажном\nсостоянии (г)",
                "Измерение: масса в естественно-влажном состоянии",
                self._get_column_width("MassNatMoist"),
            ),
            Column(
                "MassWater",
                FloatCellType(),
                "масса в\nводе (г)",
                "Измерение: масса в воде",
                self._get_column_width("MassWater"),
            ),
            Column(
                "MassWaterSatur",
                FloatCellType(),
                "Масса в\nводонасыщенном\nсостоянии (г)",
                "масса в водонасыщенном состоянии",
                self._get_column_width("MassWaterSatur"),
            ),
            Column(
                "MassWaterSatWater",
                FloatCellType(),
                "масса в\nводонасыщенном\nсостоянии в воде (г)",
                "Измерение: масса в водонасыщенном состоянии в воде",
                self._get_column_width("MassWaterSatWater"),
            ),
            Column(
                "MassDry",
                FloatCellType(),
                "масса в\nсухом состоянии\n(г)",
                "Измерение: масса в сухом состоянии",
                self._get_column_width("MassDry"),
            ),
            Column(
                "UniAxCompDistort",
                FloatCellType(),
                "разрушающая\nнагрузка при\nодноосном сжатии (кН)",
                "Измерение: разрушающая нагрузка при одноосном сжатии",
                self._get_column_width("UniAxCompDistort"),
            ),
            Column(
                "UniAxTensDistort",
                FloatCellType(),
                "разрушающая\nнагрузка при\nодноосном растяжении (кН)",
                "Измерение: разрушающая нагрузка при одноосном растяжении",
                self._get_column_width("UniAxTensDistort"),
            ),
            Column(
                "ElasticityModulus",
                FloatCellType(),
                "модуль\nупругости",
                "Измерение: модуль упругости",
                self._get_column_width("ElasticityModulus"),
            ),
            Column(
                "DeclineModulus",
                FloatCellType(),
                "модуль\nспада",
                "Измерение: модуль спада",
                self._get_column_width("DeclineModulus"),
            ),
            Column(
                "PuassonCoeff",
                FloatCellType(),
                "Коэффициент\nПуассона",
                "Измерение: коэффициент Пуассона",
                self._get_column_width("PuassonCoeff"),
            ),
            Column(
                "DiffStrength",
                FloatCellType(),
                "Дифференциальная\nпрочность",
                "Измерение: дифференциальная прочность",
                self._get_column_width("DiffStrength"),
            ),
        ]
    
    def get_columns(self) -> List[Column]:
        return self._columns
    
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



__CONFIG_VERSION__ = 1


class PmSamplesEditor(BaseEditor):
    def __init__(self, parent, identity, menubar, toolbar, statusbar):
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )
        self._config_provider.flush()
        super().__init__(
            parent,
            "Редактор: [Физ. Мех. свойства] Образцы для " + identity.o.Name,
            identity,
            PmSamplesModel(self._config_provider),
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
