from typing import List, Iterable, Dict
import wx

from ui.widgets.grid_new import *
from ui.widgets.grid_new.widget import Column
from ui.windows.main_window.identity import Identity
from ui.class_config_provider import ClassConfigProvider
from ui.icon import get_art
from .widget import *
from dataclasses import dataclass, field

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


class DMEditor(wx.Panel):
    def __init__(self, parent, identity, menubar, toolbar, statusbar):
        super().__init__(parent.get_native())
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )
        self._config_provider.flush()
        self.o = identity.o
        self._identity = identity
        self._title = "Редактор: [Разгрузка] замеры для " + identity.o.Name

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor = GridEditor(self, DMModel(self._config_provider), menubar, toolbar, statusbar)
        main_sizer.Add(self.editor, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()

        self._bind_all()

    def _bind_all(self):
        self.editor.Bind(EVT_GRID_EDITOR_STATE_CHANGED, self._on_editor_state_changed)
        self.editor.Bind(EVT_GRID_COLUMN_RESIZED, self._on_editor_column_resized)

    def _on_editor_column_resized(self, event):
        if self._config_provider['column_width'] == None:
            self._config_provider['column_width'] = {}
        self._config_provider['column_width'][event.column.id] = event.size
        self._config_provider.flush()

    def _on_editor_state_changed(self, event):
        wx.PostEvent(self, EditorNBStateChangedEvent(target=self))

    def get_identity(self) -> Identity | None:
        return self._identity

    def get_title(self) -> str:
        return self._title

    def get_icon(self):
        return wx.ART_REPORT_VIEW, get_art(wx.ART_REPORT_VIEW, scale_to=16)

    def can_save(self) -> bool:
        return self.editor.can_save()

    def can_copy(self) -> bool:
        return self.editor.can_copy()

    def can_cut(self) -> bool:
        return self.editor.can_cut()

    def can_paste(self) -> bool:
        return self.editor.can_paste()

    def can_undo(self) -> bool:
        return self.editor.can_undo()

    def can_redo(self) -> bool:
        return self.editor.can_redo()

    def save(self):
        self.editor.save()

    def copy(self):
        self.editor.copy()

    def cut(self):
        self.editor.cut()

    def paste(self):
        self.editor.paste()

    def undo(self):
        self.editor.undo()

    def redo(self):
        self.editor.redo()

    def is_changed(self) -> bool:
        return self.editor.is_changed()

    def on_select(self):
        self.editor.apply_controls()

    def on_deselect(self):
        self.editor.remove_controls()

    def on_close(self) -> bool:
        if self.can_save():
            ret = wx.MessageBox(
                "Редактор имеет нехосраненные изменения. Сохранить?",
                "Подтвердите закрытие",
                style=wx.YES | wx.NO | wx.CANCEL | wx.YES_DEFAULT | wx.ICON_INFORMATION,
            )
            if ret == wx.CANCEL:
                return False
            elif ret == wx.YES:
                try:
                    self.save()
                except:
                    return False
        return True
    
    def is_read_only(self):
        return False
