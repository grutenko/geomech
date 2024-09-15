import wx
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