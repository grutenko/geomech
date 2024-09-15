from .cell_type_proto import CellType
from wx.grid import GridCellEditor, GridCellRenderer, GridCellNumberRenderer, GridCellNumberEditor


class NumberCellType(CellType):
    __typname__ = "number"
    __typdescr__ = "Целое число"

    def __init__(self) -> None:
        super().__init__()
        self.GRID_CELL_NUMBER_EDITOR = GridCellNumberEditor()
        self.GRID_CELL_NUMBER_RENDERER = GridCellNumberRenderer()

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