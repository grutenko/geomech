from ui.custom_datetime import date, datetime

from wx.grid import (
    GridCellAutoWrapStringEditor,
    GridCellEditor,
    GridCellRenderer,
    GridCellStringRenderer,
)

from ui.widgets.grid.widget import CellType


class DateCellType(CellType):
    def __init__(self) -> None:
        super().__init__()

    def _test_repr_fmt0(self, value) -> bool:
        try:
            _date = datetime.strptime(value, "%d.%m.%Y")
        except:
            return False
        else:
            return True

    def _test_repr_fmt1(self, value) -> bool:
        try:
            _date = datetime.strptime(value, "%Y-%m-%d")
        except:
            return False
        else:
            return True

    def test_repr(self, value) -> bool:
        return self._test_repr_fmt0(value) or self._test_repr_fmt1(value)

    def to_string(self, value) -> str:
        _date = datetime(value.year, value.month, value.day)
        return _date.strftime("%d.%m.%Y")

    def from_string(self, value: str):
        try:
            _date = datetime.strptime(value, "%d.%m.%Y")
        except:
            _date = datetime.strptime(value, "%d-%m-%Y")
        _date = date(_date.year, _date.month, _date.day)
        return _date

    def get_type_name(self) -> str:
        return "date"

    def get_type_descr(self) -> str:
        return "Дата"

    def get_grid_renderer(self) -> GridCellRenderer:
        return GridCellStringRenderer()

    def get_grid_editor(self) -> GridCellEditor:
        return GridCellAutoWrapStringEditor()
