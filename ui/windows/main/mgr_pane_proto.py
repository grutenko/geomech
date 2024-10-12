import wx
from typing import Protocol, runtime_checkable


@runtime_checkable
class MgrPaneProto(Protocol):
    def get_pane_info(self) -> str | None:
        """
        Должен вернуть строку с сохраненными данными для этой панели
        Либо None если данных нет
        """
        ...

    def save_pane_info(self, info: str):
        """
        Сохраняет текущие параметры панели
        """
        ...
