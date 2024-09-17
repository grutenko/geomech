from typing import Iterable
import wx

from ui.widgets.grid import *
from ui.widgets.grid.column import Column
from .base_grid import BaseGrid

class _Model(ModelProto):
    def get_columns(self) -> Iterable[Column]:
        return []
    
    def get_row_state(self, row: int):
        return None
    
    def get_value_at(self, col: int, row: int) -> str:
        return ''
    
    def total_rows(self) -> int:
        return 0

class DischargeMeasurementsEditor(BaseGrid):
    def __init__(self, parent):
        super().__init__(parent)
        self._model = _Model()
        self.start(self._model)