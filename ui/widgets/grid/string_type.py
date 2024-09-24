from .cell_type_proto import CellType
import wx
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