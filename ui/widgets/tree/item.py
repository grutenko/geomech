import wx

from typing import Protocol, List, Tuple

class TreeNode(Protocol):
    def get_parent(self) -> 'TreeNode':
        raise NotImplementedError("Method get_parent() not implemented.")
    def get_name(self) -> str:
        raise NotImplementedError("Method get_name() not implemented.")
    def is_name_bold(self) -> bool:
        return False
    def is_name_italic(self) -> bool:
        return False
    def get_icon(self) -> Tuple[str, wx.Bitmap] | None:
        return None
    def get_icon_open(self) -> Tuple[str, wx.Bitmap] | None:
        return None
    def get_subnodes(self) -> List['TreeNode']:
        return []
    def is_leaf(self) -> bool:
        return False
    def __eq__(self, o):
        raise NotImplementedError("Method __eq__() not implemented.")