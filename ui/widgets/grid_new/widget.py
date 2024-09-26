import wx
import wx.grid
import wx.lib.newevent

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
        self.GRID_CELL_STRING_RENDERER = GridCellStringRenderer()
        self.GRID_CELL_STRING_EDITOR = GridCellAutoWrapStringEditor()

    def get_type_name(self):
        return "string"
    
    def get_type_descr(self) -> str:
        return "Строка"

    def test_repr(self, value) -> bool:
        return True

    def from_string(self, value: str):
        return value

    def to_string(self, value) -> str:
        return value

    def get_grid_renderer(self) -> GridCellRenderer:
        self.GRID_CELL_STRING_RENDERER.IncRef()
        return self.GRID_CELL_STRING_RENDERER

    def get_grid_editor(self) -> GridCellEditor:
        self.GRID_CELL_STRING_EDITOR.IncRef()
        return self.GRID_CELL_STRING_EDITOR

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
        self.GRID_CELL_FLOAT_EDITOR = wx.grid.GridCellFloatEditor(precision=2, format=wx.grid.GRID_FLOAT_FORMAT_FIXED)
        self.GRID_CELL_FLOAT_RENDERER = wx.grid.GridCellFloatRenderer(precision=2, format=wx.grid.GRID_FLOAT_FORMAT_FIXED)

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
                float_value = float(value.replace(',', '.'))
            except ValueError:
                ret = False

        return ret

    def from_string(self, value: str):
        try:
            floatValue = float(value)
        except ValueError as e:
            try:
                float_value = float(value.replace(',', '.'))
            except ValueError as e2:
                raise e

        return float_value

    def to_string(self, value) -> str:
        return str(value)

    def get_grid_renderer(self) -> GridCellRenderer:
        self.GRID_CELL_FLOAT_RENDERER.IncRef()
        return self.GRID_CELL_FLOAT_RENDERER

    def get_grid_editor(self) -> GridCellEditor:
        self.GRID_CELL_FLOAT_EDITOR.IncRef()
        return self.GRID_CELL_FLOAT_EDITOR
    
    def __eq__(self, value: object) -> bool:
        return type(value) == FloatCellType
    
class NumberCellType(CellType):
    def __init__(self) -> None:
        super().__init__()
        self.GRID_CELL_NUMBER_EDITOR = wx.grid.GridCellNumberEditor()
        self.GRID_CELL_NUMBER_RENDERER = wx.grid.GridCellNumberRenderer()

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
        return int(value)

    def to_string(self, value) -> str:
        return str(value)

    def get_grid_renderer(self) -> GridCellRenderer:
        return self.GRID_CELL_NUMBER_RENDERER

    def get_grid_editor(self) -> GridCellEditor:
        return self.GRID_CELL_NUMBER_EDITOR
    
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


