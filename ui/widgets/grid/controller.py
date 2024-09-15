import wx
import io
import csv
import math

from wx.grid import *
from typing import List

from .cell_error import CellError
from .cell_type_proto import CellType
from .model_proto import Model
from .icons_options import IconsOptions
from .commands import cmdAppendRows, cmdDeleteRows, cmdSetValue, cmdPaste

ID_SAVE = wx.ID_HIGHEST + 1
ID_SAVE_AND_EXIT = ID_SAVE + 1
ID_PASTE = ID_SAVE + 2
ID_ADD_ROWS = ID_SAVE + 3
ID_DELETE_ROWS = ID_SAVE + 4
ID_MOVE_UP = ID_SAVE + 5
ID_MOVE_DOWN = ID_SAVE + 6
ID_SET_VALUE = ID_SAVE + 7
ID_UNDO = ID_SAVE + 8
ID_REDO = ID_SAVE + 9
ID_SELECT_ALL = ID_SAVE + 10
ID_DESELETECT = ID_SAVE + 11
ID_TOGGLE_OPTIONAL_COLUMNS = ID_SAVE + 12
ID_COPY = ID_SAVE + 13
ID_CUT = ID_SAVE + 14
ID_TOGGLE_ERRORS = ID_SAVE + 15
ID_APPEND_ROW = ID_SAVE + 16
ID_COLSIZE_BY_HEADER = ID_SAVE + 17
ID_COLSIZE_BY_VALUE = ID_SAVE + 18


