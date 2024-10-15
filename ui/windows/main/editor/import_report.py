import wx

from ui.widgets.grid.widget import *

class _Model(Model):
    def __init__(self, columns, table):
        self._columns = columns
        self._table = table

    def get_columns(self):
        return list(self._columns.values())
    
    def total_rows(self):
        return len(self._table)
    
    def get_value_at(self, col, row) -> str:
        return self._table[row][col]

class ImportReport(wx.Panel):
    def __init__(self, parent, title, columns, table, menubar, toolbar, statusbar):
        super().__init__(parent)

        self._title = title

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.grid = GridEditor(self, _Model(columns, table), menubar, toolbar, statusbar, read_only=True)
        self.grid.auto_size_columns(True)
        main_sizer.Add(self.grid, 1, wx.EXPAND)
        self.SetSizer(main_sizer)
        self.Layout()

    def get_identity(self):
        return None

    def get_icon(self):
        return "check", get_icon("check", scale_to=16)
    
    def get_title(self):
        return self._title
    
    def is_read_only(self):
        return True
    
    def is_changed(self):
        return False
    
    def on_select(self):
        self.grid.apply_controls()

    def on_deselect(self):
        self.grid.remove_controls()

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

    def on_close(self) -> bool:
        self.grid.end()
        return True