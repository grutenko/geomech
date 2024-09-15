
from typing import Text
import wx
import re


class Validator(wx.Validator):
    msg: str

    def __init__(self, msg: str = None):
        super().__init__()
        self.msg = msg

    def Validate(self, parent): ...


class TextValidator(Validator):
    lenMin: int
    lenMax: int
    pattern: str

    def __init__(self, msg: str = None, lenMin=None, lenMax=None, pattern=None):
        super().__init__(msg)
        self.lenMin = lenMin
        self.lenMax = lenMax
        self.pattern = pattern

    def Validate(self, ctrl: wx.TextCtrl):
        ok = True
        if not ctrl.IsEnabled():
            return True
        if self.lenMin != None:
            ok = ok and len(ctrl.GetValue()) >= self.lenMin
        if self.lenMax != None:
            ok = ok and len(ctrl.GetValue()) <= self.lenMax
        if self.pattern != None:
            ok = ok and re.match(self.pattern, ctrl.GetValue())
        if not ok:
            ctrl.SetBackgroundColour("red")
            ctrl.Refresh()
        else:
            ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            ctrl.Refresh()
        return ok

    def TransferFromWindow(self):
        return True

    def TransferToWindow(self):
        return True

    def Clone(self):
        c = TextValidator()
        c.__dict__.update(self.__dict__)
        return c
