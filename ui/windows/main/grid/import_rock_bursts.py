from typing import List

import wx

from ui.widgets.grid.widget import *
from ui.widgets.grid.widget import Column

from .choice_cell_type import ChoiceCellType
from .date_cell_type import DateCellType


class _Model(Model):
    def __init__(self):
        self._rows = []
        self._columns = [
            Column("@number", StringCellType(), "* Номер", "(Обязат.) Номер скважины", init_width=100),
            Column("Comment", StringCellType(), "Комментарий", "Комментарий", init_width=200, optional=True),
            Column(
                "@parent_type",
                ChoiceCellType(["Горный объект", "Станция"]),
                "* Тип родителя",
                "(Обязат.) Тип родителя",
            ),
            Column(
                "@station_or_mine_object",
                StringCellType(),
                "* ID родителя",
                "(Обязат.) ID родителя",
                init_width=80,
            ),
            Column("X", FloatCellType(), "X", "X", init_width=40),
            Column("Y", FloatCellType(), "Y", "Y", init_width=40),
            Column("Z", FloatCellType(), "Z", "Z", init_width=40),
            Column(
                "Azimuth",
                FloatCellType(),
                "* Азимут\n(град.)",
                "(Обязат.) Азимут (град.)",
                init_width=70,
            ),
            Column(
                "Tilt",
                FloatCellType(),
                "* Наклон\n(град.)",
                "(Обязат.) Наклон (град.)",
                init_width=70,
            ),
            Column(
                "Diameter",
                FloatCellType(),
                "* Диаметр\n(м)",
                "(Обязат.) Диаметр (м)",
                init_width=70,
            ),
            Column("Length", FloatCellType(), "Длина\n(м)", "Длина (м)", init_width=70),
            Column(
                "StartDate",
                DateCellType(),
                "* Дата\nзакладки",
                "(Обязат.) Дата закладки",
                init_width=100,
            ),
            Column("EndDate", DateCellType(), "Дата завершения\nбурения", "Дата завершения бурения", init_width=100, optional=True),
            Column("DestroyDate", DateCellType(), "Дата\nликвидации", "Дата ликвидации", init_width=100, optional=True),
            Column(
                "Core_Need",
                ChoiceCellType(["Да", "Нет"]),
                "* Добавить\nкерн?",
                "(Обязат.) Добавить керн?",
            ),
            Column("Core_Comment", StringCellType(), "Керн: Комментарий", "Керн: Комментарий", init_width=200, optional=True),
            Column("Core_StartSetDate", DateCellType(), "Керн: Дата\nначала отбора", "Керн: Дата начала отбора", init_width=100, optional=True),
            Column("Core_EndSetDate", DateCellType(), "Керн: Дата\nокончания отбора", "Керн: Дата окончания отбора", init_width=120, optional=True),
        ]

    def validate(self):
        errors = []
        for row_index, row in enumerate(self._rows):
            for col in self._columns:
                if len(row[col.id]) == 0:
                    if col.optional:
                        continue
                    else:
                        _msg = "Значение не должно быть пустым."
                        errors.append((col.name_long, row_index, _msg))
                elif not col.cell_type.test_repr(row[col.id]):
                    _msg = 'Неподходящее значение для ячейки типа "%s"' % col.cell_type.get_type_descr()
                    errors.append((col.name_long, row_index, _msg))
        return errors

    def get_columns(self) -> List[Column]:
        return self._columns

    def total_rows(self):
        return len(self._rows)

    def insert_row(self, index):
        self._rows.insert(
            index,
            {
                "@number": "",
                "Comment": "",
                "@parent_type": "Горный объект",
                "@station_or_mine_object": "",
                "X": "0.0",
                "Y": "0.0",
                "Z": "0.0",
                "Azimuth": "0.0",
                "Tilt": "0.0",
                "Diameter": "0.0",
                "Length": "0.0",
                "StartDate": "",
                "EndDate": "",
                "DestroyDate": "",
                "Core_Need": "Нет",
                "Core_Comment": "",
                "Core_StartSetDate": "",
                "Core_EndSetDate": "",
            },
        )

    def get_value_at(self, col, row) -> str:
        return self._rows[row][self._columns[col].id]

    def set_value_at(self, col, row, value):
        self._rows[row][self._columns[col].id] = value

    def delete_row(self, row):
        del self._rows[row]

    def restore_row(self, row, state):
        self._rows.insert(row, state)

    def have_changes(self):
        return len(self._rows) > 0

    def get_row_state(self, row):
        return self._rows[row]


class GridPanel(GridEditor):
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent, _Model(), menubar, toolbar, statusbar, header_height=40)
        self.show_errors_view()


from pony.orm import *

from database import MineObject
from ui.windows.main.identity import Identity

from ..notebook.widget import EditorNBStateChangedEvent


class ImportRockBursts(wx.Panel):
    @db_session
    def __init__(self, parent, menu, toolbar, statusbar):
        super().__init__(parent)
        self.toolbar = toolbar

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._local_toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.TB_HORZ_TEXT)
        item = self._local_toolbar.AddTool(wx.ID_SPELL_CHECK, "Проверить", get_icon("check"))
        self._local_toolbar.Bind(wx.EVT_TOOL, self._on_check, item)
        item = self._local_toolbar.AddTool(wx.ID_SAVE, "Импортировать", get_icon("import-xls"))
        self._local_toolbar.Realize()
        main_sizer.Add(self._local_toolbar, 0, wx.EXPAND)
        self.grid = GridPanel(self, menu, toolbar, statusbar)
        main_sizer.Add(self.grid, 1, wx.EXPAND)

        self.SetSizer(main_sizer)
        self.Layout()

        o = select(o for o in MineObject if o.Level == 0).first()
        self._identity = Identity(o, o, "import_rock_bursts")

        self._controls_initialized = False

        self._bind_all()

    def _bind_all(self):
        self.grid.Bind(EVT_GRID_EDITOR_STATE_CHANGED, self._on_editor_state_changed)

    def _on_check(self, event):
        self.grid.validate()

    @db_session
    def get_identity(self):
        return self._identity

    def get_title(self) -> str:
        return "Импортировать горные удары"

    def get_icon(self):
        return "import-xls", get_icon("import-xls", scale_to=16)

    def can_save(self) -> bool:
        return False

    def can_copy(self) -> bool:
        return self.grid.can_copy()

    def can_cut(self) -> bool:
        return self.grid.can_cut()

    def can_paste(self) -> bool:
        return self.grid.can_paste()

    def can_undo(self) -> bool:
        return self.grid.can_undo()

    def can_redo(self) -> bool:
        return self.grid.can_redo()

    def save(self):
        return self.grid.save()

    def copy(self):
        self.grid.copy()

    def cut(self):
        self.grid.cut()

    def paste(self):
        self.grid.paste()

    def undo(self):
        self.grid.undo()

    def redo(self):
        self.grid.redo()

    def is_changed(self) -> bool:
        return self.grid.is_changed()

    def on_select(self):
        self.grid.apply_controls()

    def on_deselect(self):
        self.grid.remove_controls()

    def _on_editor_state_changed(self, event):
        wx.PostEvent(self, EditorNBStateChangedEvent(target=self))

    def on_close(self) -> bool:
        if self.can_save():
            ret = wx.MessageBox(
                "Редактор имеет несохраненные изменения. Сохранить?",
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
        self.grid.end()
        return True

    def is_read_only(self):
        return False
