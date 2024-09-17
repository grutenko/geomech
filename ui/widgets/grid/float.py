from .cell_type_proto import CellType
from wx.grid import GridCellEditor, GridCellRenderer, GridCellFloatEditor, GridCellFloatRenderer

class FloatCellType(CellType):
    __typname__ = "float"
    __typdescr__ = "Число с плавающей запятой"

    def __init__(self) -> None:
        super().__init__()
        self.GRID_CELL_FLOAT_EDITOR = GridCellFloatEditor()
        self.GRID_CELL_FLOAT_RENDERER = GridCellFloatRenderer()

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
        return self.GRID_CELL_FLOAT_RENDERER

    def get_grid_editor(self) -> GridCellEditor:
        return self.GRID_CELL_FLOAT_EDITOR
    
    def __eq__(self, value: object) -> bool:
        return type(value) == FloatCellType