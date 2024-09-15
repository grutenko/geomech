from typing import Protocol
from wx.grid import GridCellRenderer, GridCellEditor


class CellType(Protocol):
    __typname__: str
    __typdescr__: str

    def test_repr(self, value) -> bool:
        """
        Return true is str repr of value is valid for this type
        """
        ...

    def to_string(self, value) -> str:
        '''
        Get string repr of value for this type
        '''
        raise NotImplementedError("Method into_string() not implemented.")

    def from_string(self, value: str):
        '''
        Get original repr of string value for this type
        '''
        raise NotImplementedError("Method from_string() not implemented.")

    def get_grid_renderer(self) -> GridCellRenderer:
        """
        Return renderer for this type
        """
        raise NotImplementedError(
            "Method get_grid_renderer() not implemented.")

    def get_grid_editor(self) -> GridCellEditor:
        """
        Return editor for this type
        """
        raise NotImplementedError("Method get_grid_editor() not implemented.")
    
    def open_editor(self, value: str) -> str:
        """
        Open dialog editor and return str repr of old value or none if edition canceled
        """
        return None