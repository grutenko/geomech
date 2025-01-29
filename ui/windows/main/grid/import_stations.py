import datetime
from dataclasses import dataclass
from typing import Dict

import pubsub
import wx
from pony.orm import commit, db_session, select

from database import MineObject, Station
from ui.datetimeutil import encode_date
from ui.icon import get_icon
from ui.widgets.grid.widget import (
    EVT_GRID_EDITOR_STATE_CHANGED,
    EVT_GRID_MODEL_STATE_CHANGED,
    Column,
    FloatCellType,
    GridEditor,
    Model,
    NumberCellType,
    StringCellType,
)
from ui.windows.main.identity import Identity

from ..notebook.widget import EditorNBStateChangedEvent, EditorNotebook
from .date_cell_type import DateCellType
from .import_report import ImportReport


@dataclass
class _Row:
    fields: Dict[str, str]
    p: any = None
    full_number: str = None
    full_name: str = None


class _Model(Model):
    def __init__(self):
        super().__init__()
        self._rows = []
        self._columns = {
            "@number": Column(
                "@number",
                StringCellType(),
                "* Номер",
                "(Обязат.) Номер скважины",
                init_width=100,
            ),
            "Comment": Column(
                "Comment",
                StringCellType(),
                "Комментарий",
                "Комментарий",
                init_width=200,
                optional=True,
            ),
            "@mine_object": Column(
                "@mine_object",
                NumberCellType(),
                "* ID родителя",
                "(Обязат.) ID родителя",
                init_width=80,
            ),
            "X": Column("X", FloatCellType(), "X", "X", init_width=40),
            "Y": Column("Y", FloatCellType(), "Y", "Y", init_width=40),
            "Z": Column("Z", FloatCellType(), "Z", "Z", init_width=40),
            "StartDate": Column(
                "StartDate",
                DateCellType(),
                "* Дата\nзакладки",
                "(Обязат.) Дата закладки",
                init_width=100,
            ),
            "EndDate": Column(
                "EndDate",
                DateCellType(),
                "Дата завершения\nбурения",
                "Дата завершения бурения",
                init_width=100,
                optional=True,
            ),
        }

    @db_session
    def _make_number(self, row_index):
        p = self._rows[row_index].p
        if p == None:
            return

        p = MineObject[p.RID]
        number = ""
        name = " на"
        while p.Level > 0:
            number += "@" + (p.Name if len(p.Name) < 4 else p.Name[:4])
            name += " " + p.Name
            p = p.parent

        self._rows[row_index].full_number = number
        self._rows[row_index].full_name = name

    @db_session
    def validate(self):
        errors = []

        for col in self._columns.values():
            for row_index, row in enumerate(self._rows):
                if len(row.fields[col.id]) == 0:
                    if col.optional:
                        continue
                    else:
                        _msg = "Значение не должно быть пустым."
                        errors.append((col, row_index, _msg))
                if len(row.fields[col.id]) > 0 and not col.cell_type.test_repr(row.fields[col.id]):
                    _msg = 'Неподходящее значение для ячейки типа "%s"' % col.cell_type.get_type_descr()
                    errors.append((col, row_index, _msg))

        _mine_objects_ids = []
        for o in select(o for o in MineObject):
            _mine_objects_ids.append(o.RID)

        for index, row in enumerate(self._rows):
            _id = row.fields["@mine_object"]

            if len(_id) == 0 or not self._columns["@mine_object"].cell_type.test_repr(_id):
                continue

            _id = self._columns["@mine_object"].cell_type.from_string(_id)

            if _id not in _mine_objects_ids:
                errors.append(
                    (
                        self._columns["@mine_object"],
                        index,
                        "Горный обьект с таким ID не существует.",
                    )
                )

        duplicates = {}
        for index, row in enumerate(self._rows):
            _v = row.fields["@number"]
            if len(_v) == 0:
                continue
            if _v not in duplicates:
                duplicates[_v] = []
            duplicates[_v].append(index)
        col = self._columns["@number"]
        for indexes in duplicates.values():
            if len(indexes) > 1:
                errors.append((col, indexes[0], "Номер станции должен быть уникален"))

        stations = select(o for o in Station)
        _numbers = []
        for o in stations:
            _numbers.append(o.Number)

        for index, row in enumerate(self._rows):
            _v = row.fields["@number"]
            if len(_v) == 0 or row.full_number == None:
                continue
            if _v + row.full_number in _numbers:
                errors.append(
                    (
                        self._columns["@number"],
                        index,
                        "Станция с таким номером уже зарегистрирована",
                    )
                )

        return errors

    def get_columns(self):
        return list(self._columns.values())

    def total_rows(self):
        return len(self._rows)

    def insert_row(self, index):
        fields = {
            "@number": "",
            "Comment": "",
            "@mine_object": "",
            "X": "0.0",
            "Y": "0.0",
            "Z": "0.0",
            "StartDate": "",
            "EndDate": "",
        }
        self._rows.insert(index, _Row(fields))

    def get_value_at(self, col, row) -> str:
        return self._rows[row].fields[list(self._columns.values())[col].id]

    @db_session
    def set_value_at(self, col, row_index, value):
        col_id = list(self._columns.values())[col].id
        value = value.strip()
        self._rows[row_index].fields[col_id] = value

        col_keys = list(self._columns.keys())
        if col_keys[col] == "@mine_object":
            col = self._columns["@mine_object"]
            if col.cell_type.test_repr(value):
                p = select(o for o in MineObject if o.RID == col.cell_type.from_string(value)).first()
                if p != None:
                    self._rows[row_index].p = p
                    self._make_number(row_index)
                else:
                    self._rows[row_index].p = p

    def delete_row(self, row):
        del self._rows[row]

    def restore_row(self, row, state):
        self._rows.insert(row, state)

    def have_changes(self):
        return len(self._rows) > 0

    def get_row_state(self, row):
        return self._rows[row]

    @db_session
    def save(self):
        self._stations = []
        cc = self._columns
        for row in self._rows:
            p = MineObject[row.p.RID]
            _fields = {
                "mine_object": p,
                "Number": row.fields["@number"] + row.full_number,
                "Name": row.fields["@number"] + row.full_name,
                "Comment": row.fields["Comment"],
                "X": cc["X"].cell_type.from_string(row.fields["X"]),
                "Y": cc["Y"].cell_type.from_string(row.fields["Y"]),
                "Z": cc["Z"].cell_type.from_string(row.fields["Z"]),
                "StartDate": encode_date(cc["StartDate"].cell_type.from_string(row.fields["StartDate"])),
                "HoleCount": 0,
            }

            if len(row.fields["EndDate"]) > 0:
                _fields["EndDate"] = encode_date(cc["EndDate"].cell_type.from_string(row.fields["EndDate"]))

            self._stations.append(Station(**_fields))

        commit()
        self._rows = []
        return True


