import wx
import re
from wx.grid import GridCellStringRenderer, GridCellAutoWrapStringEditor, GridCellRenderer, GridCellEditor
from ui.widgets.grid.cell_type_proto import CellType


class VecCellType(CellType):
    def __init__(self, item_type: CellType, min_count=0, max_count=-1):
        self._item_type = item_type
        self.GRID_CELL_STRING_RENDERER = GridCellStringRenderer()
        self.GRID_CELL_STRING_EDITOR = GridCellAutoWrapStringEditor()

    def get_type_name(self) -> str:
        return "vec<%s>" % self._item_type.get_type_name()
    
    def get_type_descr(self) -> str:
        return "[Список] %s" % self._item_type.get_type_descr()

    def test_repr(self, value) -> bool:
        return super().test_repr(value)

    def to_string(self, value) -> str:
        return ";".join(map(lambda x: self._item_type.to_string(x), value))

    def from_string(self, value: str):
        values = []
        for item in re.split("\s*;\s*", value):
            values.append(self._item_type.from_string(item))
        return values
    
    def get_grid_renderer(self) -> GridCellRenderer:
        self.GRID_CELL_STRING_RENDERER.IncRef()
        return self.GRID_CELL_STRING_RENDERER

    def get_grid_editor(self) -> GridCellEditor:
        self.GRID_CELL_STRING_EDITOR.IncRef()
        return self.GRID_CELL_STRING_EDITOR
    
    def __eq__(self, o):
        return isinstance(o, VecCellType)