import wx
import wx.grid
import wx.lib.newevent
import wx.lib.agw.flatnotebook

from typing import Protocol, List
from dataclasses import dataclass
from ui.icon import get_art
import io
import csv


class CellType(Protocol):
    def get_type_name(self) -> str:
        """
        Return short name of this type
        """
        return "Тип"

    def get_type_descr(self) -> str:
        """
        Return type description
        """
        return "Тип"

    def test_repr(self, value) -> bool:
        """
        Return true is str repr of value is valid for this type
        """
        ...

    def to_string(self, value) -> str:
        """
        Get string repr of value for this type
        """
        raise NotImplementedError("Method into_string() not implemented.")

    def from_string(self, value: str):
        """
        Get original repr of string value for this type
        """
        raise NotImplementedError("Method from_string() not implemented.")

    def get_grid_renderer(self) -> wx.grid.GridCellRenderer:
        """
        Return renderer for this type
        """
        raise NotImplementedError("Method get_grid_renderer() not implemented.")

    def get_grid_editor(self) -> wx.grid.GridCellEditor:
        """
        Return editor for this type
        """
        raise NotImplementedError("Method get_grid_editor() not implemented.")

    def open_editor(self, value: str) -> str:
        """
        Open dialog editor and return str repr of old value or none if edition canceled
        """
        return None


from wx.grid import (
    GridCellEditor,
    GridCellRenderer,
    GridCellStringRenderer,
    GridCellAutoWrapStringEditor,
)


class StringCellType(CellType):
    def __init__(self) -> None:
        super().__init__()

    def get_type_name(self):
        return "string"

    def get_type_descr(self) -> str:
        return "Строка"

    def test_repr(self, value) -> bool:
        return True

    def from_string(self, value: str):
        if value == None:
            return ""
        return value

    def to_string(self, value) -> str:
        if value == None:
            return ""
        return value

    def get_grid_renderer(self) -> GridCellRenderer:
        return GridCellStringRenderer()

    def get_grid_editor(self) -> GridCellEditor:
        return GridCellAutoWrapStringEditor()

    def open_editor(self, parent, value: str) -> str:
        dlg = wx.TextEntryDialog(
            parent, "Значение ячеек", "Веедите новое значения для выбраных ячеек", value
        )
        if dlg.ShowModal() == wx.ID_OK:
            return dlg.GetValue()
        return None

    def __eq__(self, value: object) -> bool:
        return type(value) == StringCellType


class FloatCellType(CellType):
    def __init__(self) -> None:
        super().__init__()

    def get_type_name(self):
        return "float"

    def get_type_descr(self) -> str:
        return "Число с плавающей запятой"

    def test_repr(self, value) -> bool:
        ret = True
        try:
            float_value = float(value)
        except ValueError:
            try:
                float_value = float(value.replace(",", "."))
            except ValueError:
                ret = False

        return ret

    def from_string(self, value: str):
        if value.strip() == "":
            return None
        try:
            float_value = float(value)
        except ValueError as e:
            try:
                float_value = float(value.replace(",", "."))
            except ValueError as e2:
                raise e

        return float_value

    def to_string(self, value) -> str:
        if value == None:
            return ""
        return str(value)

    def get_grid_renderer(self) -> GridCellRenderer:
        return wx.grid.GridCellFloatRenderer(
            precision=2, format=wx.grid.GRID_FLOAT_FORMAT_FIXED
        )

    def get_grid_editor(self) -> GridCellEditor:
        return wx.grid.GridCellFloatEditor(
            precision=2, format=wx.grid.GRID_FLOAT_FORMAT_FIXED
        )

    def __eq__(self, value: object) -> bool:
        return type(value) == FloatCellType


class NumberCellType(CellType):
    def __init__(self) -> None:
        super().__init__()

    def get_type_name(self):
        return "number"

    def get_type_descr(self) -> str:
        return "Целое число"

    def test_repr(self, value: str) -> bool:
        ret = True
        try:
            int_value = int(value)
        except ValueError:
            ret = False

        return ret

    def from_string(self, value: str):
        if value == None:
            return 0
        return int(value)

    def to_string(self, value) -> str:
        if value == None:
            return "0"
        return str(value)

    def get_grid_renderer(self) -> GridCellRenderer:
        return wx.grid.GridCellNumberRenderer()

    def get_grid_editor(self) -> GridCellEditor:
        return wx.grid.GridCellNumberEditor()

    def __eq__(self, value: object) -> bool:
        return type(value) == NumberCellType


@dataclass
class Column:
    id: any
    cell_type: CellType
    name_short: str
    name_long: str | None
    init_width: int = -1

    def __eq__(self, value: object) -> bool:
        return type(value) == Column and value.id == self.id


from ui.icon import get_icon