class Controller:
    def __init__(
        self,
        model: Model,
        view: Grid,
        toolbar: wx.ToolBar,
        statusbar: wx.StatusBar,
        menubar: wx.MenuBar,
        icons: IconsOptions = IconsOptions(),
        read_only: bool = False,
        support_move: bool = True,
    ) -> None:
        self._view = view
        self._model = model
        self._toolbar = toolbar
        self._statusbar = statusbar
        self._menubar = menubar
        self._icons = icons
        self._columns = []
        self._last_cursor_pos = None
        self._in_edit_mode = False

        self._statusbar.SetFieldsCount(4)
        self._statusbar.SetStatusText("Маштаб: 100%", 3)
        self._statusbar.Update()

        self._zoom = 1
        self._original_row_size = 20
        initial_columns = []
        for i in range(len(model.get_columns())):
            initial_columns.append(100)
        self._original_col_sizes = initial_columns
        self._original_font_size = 14

        self._view.SetColLabelSize(20)
        self._view.GridLineColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND)
        font: wx.Font = self._view.GetLabelFont()
        info: wx.NativeFontInfo = font.GetNativeFontInfo()
        info.SetNumericWeight(400)
        info.SetPointSize(14)
        font.SetNativeFontInfo(info)
        self._view.SetLabelFont(font)

        self._selection = []
        self._command_processor = wx.CommandProcessor()

        self._append_rows_undo_stack = []
        self._delete_rows_undo_stack = []
        self._set_cell_value_undo_stack = []
        self._past_undo_stack = []

        self._is_read_only = read_only
        self._supports_move = support_move

        self._init_controls()
        self._render(initial=True)
        self._bind()

    def _init_controls(self):
        if not self._is_read_only:
            self._changes_menu = wx.Menu()
            item = self._changes_menu.Append(ID_SAVE, "&Сохранить\tCTRL+S")
            item.Enable(False)
            self._changes_menu.Bind(wx.EVT_MENU, self._on_click_save, item)
            item.SetBitmap(self._icons.save)
            item = self._changes_menu.Append(
                ID_SAVE_AND_EXIT, "&Сохранить и выйти\tCTRL+SHIFT+S"
            )
            item.Enable(False)
            item.SetBitmap(self._icons.save)
            self._menubar.Append(self._changes_menu, "Файл")

        self._edit_menu = wx.Menu()
        item = self._edit_menu.Append(ID_COPY, "&Копировать\tCTRL+C")
        item.Enable(False)
        item.SetBitmap(self._icons.copy)
        self._edit_menu.Bind(wx.EVT_MENU, self._on_copy, item)

        if not self._is_read_only:
            item = self._edit_menu.Append(ID_CUT, "&Вырезать\tCTRL+X")
            item.Enable(False)
            item.SetBitmap(self._icons.cut)
            self._edit_menu.Bind(wx.EVT_MENU, self._on_cut, item)

            item = self._edit_menu.Append(ID_PASTE, "&Вставить\tCTRL+V")
            self._edit_menu.Bind(wx.EVT_MENU, self._on_paste, item)
            item.SetBitmap(self._icons.insert)

        self._menubar.Append(self._edit_menu, "Правка")

        if not self._is_read_only:
            self._edit_menu.AppendSeparator()

            item = self._edit_menu.Append(ID_UNDO, "&Отменить\tCTRL+Z")
            item.Enable(False)
            self._edit_menu.Bind(wx.EVT_MENU, self._on_undo, item)
            item.SetBitmap(self._icons.cancel)
            item = self._edit_menu.Append(ID_REDO, "&Вернуть\tCTRL+Y")
            item.Enable(False)
            self._edit_menu.Bind(wx.EVT_MENU, self._on_redo, item)
            item.SetBitmap(self._icons.back)

            self._edit_menu.AppendSeparator()

        item = self._edit_menu.Append(ID_SELECT_ALL, "&Выделить все\tCTRL+A")
        self._edit_menu.Bind(wx.EVT_MENU, self._on_select_all, item)
        item = self._edit_menu.Append(ID_DESELETECT, "&Снять выделение\tCTRL+SHIFT+A")
        self._edit_menu.Bind(wx.EVT_MENU, self._on_remove_selection, item)

        self._view_menu = wx.Menu()

        item = self._view_menu.AppendCheckItem(
            ID_TOGGLE_ERRORS, "Показать / Скрыть панель ошибок"
        )
        self._view_menu.Bind(wx.EVT_MENU, self._on_toggle_errors_panel, item)

        self._view_menu.AppendSeparator()
        item = self._view_menu.Append(
            ID_COLSIZE_BY_VALUE, "Ширина столбцов по значению"
        )
        self._view_menu.Bind(wx.EVT_MENU, self._on_cols_by_value, item)

        self._view_menu.AppendSeparator()

        menu = wx.Menu()

        menu.Append(50, "50%")
        menu.Append(75, "75%")
        menu.Append(100, "100%\tCTRL+SHIFT+M")
        menu.Append(150, "150%")
        menu.Append(200, "200%")
        menu.Append(300, "300%")
        menu.Append(400, "400%")

        menu.Bind(wx.EVT_MENU, self._on_zoom_change_clicked)

        self._view_menu.AppendSubMenu(menu, "Масштаб")

        self._menubar.Append(self._view_menu, "Вид")

        self._row_menu = wx.Menu()

        if not self._is_read_only:
            item = self._row_menu.Append(ID_APPEND_ROW, "&Добавить строку\tCTRL+R")
            item.SetBitmap(self._icons.add_row)
            self._row_menu.Bind(wx.EVT_MENU, self._on_add_one_empty_row, item)
            sub_menu = wx.Menu()
            for i in range(1, 20 + 1):
                sub_menu.Append(i, str(i))
            sub_menu.Bind(wx.EVT_MENU, self._on_add_empty_rows)
            item = self._row_menu.AppendSubMenu(sub_menu, "Добавить строки")
            item.SetBitmap(self._icons.add_row)
            self._row_menu.Bind(wx.EVT_MENU, self._on_add_one_empty_row, item)
            item = self._row_menu.Append(ID_DELETE_ROWS, "&Удалить строки\tDEL")
            self._row_menu.Bind(wx.EVT_MENU, self._on_delete_rows, item)
            item.Enable(False)
            item.SetBitmap(self._icons.delete_row)
            self._row_menu.AppendSeparator()
            item = self._row_menu.Append(ID_MOVE_UP, "&Переместить выше\tCTRL+UP")
            item.Enable(False)
            item.SetBitmap(self._icons.up)
            self._row_menu.Bind(wx.EVT_MENU, self._on_row_move_up, item)
            item = self._row_menu.Append(ID_MOVE_DOWN, "&Переместить ниже\tCTRL+DOWN")
            item.Enable(False)
            item.SetBitmap(self._icons.down)
            self._row_menu.Bind(wx.EVT_MENU, self._on_row_move_down, item)
            self._row_menu.AppendSeparator()

            self._menubar.Append(self._row_menu, "Строка")

        if not self._is_read_only:
            self._range_menu = wx.Menu()
            item = self._range_menu.Append(ID_SET_VALUE, "Присвоить значение")
            item.Enable(False)
            self._range_menu.Bind(wx.EVT_MENU, self._on_click_set_value, item)
            item.SetBitmap(self._icons.write_text)
            self._menubar.Append(self._range_menu, "Диапазон")

        # TOOLBAR
        if not self._is_read_only:
            tool: wx.ToolBarToolBase = self._toolbar.AddTool(
                ID_SAVE,
                "Сохранить",
                self._icons.save,
                "Сохранить изменения",
                kind=wx.ITEM_DROPDOWN,
            )
            tool.Enable(False)
            self._toolbar.Bind(wx.EVT_TOOL, self._on_click_save, id=ID_SAVE)
            self._toolbar_save_menu = wx.Menu()
            item = self._toolbar_save_menu.Append(ID_SAVE_AND_EXIT, "Сохранить и выйти")
            item.Enable(False)
            item.SetBitmap(self._icons.save)
            tool.SetDropdownMenu(self._toolbar_save_menu)
            self._toolbar.AddSeparator()
            tool = self._toolbar.AddTool(
                ID_ADD_ROWS,
                "Добавить строки",
                self._icons.add_row,
                "Добавить строки",
                kind=wx.ITEM_DROPDOWN,
            )
            self._toolbar.Bind(wx.EVT_TOOL, self._on_add_one_empty_row, id=ID_ADD_ROWS)
            menu = wx.Menu()
            for i in range(1, 21):
                menu.Append(i, str(i))
            menu.Bind(wx.EVT_MENU, self._on_add_empty_rows)
            tool.SetDropdownMenu(menu)
            tool = self._toolbar.AddTool(
                ID_DELETE_ROWS,
                "Удалить строки",
                self._icons.delete_row,
                "Удалить строки",
            )
            tool.Enable(False)
            self._toolbar.Bind(wx.EVT_TOOL, self._on_delete_rows, id=ID_DELETE_ROWS)
            tool = self._toolbar.AddTool(
                ID_MOVE_UP, "Переместить выше", self._icons.up, "Переместить выше"
            )
            tool.Enable(False)
            self._toolbar.Bind(wx.EVT_TOOL, self._on_row_move_up, id=ID_MOVE_UP)
            tool = self._toolbar.AddTool(
                ID_MOVE_DOWN,
                "Переместить ниже",
                self._icons.down,
                "Переместить ниже",
            )
            tool.Enable(False)
            self._toolbar.Bind(wx.EVT_TOOL, self._on_row_move_down, id=ID_MOVE_UP)
            self._toolbar.AddSeparator()
            tool = self._toolbar.AddTool(
                ID_SET_VALUE,
                "Присвоить значение",
                self._icons.write_text,
                "Присвоить значение",
            )
            tool.Enable(False)
            self._toolbar.Bind(wx.EVT_TOOL, self._on_click_set_value, id=ID_SET_VALUE)
            self._toolbar.AddSeparator()
            tool = self._toolbar.AddTool(
                ID_UNDO,
                "Отменить",
                self._icons.cancel,
                "Отменить последнюю операцию",
            )
            tool.Enable(False)
            self._toolbar.Bind(wx.EVT_TOOL, self._on_undo, id=ID_UNDO)
            tool = self._toolbar.AddTool(
                ID_REDO, "Вернуть", self._icons.back, "Вернуть последнюю операцию"
            )
            tool.Enable(False)
            self._toolbar.Bind(wx.EVT_TOOL, self._on_redo, id=ID_REDO)

            self._toolbar.Realize()

    def _on_zoom_change_clicked(self, event: wx.MenuEvent):
        factor = event.GetId()
        self._zoom = factor / 100
        self._render_sizing()
        self._statusbar.SetStatusText("Масштаб:" + str(factor) + '%', 3)

    def _on_cols_by_value(self, event):
        self._view.AutoSizeColumns(False)
        for column_index in range(self._view.GetNumberCols()):
            self._original_col_sizes[column_index] = self._view.GetColSize(column_index) / self._zoom

    def _on_click_save(self, event): ...

    def _on_copy(self, event=None):
        blocks: List[GridBlockCoords] = [x for x in self._view.GetSelectedBlocks()]

        if len(blocks) == 0:
            blocks.append(
                GridBlockCoords(
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

    def _on_cut(self, event):
        self._on_copy()
        blocks: List[GridBlockCoords] = [x for x in self._view.GetSelectedBlocks()]
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

    def _on_paste(self, event):
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
                        "Несоответствие выделения",
                        "Выделеный диапазон не соответствует вставляемой таблице. Игнорировать это?",
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

    def _on_undo(self, event):
        self._command_processor.Undo()
        self._update_controls_state()

    def _on_redo(self, event):
        self._command_processor.Redo()
        self._update_controls_state()

    def _on_toggle_errors_panel(self, event): ...

    def _on_add_one_empty_row(self, event):
        self._command_processor.Submit(cmdAppendRows(self, 1))
        self._update_controls_state()

    def _on_add_empty_rows(self, event):
        count_rows = event.GetId()
        self._command_processor.Submit(cmdAppendRows(self, count_rows))
        self._update_controls_state()

    def _on_delete_rows(self, event):
        self._command_processor.Submit(
            cmdDeleteRows(self, self._view.GetSelectedRows())
        )
        self._update_controls_state()

    def _on_row_move_up(self, event): ...

    def _on_row_move_down(self, event): ...

    def _on_select_all(self, event):
        self._view.SelectAll()

    def _on_remove_selection(self, event):
        self._view.DeselectCell()

    def _on_click_set_value(self, event):
        blocks = [x for x in self._view.GetSelectedBlocks()]
        cells_type = None
        cells = []

        if len(blocks) == 0:
            cur_row, cur_col = (
                self._view.GetGridCursorRow(),
                self._view.GetGridCursorCol(),
            )
            cells_type = self._columns[cur_col].cell_type
            cells = [(cur_row, cur_col)]
            cur_value = self._view.GetCellValue(cur_row, cur_col)
        else:
            for block in blocks:
                for row_index in range(block.GetTopRow(), block.GetBottomRow() + 1):
                    for col_index in range(block.GetLeftCol(), block.GetRightCol() + 1):
                        if cells_type == None:
                            cells_type = self._columns[col_index].cell_type
                        elif cells_type != self._columns[col_index].cell_type:
                            raise RuntimeError(
                                "Разные типы ячеек в диапазоне. Одновренное редактирование невозможно"
                            )
                        cells.append((row_index, col_index))
            cur_value = ""

        new_value = cells_type.open_editor(self._view, cur_value)
        if new_value != None:
            self._command_processor.Submit(cmdSetValue(self, cells, new_value))

        self._update_controls_state()

    def _on_add_one_empty_row(self, event):
        self._command_processor.Submit(cmdAppendRows(self, 1))
        self._update_controls_state()

    def _bind(self):
        self._view.Bind(EVT_GRID_SELECT_CELL, self._on_change_selected_cell)
        self._view.Bind(EVT_GRID_RANGE_SELECTED, self._on_change_selection)
        self._view.Bind(wx.EVT_MOUSEWHEEL, self._on_zoom)
        self._view.Bind(EVT_GRID_CMD_COL_SIZE, self._on_cell_dragged)
        self._view.Bind(EVT_GRID_CELL_CHANGING, self._on_cell_changing)

    def _on_cell_changing(self, event: GridEvent):
        row_index = event.GetRow()
        col_index = event.GetCol()
        value = event.GetString()
        self._command_processor.Submit(cmdSetValue(self, [(row_index, col_index)], value))
        self._update_controls_state()


    def _on_cell_dragged(self, event: GridSizeEvent):
        column_index = event.GetRowOrCol()
        self._original_col_sizes[column_index] = self._view.GetColSize(column_index) / self._zoom

    def _on_zoom(self, event: wx.MouseEvent):
        if event.controlDown and event.GetWheelAxis() == wx.MOUSE_WHEEL_VERTICAL:
            new_zoom = self._zoom + (event.GetWheelRotation() / 100)
            if new_zoom > 4:
                new_zoom = 4
            elif new_zoom < 0.5:
                new_zoom = 0.5
            self._zoom = new_zoom
            self._render_sizing()
            self._statusbar.SetStatusText("Масштаб: " + str(int(self._zoom * 100)) + '%', 3)
            self._statusbar.Update()
        else:
            event.Skip()

    def _on_change_selection(self, event):
        self._update_controls_state()

    def _update_undo_redo_state(self):
        """
        Update state of undo redo controls
        """
        global_enable = not self._in_edit_mode
        self._edit_menu.Enable(
            ID_UNDO, global_enable and self._command_processor.CanUndo()
        )
        self._edit_menu.Enable(
            ID_REDO, global_enable and self._command_processor.CanRedo()
        )
        self._toolbar.EnableTool(
            ID_UNDO, global_enable and self._command_processor.CanUndo()
        )
        self._toolbar.EnableTool(
            ID_REDO, global_enable and self._command_processor.CanRedo()
        )

    def _update_controls_state(self):
        """
        Update state of all controls (menubar, statusbar, toolbar)
        """
        blocks_selected = False
        blocks: GridBlocks = self._view.GetSelectedBlocks()
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
        if not self._is_read_only:
            self._range_menu.Enable(ID_SET_VALUE, global_enable and is_cells_selected)
            self._toolbar.EnableTool(ID_SET_VALUE, global_enable and is_cells_selected)

        self._edit_menu.Enable(ID_COPY, global_enable and is_cells_selected)

        if not self._is_read_only:
            self._edit_menu.Enable(ID_CUT, global_enable and is_cells_selected)

        if not self._is_read_only:
            self._toolbar.EnableTool(ID_ADD_ROWS, global_enable)

        rows = self._view.GetSelectedRows()
        is_rows_selected = len(rows) > 0

        if not self._is_read_only:
            self._row_menu.Enable(ID_DELETE_ROWS, global_enable and is_rows_selected)
            self._toolbar.EnableTool(ID_DELETE_ROWS, global_enable and is_rows_selected)

            if not self._is_read_only:
                self._row_menu.Enable(
                    ID_MOVE_UP, global_enable and is_rows_selected and min(rows) != 0
                )
                self._toolbar.EnableTool(
                    ID_MOVE_UP, global_enable and is_rows_selected and min(rows) != 0
                )
                self._row_menu.Enable(
                    ID_MOVE_DOWN,
                    global_enable
                    and is_rows_selected
                    and max(rows) < self._view.GetNumberRows() - 1,
                )
                self._toolbar.EnableTool(
                    ID_MOVE_DOWN,
                    global_enable
                    and is_rows_selected
                    and max(rows) < self._view.GetNumberRows() - 1,
                )

            self._changes_menu.Enable(
                ID_SAVE, not self._in_edit_mode and self._model.have_changes()
            )
            self._toolbar.EnableTool(
                ID_SAVE, not self._in_edit_mode and self._model.have_changes()
            )
            self._changes_menu.Enable(
                ID_SAVE_AND_EXIT, not self._in_edit_mode and self._model.have_changes()
            )
            self._toolbar_save_menu.Enable(
                ID_SAVE_AND_EXIT, not self._in_edit_mode and self._model.have_changes()
            )

        self._update_undo_redo_state()

        self._toolbar.Realize()

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
            attr = GridCellAttr()
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

    def _render_sizing(self, begin_batch: bool = True):
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
        self._statusbar.SetStatusText("Столбец: " + name, 1)
        self._statusbar.SetStatusText("Тип ячейки: " + column.cell_type.__typdescr__, 2)
        self._update_controls_state()
        event.Skip()

    def _unbind(self):
        self._view.Unbind(EVT_GRID_SELECT_CELL, handler=self._on_change_selected_cell)
        self._view.Unbind(wx.EVT_KILL_FOCUS, handler=self._on_kill_focus)
        self._view.Unbind(wx.EVT_SET_FOCUS, handler=self._on_set_focus)
        self._view.Unbind(EVT_GRID_RANGE_SELECTED, handler=self._on_change_selection)

    def detach(self):
        self._unbind()

        self._view.BeginBatch()
        if self._view.GetNumberRows() > 0:
            self._view.DeleteRows(0, self._view.GetNumberRows())
        if self._view.GetNumberCols() > 0:
            self._view.DeleteCols(0, self._view.GetNumberCols())
        self._view.EndBatch()

        while self._menubar.GetMenuCount() > 0:
            self._menubar.Remove(0)
        self._toolbar.ClearTools()
        self._toolbar.Realize()

    def _cmd_append_rows(self, number_rows):
        for i in range(number_rows):
            self._model.insert_row(self._model.total_rows())
        self._append_rows_undo_stack.append(number_rows)
        self._render()
        self._view.GoToCell(
            self._view.GetNumberRows() - 1, self._view.GetGridCursorCol()
        )

    def _cmd_undo_append_rows(self):
        number_rows = self._append_rows_undo_stack.pop()
        for i in range(number_rows):
            self._model.delete_row(self._model.total_rows() - 1)
        self._render()
        self._view.GoToCell(
            self._view.GetNumberRows() - 1, self._view.GetGridCursorCol()
        )

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

    def _cmd_undo_delete_rows(self):
        rows_data = self._delete_rows_undo_stack.pop()
        for row_index, state in rows_data.items():
            self._model.restore_row(row_index, state)
        self._render()

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

    def _cmd_undo_set_cell_value(self):
        undo = self._set_cell_value_undo_stack.pop()
        for cell_row, cell_col, value in undo:
            self._model.set_value_at(cell_col, cell_row, value)
        self._render()

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

    def _cmd_undo_paste(self):
        undo = self._past_undo_stack.pop()
        for row_index, col_index, value in undo:
            self._model.set_value_at(col_index, row_index, value)

        self._render()