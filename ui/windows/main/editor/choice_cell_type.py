import wx
from datetime import date, datetime

from wx.grid import GridCellRenderer, GridCellEditor, GridCellChoiceEditor, GridCellStringRenderer

from ui.widgets.grid.widget import CellType


class ChoiceCellType(CellType):
    def __init__(self, choices=[]) -> None:
        super().__init__()
        self.choices = choices

    def test_repr(self, value) -> bool:
        return value.strip() in self.choices

    def to_string(self, value) -> str:
        return value

    def from_string(self, value: str):
        return value

    def get_type_name(self) -> str:
        return "choice"

    def get_type_descr(self) -> str:
        return "Выбор из списка"

    def get_grid_renderer(self) -> GridCellRenderer:
        return GridCellStringRenderer()

    def get_grid_editor(self) -> GridCellEditor:
        return GridCellChoiceEditor(self.choices)
