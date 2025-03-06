from wx.grid import (
    GridCellChoiceEditor,
    GridCellEditor,
    GridCellRenderer,
    GridCellStringRenderer,
)

from ui.widgets.grid.widget import CellType


class ChoiceCellType(CellType):
    def __init__(self, choices=[], allow_other=False) -> None:
        super().__init__()
        self.choices = choices
        self.allow_other = allow_other

    def set_choices(self, choices):
        self.choices = choices

    def test_repr(self, value) -> bool:
        if self.allow_other:
            return True
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
        return GridCellChoiceEditor(self.choices, allowOthers=self.allow_other)

    def index_of(self, value):
        return self.choices.index(value)