class GridPanel(GridEditor):
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent, _Model(), menubar, toolbar, statusbar, header_height=40)
        self.show_errors_view()


class ImportStations(wx.Panel):
    @db_session
    def __init__(self, parent, menu, toolbar, statusbar):
        super().__init__(parent)
        self.menu = menu
        self.toolbar = toolbar
        self.statusbar = statusbar

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._local_toolbar = wx.ToolBar(self, style=wx.TB_HORIZONTAL | wx.TB_HORZ_TEXT)
        item = self._local_toolbar.AddTool(wx.ID_SPELL_CHECK, "Проверить", get_icon("check"))
        self._local_toolbar.Bind(wx.EVT_TOOL, self._on_check, item)
        item = self._local_toolbar.AddTool(wx.ID_SAVE, "Импортировать", get_icon("import-xls"))
        self._local_toolbar.Bind(wx.EVT_TOOL, self._on_import, item)
        self._local_toolbar.Realize()
        main_sizer.Add(self._local_toolbar, 0, wx.EXPAND)
        self.grid = GridPanel(self, menu, toolbar, statusbar)
        main_sizer.Add(self.grid, 1, wx.EXPAND)

        self.SetSizer(main_sizer)
        self.Layout()

        o = select(o for o in MineObject if o.Level == 0).first()
        self._identity = Identity(o, o, "import_stations")

        self._controls_initialized = False

        self._bind_all()

        self._valid = None

    def _bind_all(self):
        self.grid.Bind(EVT_GRID_EDITOR_STATE_CHANGED, self._on_editor_state_changed)
        self.grid.Bind(EVT_GRID_MODEL_STATE_CHANGED, self._on_model_state_changed)

    def _on_model_state_changed(self, event):
        self.grid.validate(save_edit_control=False)

    def _on_import(self, event):
        self.save()

    def _on_check(self, event):
        self.grid.validate()

    @db_session
    def get_identity(self):
        return self._identity

    def get_title(self) -> str:
        return "Импортировать станции"

    def get_icon(self):
        return "import-xls", get_icon("import-xls", scale_to=16)

    def can_save(self) -> bool:
        return self.grid.can_save()

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

    def can_find(self) -> bool:
        return self.grid.can_find()

    def can_find_next(self) -> bool:
        return self.grid.can_find_next()

    def find(self):
        self.grid.find()

    def find_next(self):
        self.grid.find_next()

    def save(self):
        if not self.grid.validate():
            wx.MessageBox(
                "В таблице обнаружены ошибки. Импорт невозможен.",
                "Ошибки таблицы",
                style=wx.OK | wx.ICON_ERROR,
            )
            return
        ret = wx.MessageBox(
            "В базу данных будут добавлены скважины в соотретствии с представленой таблицей. Продолжить?",
            "Подтвердите импорт",
            style=wx.YES | wx.NO | wx.YES_DEFAULT | wx.ICON_INFORMATION,
        )
        if ret != wx.YES:
            return
        if self.grid.save():
            m = EditorNotebook.get_instance().get_native()
            time = datetime.datetime.now()
            title = "Отчет об импорте: %s:%s:%s" % (str(time.hour).zfill(2), str(time.minute).zfill(2), str(time.second).zfill(2))
            columns = {
                "RID": Column("RID", NumberCellType(), "ID", "ID скважины"),
                "Number": Column("Number", StringCellType(), "№", "Номер станции", init_width=150),
                "Name": Column("Name", StringCellType(), "Название", "Название станции", init_width=150),
            }
            table = []
            for s in self.grid._model._stations:
                _row = []
                _row.append(str(s.RID))
                _row.append(s.Number)
                _row.append(s.Name)
                table.append(_row)
            report = ImportReport(m, title, columns, table, self.menu, self.toolbar, self.statusbar)
            pubsub.pub.sendMessage("cmd.editor.open", target=self, editor=report)
            pubsub.pub.sendMessage("cmd.editor.close", target=self, identity=self._identity)

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
        self._local_toolbar.EnableTool(wx.ID_SAVE, self.can_save())
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