class GridEditor(wx.Panel):
    def __init__(self, parent, model, menubar, toolbar, statusbar):
        super().__init__(parent)
        self.menubar: wx.MenuBar = menubar
        self.toolbar: wx.ToolBar = toolbar
        self.statusbar: wx.StatusBar = statusbar
        self._model = model

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self._view = wx.grid.Grid(self)
        self._view.SetDoubleBuffered(True)
        self._view.DisableDragRowSize()
        self._view.SetSelectionBackground(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        )
        self._view.SetRowLabelSize(30)
        self._view.SetColLabelSize(20)
        self._view.CreateGrid(0, 0)
        self._view.EnableEditing(True)
        self._zoom = 1
        self._original_row_size = 20
        initial_columns = []
        for column in model.get_columns():
            initial_columns.append(column.init_width if column.init_width > 0 else 100)
        self._original_col_sizes = initial_columns
        self._original_font_size = 9

        self._view.SetColLabelSize(20)
        self._view.GridLineColour = wx.SystemSettings.GetColour(
            wx.SYS_COLOUR_ACTIVEBORDER
        )
        font: wx.Font = self._view.GetLabelFont()
        info: wx.NativeFontInfo = font.GetNativeFontInfo()
        info.SetNumericWeight(400)
        info.SetPointSize(9)
        font.SetNativeFontInfo(info)
        self._view.SetLabelFont(font)

        main_sizer.Add(self._view, 1, wx.EXPAND)

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
            attr.SetRenderer(column.cell_type.get_grid_renderer())
            attr.SetEditor(column.cell_type.get_grid_editor())
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

            self._view.GoToCell(cursor_row, cursor_col)

        self._view.EndBatch()

    def _render_sizing(self, begin_batch = False):
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

    def save(self): ...

    def copy(self):
        blocks: List[wx.grid.GridBlockCoords] = [x for x in self._view.GetSelectedBlocks()]

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
        blocks: List[wx.grid.GridBlockCoords] = [x for x in self._view.GetSelectedBlocks()]
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

                print(table)

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
        self._item_0.SetBitmap(get_art(wx.ART_PLUS))
        self._item_1 = menu.Append(ID_REMOVE_ROW, "Удалить строку\tDEL")
        self._item_1.Enable(False)
        menu.Bind(wx.EVT_MENU, self._on_delete_row, self._item_1)
        self._sep_1 = menu.AppendSeparator()
        self._item_2 = menu.Append(ID_SELECT_ALL, "Выделить все\tCTRL+A")
        menu.Bind(wx.EVT_MENU, self._on_select_all, self._item_2)
        self._item_3 = menu.Append(ID_CANCEL_SELECTION, "Снять выделение\tCTRL+SHIFT+A")
        menu.Bind(wx.EVT_MENU, self._on_cancel_selection, self._item_3)
        self._tool_sep_0 = self.toolbar.AddSeparator()
        self._tool_item_0 = self.toolbar.AddTool(ID_ADD_ROW, "Добавить строку", get_art(wx.ART_PLUS))
        self._tool_item_0.Enable(False)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add_row, id=ID_ADD_ROW)
        self._tool_item_0 = self.toolbar.AddTool(ID_REMOVE_ROW, "Удалить строки", get_art(wx.ART_DELETE))
        self._tool_item_0.Enable(False)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_delete_row, id=ID_REMOVE_ROW)
        self.toolbar.Realize()
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
        self.toolbar.DeleteToolByPos(self.toolbar.GetToolsCount() - 3)
        self.toolbar.DeleteTool(ID_ADD_ROW)
        self.toolbar.DeleteTool(ID_REMOVE_ROW)
        self.toolbar.Realize()
        self._controls_initialized = False

    def _update_undo_redo_state(self):
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
        self._set_state(
            {
                "can_copy": global_enable and is_cells_selected,
                "can_cut": global_enable and is_cells_selected,
                "can_paste": global_enable,
                "can_save": self._model.have_changes(),
            }
        )
        self._update_undo_redo_state()

        self.toolbar.EnableTool(ID_ADD_ROW, global_enable)
        rows = self._view.GetSelectedRows()
        is_rows_selected = len(rows) > 0
        self.menubar.Enable(ID_ADD_ROW, global_enable)
        self.menubar.Enable(ID_REMOVE_ROW, global_enable and is_rows_selected)
        self.toolbar.EnableTool(ID_REMOVE_ROW, global_enable and is_rows_selected)

        self.toolbar.Realize()

    def is_changed(self) -> bool:
        return self._model.have_changes()
    
    def _cmd_append_rows(self, number_rows):
        for i in range(number_rows):
            self._model.insert_row(self._model.total_rows())
        self._append_rows_undo_stack.append(number_rows)
        self._render()
        self._view.GoToCell(
            self._view.GetNumberRows() - 1, self._view.GetGridCursorCol()
        )
        self._set_state({"can_save": self._model.have_changes()})

    def _cmd_undo_append_rows(self):
        number_rows = self._append_rows_undo_stack.pop()
        for i in range(number_rows):
            self._model.delete_row(self._model.total_rows() - 1)
        self._render()
        if self._model.total_rows() > 0:
            y = self._view.GetNumberRows() - 1
            x = self._view.GetGridCursorCol()
            self._view.GoToCell(y, x)
        self._set_state({"can_save": self._model.have_changes()})

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
        self._set_state({"can_save": self._model.have_changes()})

    def _cmd_undo_delete_rows(self):
        rows_data = self._delete_rows_undo_stack.pop()
        for row_index, state in rows_data.items():
            self._model.restore_row(row_index, state)
        self._render()
        self._set_state({"can_save": self._model.have_changes()})

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
        self._set_state({"can_save": self._model.have_changes()})

    def _cmd_undo_set_cell_value(self):
        undo = self._set_cell_value_undo_stack.pop()
        for cell_row, cell_col, value in undo:
            self._model.set_value_at(cell_col, cell_row, value)
        self._render()
        self._set_state({"can_save": self._model.have_changes()})

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
        self._set_state({"can_save": self._model.have_changes()})

    def _cmd_undo_paste(self):
        undo = self._past_undo_stack.pop()
        for row_index, col_index, value in undo:
            self._model.set_value_at(col_index, row_index, value)

        self._render()
        self._set_state({"can_save": self._model.have_changes()})

    def is_changed(self):
        return self._model.have_changes()
