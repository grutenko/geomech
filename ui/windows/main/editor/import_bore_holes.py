from typing import List, Dict
import wx
from dataclasses import dataclass, field

from ui.widgets.grid.widget import *
from ui.widgets.grid.widget import Column
from .date_cell_type import DateCellType
from .choice_cell_type import ChoiceCellType
from ui.datetimeutil import encode_date


from .widget import EditorNBStateChangedEvent
from pony.orm import *
from database import *
from ui.windows.main.identity import Identity


@dataclass
class _Row:
    fields: Dict[str, str]
    p: any = None
    full_number: str = None


class _Model(Model):
    def __init__(self):
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
            "@parent_type": Column(
                "@parent_type",
                ChoiceCellType(["Горный объект", "Станция"]),
                "* Тип родителя",
                "(Обязат.) Тип родителя",
            ),
            "@station_or_mine_object": Column(
                "@station_or_mine_object",
                NumberCellType(),
                "* ID родителя",
                "(Обязат.) ID родителя",
                init_width=80,
            ),
            "X": Column("X", FloatCellType(), "X", "X", init_width=40),
            "Y": Column("Y", FloatCellType(), "Y", "Y", init_width=40),
            "Z": Column("Z", FloatCellType(), "Z", "Z", init_width=40),
            "Azimuth": Column(
                "Azimuth",
                FloatCellType(),
                "* Азимут\n(град.)",
                "(Обязат.) Азимут (град.)",
                init_width=70,
            ),
            "Tilt": Column(
                "Tilt",
                FloatCellType(),
                "* Наклон\n(град.)",
                "(Обязат.) Наклон (град.)",
                init_width=70,
            ),
            "Diameter": Column(
                "Diameter",
                FloatCellType(),
                "* Диаметр\n(м)",
                "(Обязат.) Диаметр (м)",
                init_width=70,
            ),
            "Length": Column("Length", FloatCellType(), "Длина\n(м)", "Длина (м)", init_width=70),
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
            "DestroyDate": Column(
                "DestroyDate",
                DateCellType(),
                "Дата\nликвидации",
                "Дата ликвидации",
                init_width=100,
                optional=True,
            ),
            "@Core_Need": Column(
                "@Core_Need",
                ChoiceCellType(["Да", "Нет"]),
                "* Добавить\nкерн?",
                "(Обязат.) Добавить керн?",
            ),
            "Core_Comment": Column(
                "Core_Comment",
                StringCellType(),
                "Керн: Комментарий",
                "Керн: Комментарий",
                init_width=200,
                optional=True,
            ),
            "Core_StartSetDate": Column(
                "Core_StartSetDate",
                DateCellType(),
                "Керн: Дата\nначала отбора",
                "Керн: Дата начала отбора",
                init_width=100,
                optional=True,
            ),
            "Core_EndSetDate": Column(
                "Core_EndSetDate",
                DateCellType(),
                "Керн: Дата\nокончания отбора",
                "Керн: Дата окончания отбора",
                init_width=120,
                optional=True,
            ),
        }

        self._mine_objects = {}
        self._stations = {}

    @db_session
    def _make_number(self, row_index):
        p = self._rows[row_index].p
        if p == None:
            return
        if isinstance(p, MineObject):
            p = MineObject[p.RID]
            number = ""
            while p.Level > 0:
                number += "@" + (p.Name if len(p.Name) < 4 else p.Name[:4])
                p = p.parent
        else:
            station = Station[p.RID]
            number = "@" + station.Number

        self._rows[row_index].full_number = number

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

        for index, row in enumerate(self._rows):
            _type = row.fields["@parent_type"]
            _id = row.fields["@station_or_mine_object"]
            if (
                len(_type) == 0
                or len(_id) == 0
                or not self._columns["@parent_type"].cell_type.test_repr(_type)
                or not self._columns["@station_or_mine_object"].cell_type.test_repr(_id)
            ):
                continue

            _mine_objects_ids = []
            for o in select(o for o in MineObject):
                _mine_objects_ids.append(o.RID)
            _stations_ids = []
            for o in select(o for o in Station):
                _stations_ids.append(o.RID)
            _id = self._columns["@station_or_mine_object"].cell_type.from_string(_id)
            if _type == "Горный объект":
                if _id not in _mine_objects_ids:
                    errors.append(
                        (
                            self._columns["@station_or_mine_object"],
                            index,
                            "Горный обьект с таким ID не существует.",
                        )
                    )
            elif _type == "Станция":
                if _id not in _stations_ids:
                    errors.append(
                        (
                            self._columns["@station_or_mine_object"],
                            index,
                            "Станция с таким ID не существует.",
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
                errors.append((col, indexes[0], "Номер скважины должен быть уникален"))

        bh = select(o for o in BoreHole)
        _numbers = []
        for o in bh:
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
                        "Скважина с таким номером уже зарегистрирована",
                    )
                )

        return errors

    def get_columns(self) -> List[Column]:
        return list(self._columns.values())

    def total_rows(self):
        return len(self._rows)

    def insert_row(self, index):
        fields = {
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
            "@Core_Need": "Нет",
            "Core_Comment": "",
            "Core_StartSetDate": "",
            "Core_EndSetDate": "",
        }
        self._rows.insert(index, _Row(fields))

    def get_value_at(self, col, row) -> str:
        return self._rows[row].fields[list(self._columns.values())[col].id]

    def set_value_at(self, col, row_index, value):
        col_id = list(self._columns.values())[col].id
        self._rows[row_index].fields[col_id] = value.strip()
        row = self._rows[row_index]
        if col_id in ["@station_or_mine_object", "@parent_type"]:
            if self._columns["@parent_type"].cell_type.test_repr(row.fields["@parent_type"]) and self._columns[
                "@station_or_mine_object"
            ].cell_type.test_repr(row.fields["@station_or_mine_object"]):
                if (
                    row.p == None
                    or (row.fields["@parent_type"] == "Горный объект" and not isinstance(row.p, MineObject))
                    or (row.fields["@parent_type"] == "Станция" and not isinstance(row.p, Station))
                    or self._columns["@station_or_mine_object"].cell_type.from_string(row.fields["@station_or_mine_object"]) != row.p.RID
                ):
                    self.load_parent_entity(row_index)
                    self._make_number(row_index)
            else:
                self._rows[row_index].p = None
                self._rows[row_index].full_number = None

    @db_session
    def load_parent_entity(self, row_index):
        col = self._columns["@station_or_mine_object"]
        row = self._rows[row_index]
        _id = col.cell_type.from_string(row.fields["@station_or_mine_object"])
        o = None
        if row.fields["@parent_type"] == "Горный объект":
            if _id not in self._mine_objects:
                tmp = select(o for o in MineObject if o.RID == _id).first()
                if tmp != None:
                    self._mine_objects[_id] = tmp
                    o = tmp
                else:
                    o = None
            else:
                o = self._mine_objects[_id]
        elif row.fields["@parent_type"] == "Станция":
            if _id not in self._stations:
                tmp = select(o for o in Station if o.RID == _id).first()
                if tmp != None:
                    self._stations[_id] = tmp
                    o = tmp
                else:
                    o = None
            else:
                o = self._stations[_id]

        self._rows[row_index].p = o

    def delete_row(self, row):
        del self._rows[row]

    def restore_row(self, row, state):
        self._rows.insert(row, state)

    def have_changes(self):
        return len(self._rows) > 0

    def get_row_state(self, row):
        return self._rows[row]

    @db_session
    def _gen_name(self, n, p):
        if isinstance(p, MineObject):
            parent = MineObject[p.RID]
            name = n + " на"
        else:
            station = Station[p.RID]
            parent = station.mine_object
            name = station.Number.split("@")[0] + "/" + n + " на"
        while parent.Level > 0:
            name += " " + parent.Name
            parent = parent.parent
        return name

    @db_session
    def save(self):
        self.bore_holes = []
        for row in self._rows:
            cc = self._columns
            fields = {
                "Number": row.fields["@number"] + row.full_number,
                "Comment": row.fields["Comment"],
                "X": cc["X"].cell_type.from_string(row.fields["X"]),
                "Y": cc["Y"].cell_type.from_string(row.fields["Y"]),
                "Z": cc["Z"].cell_type.from_string(row.fields["Z"]),
                "Azimuth": cc["Azimuth"].cell_type.from_string(row.fields["Azimuth"]),
                "Tilt": cc["Tilt"].cell_type.from_string(row.fields["Tilt"]),
                "Diameter": cc["Diameter"].cell_type.from_string(row.fields["Diameter"]),
                "Length": cc["Length"].cell_type.from_string(row.fields["Length"]),
                "StartDate": encode_date(cc["StartDate"].cell_type.from_string(row.fields["StartDate"])),
            }

            if row.fields["@parent_type"] == "Станция":
                fields["station"] = Station[cc["@station_or_mine_object"].cell_type.from_string(row.fields["@station_or_mine_object"])]
                fields["mine_object"] = fields["station"].mine_object
                fields["Name"] = self._gen_name(row.fields["@number"], fields["station"])
            elif row.fields["@parent_type"] == "Горный объект":
                fields["mine_object"] = MineObject[cc["@station_or_mine_object"].cell_type.from_string(row.fields["@station_or_mine_object"])]
                fields["Name"] = self._gen_name(row.fields["@number"], fields["mine_object"])
            else:
                raise Exception("Внутренняя ошибка")

            if len(row.fields["EndDate"]) > 0:
                fields["EndDate"] = encode_date(cc["EndDate"].cell_type.from_string(row.fields["EndDate"]))
            if len(row.fields["DestroyDate"]) > 0:
                fields["DestroyDate"] = encode_date(cc["DestroyDate"].cell_type.from_string(row.fields["DestroyDate"]))

            bore_hole = BoreHole(**fields)

            if row.fields["@Core_Need"] == "Да":
                core_fields = {
                    "mine_object": bore_hole.mine_object,
                    "bore_hole": bore_hole,
                    "Number": "Керн:" + bore_hole.Number,
                    "Name": "Керн: " + bore_hole.Name,
                    "Comment": row.fields["Core_Comment"],
                    "X": bore_hole.X,
                    "Y": bore_hole.Y,
                    "Z": bore_hole.Z,
                    "SampleType": "CORE",
                    "StartSetDate": encode_date(cc["Core_StartSetDate"].cell_type.from_string(row.fields["Core_StartSetDate"])),
                }

                if len(row.fields["Core_EndSetDate"]) > 0:
                    core_fields["EndSetDate"] = encode_date(cc["Core_EndSetDate"].cell_type.from_string(row.fields["Core_EndSetDate"]))

                core = OrigSampleSet(**core_fields)

            self.bore_holes.append(bore_hole)

        commit()
        self._rows = []

class GridPanel(GridEditor):
    def __init__(self, parent, menubar, toolbar, statusbar):
        super().__init__(parent, _Model(), menubar, toolbar, statusbar, header_height=40)
        self.show_errors_view()


class ImportBoreHoles(wx.Panel):
    @db_session
    def __init__(self, parent, menu, toolbar, statusbar):
        super().__init__(parent)
        self.toolbar = toolbar

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
        self._identity = Identity(o, o, "import_bore_holes")

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
        return "Импортировать скважины"

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
            ...

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