class CellView(wx.Dialog):
    def __init__(self, parent, column, row, value):
        colname = column.name_short.replace("\n", " ")
        super().__init__(
            parent,
            title="Свойства ячейки: Строка: %d, Cтолбец: %s" % (row, colname),
            size=wx.Size(400, 250),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._notebook = wx.Notebook(self)
        self._cell_pane = wx.Panel(self._notebook)
        self._col_pane = wx.Panel(self._notebook)
        self._type_pane = wx.Panel(self._notebook)
        self._notebook.AddPage(self._cell_pane, "Значение")
        self._notebook.AddPage(self._col_pane, "Столбец")
        self._notebook.AddPage(self._type_pane, "Тип данных")
        main_sizer.Add(self._notebook, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()


class ErrorsView(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        top_sizer = wx.BoxSizer(wx.VERTICAL)
        self._main_notebook = wx.lib.agw.flatnotebook.FlatNotebook(
            self, agwStyle=wx.lib.agw.flatnotebook.FNB_NO_NAV_BUTTONS
        )
        top_sizer.Add(self._main_notebook, 1, wx.EXPAND)
        main_panel = wx.Panel(self._main_notebook)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._list = wx.ListCtrl(main_panel, style=wx.LC_REPORT)
        self._list.AppendColumn("Столбец")
        self._list.AppendColumn("Строка")
        self._list.AppendColumn("Ошибка")
        main_sizer.Add(self._list, 1, wx.EXPAND)
        main_panel.SetSizer(main_sizer)
        self._main_notebook.AddPage(main_panel, "Ошибки", True)
        self.SetSizer(top_sizer)


class Model(Protocol):
    def get_columns(self) -> List[Column]: ...
    def get_value_at(self, row, col) -> str: ...
    def get_rows_count(self) -> int: ...
    def is_changed(self) -> bool: ...


GridEditorStateChangedEvent, EVT_GRID_EDITOR_STATE_CHANGED = wx.lib.newevent.NewEvent()

from wx.core import EmptyString


class cmdAppendRows(wx.Command):
    def __init__(self, target, number_rows):
        super().__init__(True, "Добавить пустые строки")
        self.target = target
        self.number_rows = number_rows

    def Do(self):
        if self.number_rows == 0:
            return False
        self.target._cmd_append_rows(self.number_rows)
        return True

    def Undo(self):
        self.target._cmd_undo_append_rows()
        return True


class cmdDeleteRows(wx.Command):
    def __init__(self, target, rows_pos):
        super().__init__(True, "Удалить выбранные строки")
        self.target = target
        self.rows_pos = rows_pos

    def Do(self):
        if len(self.rows_pos) == 0:
            return False
        self.target._cmd_delete_rows(self.rows_pos)
        return True

    def Undo(self):
        self.target._cmd_undo_delete_rows()
        return True


class cmdSetValue(wx.Command):
    def __init__(self, target, cells, value: str):
        super().__init__(True, "Установить значение в ячейки")
        self.target = target
        self.cells = cells
        self.value = value

    def Do(self):
        if len(self.cells) == 0:
            return False
        self.target._cmd_set_cell_value(self.cells, self.value)
        return True

    def Undo(self):
        self.target._cmd_undo_set_cell_value()
        return True


class cmdPaste(wx.Command):
    def __init__(self, target, start_row, start_col, table):
        super().__init__(True, "Вставить")
        self.target = target
        self.start_row = start_row
        self.start_col = start_col
        self.table = table

    def Do(self):
        self.target._cmd_paste(self.start_row, self.start_col, self.table)
        return True

    def Undo(self):
        self.target._cmd_undo_paste()
        return True


GridColumnResized, EVT_GRID_COLUMN_RESIZED = wx.lib.newevent.NewEvent()

ID_ADD_ROW = wx.ID_HIGHEST + 50
ID_REMOVE_ROW = ID_ADD_ROW + 1
ID_SELECT_ALL = ID_ADD_ROW + 2
ID_CANCEL_SELECTION = ID_ADD_ROW + 3
ID_TOGGLE_ERRORS = ID_ADD_ROW + 5
ID_COPY_HEADERS = ID_ADD_ROW + 6
ID_COPY_WITH_HEADER = ID_ADD_ROW + 7


class GridEditor(wx.Panel):
    def __init__(self, parent, model, menubar, toolbar, statusbar):
        super().__init__(parent)
        self.menubar: wx.MenuBar = menubar
        self.toolbar: wx.ToolBar = toolbar
        self.statusbar: wx.StatusBar = statusbar
        self._model = model

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._splitter = wx.SplitterWindow(self, style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE)

        self._hor_splitter = wx.SplitterWindow(
            self._splitter, style=wx.SP_3DSASH | wx.SP_LIVE_UPDATE
        )
        main_sizer.Add(self._splitter, 1, wx.EXPAND)

        self._view = wx.grid.Grid(
            self._hor_splitter,
            style=wx.WANTS_CHARS | wx.BORDER_NONE | wx.WS_EX_PROCESS_UI_UPDATES,
        )
        self._view.SetDoubleBuffered(True)
        self._view.DisableDragRowSize()
        self._view.SetSelectionBackground(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        )
        self._view.EnableDragRowSize(True)
        self._view.SetRowLabelSize(30)
        self._view.SetColLabelSize(50)
        self._view.CreateGrid(0, 0)
        self._view.EnableEditing(True)
        self._view.SetColMinimalAcceptableWidth(2)
        self._view.SetRowMinimalAcceptableHeight(20)
        self._zoom = 1
        self._original_row_size = 20
        initial_columns = []
        for column in model.get_columns():
            initial_columns.append(column.init_width if column.init_width > 0 else 100)
        self._original_col_sizes = initial_columns
        self._original_font_size = 9

        self._view.GridLineColour = wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_ACTIVEBORDER
        )
        font: wx.Font = self._view.GetLabelFont()
        info: wx.NativeFontInfo = font.GetNativeFontInfo()
        info.SetNumericWeight(400)
        info.SetPointSize(9)
        font.SetNativeFontInfo(info)
        self._view.SetLabelFont(font)

        self._hor_splitter.SetSashGravity(1)
        self._hor_splitter.SetMinimumPaneSize(250)
        self._hor_splitter.Initialize(self._view)

        self._errors_view = ErrorsView(self._splitter)
        self._errors_view.Hide()
        self._splitter.SetSashGravity(1)
        self._splitter.SetMinimumPaneSize(160)
        self._splitter.Initialize(self._hor_splitter)

        self.SetSizer(main_sizer)
        self.Layout()

        self._state = {
            "can_copy": False,
            "can_cut": False,
            "can_save": False,
            "can_paste": False,
            "can_undo": False,
            "can_redo": False,
            "can_save": False,
        }

        self._command_processor = wx.CommandProcessor()
        self._bind_all()

        self._last_cursor_pos = None
        self._in_edit_mode = False
        self._controls_initialized = False
        self._append_rows_undo_stack = []
        self._set_cell_value_undo_stack = []
        self._delete_rows_undo_stack = []
        self._past_undo_stack = []
        self._render(initial=True)

    def _bind_all(self):
        self._view.Bind(wx.grid.EVT_GRID_SELECT_CELL, self._on_change_selected_cell)
        self._view.Bind(wx.grid.EVT_GRID_RANGE_SELECTED, self._on_change_selection)
        self._view.Bind(wx.EVT_MOUSEWHEEL, self._on_zoom)
        self._view.Bind(wx.grid.EVT_GRID_CMD_COL_SIZE, self._on_cell_dragged)
        self._view.Bind(wx.grid.EVT_GRID_CELL_CHANGING, self._on_cell_changing)
        self._view.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self._on_cell_context_menu)
        self._view.GetGridWindow().Bind(wx.EVT_RIGHT_DOWN, self._on_right_click)
        self._view.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self._on_label_context_menu)
        self._errors_view._main_notebook.Bind(
            wx.lib.agw.flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSING,
            self._on_errors_view_closing,
            self._errors_view._main_notebook,
        )
        self._view.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self._on_editor_shown)
        self._view.Bind(wx.grid.EVT_GRID_EDITOR_HIDDEN, self._on_editor_hidden)

    def _on_editor_shown(self, event):
        self._in_edit_mode = True
        self._update_controls_state()

    def _on_editor_hidden(self, event):
        self._in_edit_mode = False
        self._update_controls_state()

    def _on_scroll(self, event):
        event.Veto()

    def _on_label_context_menu(self, event):
        if event.GetRow() == -1:
            menu = wx.Menu()
            item = menu.Append(wx.ID_INFO, "Свойства столбца")
            # menu.Bind(wx.EVT_MENU, self._on_copy_headers, item)
            item.SetBitmap(get_art(wx.ART_INFORMATION))
            item = menu.Append(ID_COPY_HEADERS, "Копировать заголовки")
            menu.Bind(wx.EVT_MENU, self._on_copy_headers, item)
            item.SetBitmap(get_art(wx.ART_COPY))
            self.PopupMenu(menu, event.GetPosition())

    def _on_errors_view_closing(self, event):
        self._splitter.Unsplit(self._errors_view)
        self._update_controls_state()
        event.Veto()

    def _on_right_click(self, event):
        x, y = self._view.CalcUnscrolledPosition(event.GetX(), event.GetY())
        row, col = self._view.XYToCell(x, y)
        if row != -1 and col != -1:
            event.Skip()
            return
        menu = wx.Menu()
        global_enable = not self._in_edit_mode
        item = menu.Append(ID_ADD_ROW, "Добавить строку\tCTRL+R")
        item.Enable(global_enable)
        menu.Bind(wx.EVT_MENU, self._on_add_row, item)
        submenu = wx.Menu()
        for i in range(1, 21):
            item = submenu.Append(i, str(i))
        item = menu.AppendSubMenu(submenu, "Добавить строки")
        submenu.Bind(wx.EVT_MENU, self._on_add_rows)
        item.SetBitmap(get_icon("add-row"))
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Выделить все")
        menu.Bind(wx.EVT_MENU, self._on_select_all, item)
        item = menu.Append(wx.ID_ANY, "Снять выделение")
        menu.Bind(wx.EVT_MENU, self._on_cancel_selection, item)
        self.PopupMenu(menu, event.GetPosition())

    def _on_add_rows(self, event: wx.MenuEvent):
        count = event.GetId()
        self._command_processor.Submit(cmdAppendRows(self, count))
        self._update_controls_state()

    def _on_cell_context_menu(self, event: wx.grid.GridEvent):
        self._view.SetGridCursor(event.GetRow(), event.GetCol())
        menu = wx.Menu()
        item = menu.Append(wx.ID_PROPERTIES, "Свойства ячейки")
        item.SetBitmap(get_art(wx.ART_QUESTION))
        menu.Bind(wx.EVT_MENU, self._on_open_cell_info, item)
        menu.AppendSeparator()
        submenu = wx.Menu()
        item = submenu.Append(wx.ID_COPY, "Копировать\tCTRL+C")
        item.SetBitmap(get_art(wx.ART_COPY))
        item.Enable(self._state["can_copy"])
        submenu.Bind(wx.EVT_MENU, self._on_copy, item)
        item = submenu.Append(
            ID_COPY_WITH_HEADER, "Копировать с заголовоком\tCTRL+SHIFT+C"
        )
        item.SetBitmap(get_art(wx.ART_COPY))
        item.Enable(self._state["can_copy"])
        submenu.Bind(wx.EVT_MENU, self._on_copy_with_headers, item)
        item = menu.AppendSubMenu(submenu, "Копировать")
        item.SetBitmap(get_art(wx.ART_COPY))
        item.Enable(self._state["can_copy"])
        item = menu.Append(wx.ID_CUT, "Вырезать\tCTRL+X")
        item.SetBitmap(get_art(wx.ART_CUT))
        item.Enable(self._state["can_cut"])
        item = menu.Append(wx.ID_PASTE, "Вставить\tCTRL+V")
        item.SetBitmap(get_art(wx.ART_PASTE))
        item.Enable(self._state["can_paste"])
        menu.AppendSeparator()
        global_enable = not self._in_edit_mode
        item = menu.Append(ID_ADD_ROW, "Добавить строку\tCTRL+R")
        item.Enable(global_enable)
        menu.Bind(wx.EVT_MENU, self._on_add_row, item)
        item.SetBitmap(get_icon("add-row"))
        submenu = wx.Menu()
        for i in range(1, 21):
            item = submenu.Append(i, str(i))
        item = menu.AppendSubMenu(submenu, "Добавить строки")
        submenu.Bind(wx.EVT_MENU, self._on_add_rows)
        item.SetBitmap(get_icon("add-row"))
        item = menu.Append(ID_REMOVE_ROW, "Удалить строку\tDEL")
        item.SetBitmap(get_icon("delete-row"))
        item.Enable(False)
        menu.Bind(wx.EVT_MENU, self._on_delete_row, item)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ANY, "Выделить все")
        menu.Bind(wx.EVT_MENU, self._on_select_all, item)
        item = menu.Append(wx.ID_ANY, "Снять выделение")
        menu.Bind(wx.EVT_MENU, self._on_cancel_selection, item)
        self.PopupMenu(menu, event.GetPosition())

    def _on_copy(self, event):
        self.copy(False)

    def _on_copy_with_headers(self, event):
        self.copy(True)

    def _on_copy_headers(self, event):
        header = []
        for column in self._columns:
            header.append(column.name_short)

        buffer = io.StringIO()
        writer = csv.writer(buffer, dialect="excel-tab")
        writer.writerows([header])

        if not wx.TheClipboard.IsOpened():
            if not wx.TheClipboard.Open():
                return

        wx.TheClipboard.SetData(wx.TextDataObject(buffer.getvalue()))
        wx.TheClipboard.Close()

    def _on_open_cell_info(self, event):
        column = self._columns[self._view.GetGridCursorCol()]
        row = self._view.GetGridCursorRow()
        dlg = CellView(self, column, row, "")
        dlg.ShowModal()

    def _render(self, initial=False):
        """
        Rerender grid from data provider
        """
        last_cursor_pos = self._last_cursor_pos
        self._columns = self._model.get_columns()

        self._view.BeginBatch()

        if self._view.GetNumberRows() > 0:
            self._view.DeleteRows(0, self._view.GetNumberRows())
        self._view.AppendRows(self._model.total_rows())
        if self._view.GetNumberCols() > 0:
            self._view.DeleteCols(0, self._view.GetNumberCols())
        self._view.AppendCols(len(self._columns))

        for col_index, column in enumerate(self._columns):
            self._view.SetColLabelValue(col_index, column.name_short)
            attr = wx.grid.GridCellAttr()
            renderer = column.cell_type.get_grid_renderer()
            attr.SetRenderer(renderer)
            editor = column.cell_type.get_grid_editor()
            attr.SetEditor(editor)
            self._view.SetColAttr(col_index, attr)

        for row_index in range(self._model.total_rows()):
            for col_index, column in enumerate(self._columns):
                self._view.SetCellValue(
                    row_index, col_index, self._model.get_value_at(col_index, row_index)
                )

        self._render_sizing(begin_batch=False)

        if (
            last_cursor_pos != None
            and self._view.GetNumberCols() > 0
            and self._view.GetNumberRows() > 0
        ):
            cursor_row, cursor_col = last_cursor_pos

            if cursor_col >= self._view.GetNumberCols():
                cursor_col = self._view.GetNumberCols() - 1
            if cursor_row >= self._view.GetNumberRows():
                cursor_row = self._view.GetNumberRows() - 1

            self._view.SetGridCursor(cursor_row, cursor_col)

        self._view.EndBatch()

    def _render_sizing(self, begin_batch=False):
        if begin_batch:
            self._view.BeginBatch()

        for col_index, size in enumerate(self._original_col_sizes):
            self._view.SetColSize(col_index, int(size * self._zoom))

        for row_index in range(self._view.GetNumberRows()):
            self._view.SetRowSize(row_index, int(self._original_row_size * self._zoom))

        font: wx.Font = self._view.GetDefaultCellFont()
        info: wx.NativeFontInfo = font.GetNativeFontInfo()
        info.SetFractionalPointSize(self._original_font_size * self._zoom)
        font.SetNativeFontInfo(info)
        self._view.SetDefaultCellFont(font)

        if begin_batch:
            self._view.EndBatch()

    def _on_change_selected_cell(self, event):
        self._last_cursor_pos = (event.GetRow(), event.GetCol())
        column = self._columns[event.GetCol()]
        if column.name_long != None:
            name = column.name_long
        else:
            name = column.name_short
        self.statusbar.SetStatusText("Столбец: " + name, 1)
        self.statusbar.SetStatusText(
            "Тип ячейки: " + column.cell_type.get_type_descr(), 2
        )
        self._update_controls_state()
        event.Skip()

    def _on_change_selection(self, event):
        self._update_controls_state()

    def _on_zoom(self, event):
        event.Skip()

    def _on_cell_dragged(self, event):
        column_index = event.GetRowOrCol()
        self._original_col_sizes[column_index] = (
            self._view.GetColSize(column_index) / self._zoom
        )
        wx.PostEvent(
            self,
            GridColumnResized(
                target=self,
                column=self._columns[column_index],
                size=self._original_col_sizes[column_index],
            ),
        )

    def _on_cell_changing(self, event):
        row_index = event.GetRow()
        col_index = event.GetCol()
        value = event.GetString()
        self._command_processor.Submit(
            cmdSetValue(self, [(row_index, col_index)], value)
        )
        self._update_controls_state()

    def _set_state(self, state):
        new_state = {**self._state, **state}
        eq = True
        for key in state.keys():
            if key not in self._state or state[key] != self._state[key]:
                eq = False
                break
        self._state = new_state
        if not eq:
            wx.PostEvent(self, GridEditorStateChangedEvent(target=self))

    def can_save(self) -> bool:
        return self._state["can_save"]

    def can_copy(self) -> bool:
        return self._state["can_copy"]

    def can_cut(self) -> bool:
        return self._state["can_cut"]

    def can_paste(self) -> bool:
        return self._state["can_paste"]

    def can_undo(self) -> bool:
        return self._state["can_undo"]

    def can_redo(self) -> bool:
        return self._state["can_redo"]

    def save(self):
        if self._model.save():
            self._update_controls_state()
            return True
        return False

    def copy(self, with_headers=False):
        blocks: List[wx.grid.GridBlockCoords] = [
            x for x in self._view.GetSelectedBlocks()
        ]

        if len(blocks) == 0:
            blocks.append(
                wx.grid.GridBlockCoords(
                    self._view.GetGridCursorRow(),
                    self._view.GetGridCursorCol(),
                    self._view.GetGridCursorRow(),
                    self._view.GetGridCursorCol(),
                )
            )
        else:
            for i in range(len(blocks) - 1):
                if (
                    blocks[i].TopRow != blocks[i + 1].TopRow
                    or blocks[i].BottomRow != blocks[i + 1].BottomRow
                ) and (
                    blocks[i].LeftCol != blocks[i + 1].LeftCol
                    or blocks[i].RightCol != blocks[i + 1].RightCol
                ):
                    raise RuntimeError(
                        "Копирование недоступно для выделеных фрагментов"
                    )

        table = []

        if len(blocks) == 1:
            for row_index in range(blocks[0].TopRow, blocks[0].BottomRow + 1):
                table.append([])
                for col_index in range(blocks[0].LeftCol, blocks[0].RightCol + 1):
                    table[len(table) - 1].append(
                        self._view.GetCellValue(row_index, col_index)
                    )
        elif (
            blocks[0].TopRow == blocks[1].TopRow
            and blocks[0].BottomRow == blocks[1].BottomRow
        ):
            blocks = sorted(blocks, key=lambda x: x.LeftCol)

            for row_index in range(blocks[0].TopRow, blocks[0].BottomRow + 1):
                table.append([])
                for block in blocks:
                    for col_index in range(block.LeftCol, block.RightCol + 1):
                        table[len(table) - 1].append(
                            self._view.GetCellValue(row_index, col_index)
                        )
        elif (
            blocks[0].LeftCol == blocks[1].LeftCol
            and blocks[0].RightCol == blocks[1].RightCol
        ):
            blocks = sorted(blocks, key=lambda x: x.TopRow)

            for block in blocks:
                for row_index in range(block.TopRow, block.BottomRow + 1):
                    table.append([])
                    for col_index in range(block.LeftCol, block.RightCol + 1):
                        table[len(table) - 1].append(
                            self._view.GetCellValue(row_index, col_index)
                        )

        buffer = io.StringIO()
        writer = csv.writer(buffer, dialect="excel-tab")
        writer.writerows(table)

        if not wx.TheClipboard.IsOpened():
            if not wx.TheClipboard.Open():
                return

        wx.TheClipboard.SetData(wx.TextDataObject(buffer.getvalue()))
        wx.TheClipboard.Close()

    def cut(self):
        self.copy()
        blocks: List[wx.grid.GridBlockCoords] = [
            x for x in self._view.GetSelectedBlocks()
        ]
        cells = []
        if len(blocks) == 0:
            cells.append((self._view.GetGridCursorRow(), self._view.GetGridCursorCol()))
        else:
            for block in blocks:
                for row_index in range(block.TopRow, block.BottomRow + 1):
                    for col_index in range(block.LeftCol, block.RightCol + 1):
                        cells.append((row_index, col_index))
        self._command_processor.Submit(cmdSetValue(self, cells, ""))
        self._update_controls_state()

    def paste(self):
        blocks = [x for x in self._view.GetSelectedBlocks()]
        cursor_row, cursor_col = (
            self._view.GetGridCursorRow(),
            self._view.GetGridCursorCol(),
        )
        if cursor_row == -1:
            cursor_row = 0
        if cursor_col == -1:
            cursor_col = 0

        if not wx.TheClipboard.IsOpened():
            if not wx.TheClipboard.Open():
                return

        if not wx.TheClipboard.IsSupported(wx.DataFormat(wx.DF_UNICODETEXT)):
            wx.TheClipboard.Close()
            return

        data = wx.TextDataObject()
        if not wx.TheClipboard.GetData(data):
            wx.TheClipboard.Close()
            return

        table = []
        buffer = io.StringIO(data.GetText())
        reader = csv.reader(buffer, dialect="excel-tab")
        for row in reader:
            if len(row) > 0:
                table.append(row)

        if len(table) == 0:
            wx.TheClipboard.Close()
            return

        if len(table) == 1 and len(table[0]) == 1:
            value = table[0][0]
            cells = []
            if len(blocks) > 0:
                for block in blocks:
                    for rowIndex in range(block.GetTopRow(), block.GetBottomRow() + 1):
                        for colIndex in range(
                            block.GetLeftCol(), block.GetRightCol() + 1
                        ):
                            cells.append((rowIndex, colIndex))
            else:
                cells.append((cursor_row, cursor_col))

            self._command_processor.Submit(cmdSetValue(self, cells, value))
        else:
            if len(blocks) > 1:
                wx.TheClipboard.Close()
                raise RuntimeError("Эта операция неприменима к нескольким выделениям.")

            if len(blocks) == 1:
                start_row, start_col = blocks[0].TopRow, blocks[0].LeftCol

                if abs(blocks[0].RightCol - blocks[0].LeftCol) + 1 != len(
                    table[0]
                ) or abs(blocks[0].TopRow - blocks[0].BottomRow) + 1 != len(table):
                    ret = wx.MessageBox(
                        "Выделеный диапазон не соответствует вставляемой таблице. Игнорировать это?",
                        "Несоответствие выделения",
                        style=wx.OK | wx.CANCEL | wx.CENTRE | wx.OK_DEFAULT,
                    )
                    if ret == wx.ID_CANCEL:
                        wx.TheClipboard.Close()
                        return
            else:
                start_row, start_col = cursor_row, cursor_col

            if len(table[0]) > (self._view.GetNumberCols() - start_col):
                wx.TheClipboard.Close()
                raise RuntimeError("Недостаточно столбцов для вставки таблицы.")

            rows_to_append = len(table) - (self._view.GetNumberRows() - start_row)
            if rows_to_append > 0:
                self._command_processor.Submit(cmdAppendRows(self, rows_to_append))

            self._command_processor.Submit(cmdPaste(self, start_row, start_col, table))

            wx.TheClipboard.Close()

    def undo(self):
        self._command_processor.Undo()
        self._update_controls_state()

    def redo(self):
        self._command_processor.Redo()
        self._update_controls_state()

    def apply_controls(self):
        if self._controls_initialized:
            self.remove_controls()
        self._controls_initialized = True
        menu: wx.Menu = self.menubar.GetMenu(1)
        self._sep_0 = menu.AppendSeparator()
        self._item_0 = menu.Append(ID_ADD_ROW, "Добавить строку\tCTRL+R")
        self._item_0.Enable(False)
        menu.Bind(wx.EVT_MENU, self._on_add_row, self._item_0)
        self._item_0.SetBitmap(get_icon("add-row"))
        self._item_1 = menu.Append(ID_REMOVE_ROW, "Удалить строку\tDEL")
        self._item_1.SetBitmap(get_icon("delete-row"))
        self._item_1.Enable(False)
        menu.Bind(wx.EVT_MENU, self._on_delete_row, self._item_1)
        self._sep_1 = menu.AppendSeparator()
        self._item_2 = menu.Append(ID_SELECT_ALL, "Выделить все\tCTRL+A")
        menu.Bind(wx.EVT_MENU, self._on_select_all, self._item_2)
        self._item_3 = menu.Append(ID_CANCEL_SELECTION, "Снять выделение\tCTRL+SHIFT+A")
        menu.Bind(wx.EVT_MENU, self._on_cancel_selection, self._item_3)

        menu: wx.Menu = self.menubar.GetMenu(2)

        self._sep_2 = menu.AppendSeparator()
        self._item_5 = menu.AppendCheckItem(
            ID_TOGGLE_ERRORS, "[Таблица:Ошибки] показать/скрыть\tCTRL+ALT+E"
        )
        menu.Bind(wx.EVT_MENU, self._on_toggle_errors, self._item_5)
        self._tool_sep_0 = self.toolbar.AddSeparator()
        self._tool_item_0 = self.toolbar.AddTool(
            ID_ADD_ROW, "Добавить строку", get_icon("add-row")
        )
        self._tool_item_0.Enable(False)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add_row, id=ID_ADD_ROW)
        self._tool_item_0 = self.toolbar.AddTool(
            ID_REMOVE_ROW, "Удалить строки", get_icon("delete-row")
        )
        self._tool_item_0.Enable(False)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_delete_row, id=ID_REMOVE_ROW)
        self.toolbar.Realize()
        self._update_controls_state()

    def _on_toggle_errors(self, event):
        if self._splitter.GetWindow2() != None:
            self._splitter.Unsplit(None)
        else:
            self._splitter.SplitHorizontally(
                self._hor_splitter, self._errors_view, -200
            )
        self._update_controls_state()

    def _on_select_all(self, event):
        self._view.SelectAll()

    def _on_cancel_selection(self, event):
        self._view.ClearSelection()

    def _on_add_row(self, event):
        self._command_processor.Submit(cmdAppendRows(self, 1))
        self._update_controls_state()

    def _on_delete_row(self, event):
        self._command_processor.Submit(
            cmdDeleteRows(self, self._view.GetSelectedRows())
        )
        self._update_controls_state()

    def remove_controls(self):
        if not self._controls_initialized:
            return
        menu: wx.Menu = self.menubar.GetMenu(1)
        menu.Remove(self._sep_0).Destroy()
        menu.Remove(self._item_0).Destroy()
        menu.Remove(self._item_1).Destroy()
        menu.Remove(self._sep_1).Destroy()
        menu.Remove(self._item_2).Destroy()
        menu.Remove(self._item_3).Destroy()
        menu = self.menubar.GetMenu(2)
        menu.Remove(self._item_5).Destroy()
        menu.Remove(self._sep_2).Destroy()
        self.toolbar.DeleteToolByPos(self.toolbar.GetToolsCount() - 3)
        self.toolbar.DeleteTool(ID_ADD_ROW)
        self.toolbar.DeleteTool(ID_REMOVE_ROW)
        self.toolbar.Realize()
        self._controls_initialized = False
        self._view.HideCellEditControl()
        self.statusbar.SetStatusText("", 1)
        self.statusbar.SetStatusText("", 2)

    def _update_undo_redo_state(self):
        if (
            self._state["can_undo"] != self._command_processor.CanUndo()
            or self._state["can_redo"] != self._command_processor.CanRedo()
        ):
            self._set_state(
                {
                    "can_undo": self._command_processor.CanUndo(),
                    "can_redo": self._command_processor.CanRedo(),
                }
            )

    def _update_controls_state(self):
        """
        Update state of all controls (menubar, statusbar, toolbar)
        """
        blocks_selected = False
        blocks: wx.grid.GridBlocks = self._view.GetSelectedBlocks()
        for block in blocks:
            blocks_selected = True
            break
        cursor_row, cursor_col = (
            self._view.GetGridCursorRow(),
            self._view.GetGridCursorCol(),
        )
        is_cursor_valid = cursor_row >= 0 and cursor_col >= 0
        is_cells_selected = is_cursor_valid or blocks_selected

        global_enable = not self._in_edit_mode
        _can_copy = global_enable
        _can_cut = global_enable
        _can_paste = global_enable
        _can_save = self._model.have_changes()
        if (
            self._state["can_copy"] != _can_copy
            or self._state["can_cut"] != _can_cut
            or self._state["can_paste"] != _can_paste
            or self._state["can_save"] != _can_save
        ):
            self._set_state(
                {
                    "can_copy": _can_copy,
                    "can_cut": _can_cut,
                    "can_paste": _can_paste,
                    "can_save": _can_save,
                }
            )
        self._update_undo_redo_state()

        if not self._controls_initialized:
            return

        rows = self._view.GetSelectedRows()
        is_rows_selected = len(rows) > 0

        _e_add_row = global_enable
        _e_remove_row = global_enable and is_rows_selected

        if _e_add_row != self.toolbar.GetToolEnabled(
            ID_ADD_ROW
        ) or _e_remove_row != self.toolbar.GetToolEnabled(ID_REMOVE_ROW):
            self.toolbar.EnableTool(ID_ADD_ROW, _e_add_row)
            self.toolbar.EnableTool(ID_REMOVE_ROW, _e_remove_row)
            self.toolbar.Realize()

        self.menubar.Enable(ID_ADD_ROW, global_enable)
        self.menubar.Enable(ID_REMOVE_ROW, global_enable and is_rows_selected)

        self.menubar.Check(ID_TOGGLE_ERRORS, self._splitter.GetWindow2() != None)

    def is_changed(self) -> bool:
        return self._model.have_changes()

    def _cmd_append_rows(self, number_rows):
        for i in range(number_rows):
            self._model.insert_row(self._model.total_rows())
        self._append_rows_undo_stack.append(number_rows)
        self._render()
        cursor_col = self._view.GetGridCursorCol()
        if cursor_col == -1:
            cursor_col = 0
        self._view.GoToCell(
            self._view.GetNumberRows() - 1, self._view.GetGridCursorCol()
        )
        _can_save = self._model.have_changes()
        if self._state["can_save"] != _can_save:
            self._set_state({"can_save": _can_save})

    def _cmd_undo_append_rows(self):
        number_rows = self._append_rows_undo_stack.pop()
        for i in range(number_rows):
            self._model.delete_row(self._model.total_rows() - 1)
        self._render()
        if self._model.total_rows() > 0:
            y = self._view.GetNumberRows() - 1
            x = self._view.GetGridCursorCol()
            self._view.GoToCell(y, x)
        _can_save = self._model.have_changes()
        if self._state["can_save"] != _can_save:
            self._set_state({"can_save": _can_save})

    def _cmd_delete_rows(self, rows_pos):
        undo = {}
        for row in rows_pos:
            undo[row] = self._model.get_row_state(row)
        self._delete_rows_undo_stack.append(undo)
        minus = 0
        for row_pos in rows_pos:
            self._model.delete_row(row_pos - minus)
            minus += 1
        self._render()
        _can_save = self._model.have_changes()
        if self._state["can_save"] != _can_save:
            self._set_state({"can_save": _can_save})

    def _cmd_undo_delete_rows(self):
        rows_data = self._delete_rows_undo_stack.pop()
        for row_index, state in rows_data.items():
            self._model.restore_row(row_index, state)
        self._render()
        _can_save = self._model.have_changes()
        if self._state["can_save"] != _can_save:
            self._set_state({"can_save": _can_save})

    def _cmd_set_cell_value(self, cells, value: str):
        undo = []
        for cell_row, cell_col in cells:
            undo.append(
                (cell_row, cell_col, self._model.get_value_at(cell_col, cell_row))
            )
        self._set_cell_value_undo_stack.append(undo)

        for cell_row, cell_col in cells:
            self._model.set_value_at(cell_col, cell_row, value)

        self._render()
        _can_save = self._model.have_changes()
        if self._state["can_save"] != _can_save:
            self._set_state({"can_save": _can_save})

    def _cmd_undo_set_cell_value(self):
        undo = self._set_cell_value_undo_stack.pop()
        for cell_row, cell_col, value in undo:
            self._model.set_value_at(cell_col, cell_row, value)
        self._render()
        _can_save = self._model.have_changes()
        if self._state["can_save"] != _can_save:
            self._set_state({"can_save": _can_save})

    def _cmd_paste(self, start_row, start_col, table):
        undo = []
        for row_index in range(len(table)):
            for col_index in range(len(table[row_index])):
                undo.append(
                    (
                        row_index + start_row,
                        col_index + start_col,
                        self._model.get_value_at(
                            col_index + start_col, row_index + start_row
                        ),
                    )
                )
                self._model.set_value_at(
                    col_index + start_col,
                    row_index + start_row,
                    table[row_index][col_index],
                )

        self._past_undo_stack.append(undo)
        self._render()
        _can_save = self._model.have_changes()
        if self._state["can_save"] != _can_save:
            self._set_state({"can_save": _can_save})

    def _cmd_undo_paste(self):
        undo = self._past_undo_stack.pop()
        for row_index, col_index, value in undo:
            self._model.set_value_at(col_index, row_index, value)

        self._render()
        _can_save = self._model.have_changes()
        if self._state["can_save"] != _can_save:
            self._set_state({"can_save": _can_save})

    def is_changed(self):
        return self._model.have_changes()

    def end(self): ...