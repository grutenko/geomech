import wx

import numpy as np

from pony.orm import *
from database import CoordSystem
from .ui import Ui_CsTransl
from ui.icon import get_icon


@db_session
def _getCoordSystems(rootSystem=None):
    if rootSystem:
        childs = (
            select(cs for cs in CoordSystem if cs.parent == rootSystem)
        )
    else:
        childs = select(cs for cs in CoordSystem if cs.Level == 0)
    coordSystems = []
    for child in childs:
        coordSystems.append(child)
        coordSystems += _getCoordSystems(child)
    return coordSystems


class CsTransl(Ui_CsTransl):
    def __init__(self, parent):
        super().__init__(parent, size=wx.Size(250, 350))
        self.SetIcon(wx.Icon(get_icon("logo@16")))

        self.Bind(wx.EVT_CLOSE, self._onClose)

        self._coordSystems = _getCoordSystems()

        for index, coordSystem in enumerate(self._coordSystems):
            self.choce_from.Append(
                (" . " * coordSystem.Level) + coordSystem.Name, coordSystem
            )
        for index, coordSystem in enumerate(self._coordSystems):
            self.choice_to.Append(
                (" . " * coordSystem.Level) + coordSystem.Name, coordSystem
            )
        if len(self._coordSystems) > 0:
            self.field_X_from.Enable()
            self.field_Y_from.Enable()
            self.field_X_to.Enable()
            self.field_Y_to.Enable()
            self.choce_from.Select(0)
            self.choice_to.Select(0)

        self.btn_calc.Bind(wx.EVT_BUTTON, self._on_calc)

        self.SetSize(250, 350)
        self.Center()
        self.Layout()

    def _on_calc(self, event):
        self._calc()

    def _coord_transf(self, X, mat):
        X1 = np.array(X)
        X_out = np.array(X1).reshape(2, 1)
        X_out = np.vstack((X_out, 1))
        return np.dot(mat, X_out)[:-1].reshape(2)

    def _calc(self):
        cs_from: CoordSystem = self._coordSystems[self.choce_from.GetSelection()]
        cs_to: CoordSystem = self._coordSystems[self.choice_to.GetSelection()]
        if cs_from.Level > cs_to.Level:
            # переводим координаты в систему координат родителя
            # предполагаем что у всех рудничных систем один родитель и нет потомков
            mat = np.array(
                [
                    [cs_from.X_X, cs_from.X_Y, cs_from.X_Z],
                    [cs_from.Y_X, cs_from.Y_Y, cs_from.Y_Z],
                    [cs_from.Z_X, cs_from.Z_Y, cs_from.Z_Z],
                ]
            )
            a = self._coord_transf(
                np.array([self.field_X_from.GetValue(), self.field_Y_from.GetValue()]),
                mat,
            )
            self.field_X_to.SetValue(a[0])
            self.field_Y_to.SetValue(a[1])
        elif cs_from.Level < cs_to.Level:
            # переводим из глобальной в локальную систему координат
            mat = np.array(
                [
                    [cs_to.X_X, cs_to.X_Y, cs_to.X_Z],
                    [cs_to.Y_X, cs_to.Y_Y, cs_to.Y_Z],
                    [cs_to.Z_X, cs_to.Z_Y, cs_to.Z_Z],
                ]
            )
            mat = np.linalg.inv(mat)
            coords = np.array(
                [self.field_X_from.GetValue(), self.field_Y_from.GetValue(), 1]
            )
            a = np.dot(mat, coords)[:-1]
            self.field_X_to.SetValue(a[0])
            self.field_Y_to.SetValue(a[1])
        elif cs_from.Level == cs_to.Level:
            if cs_from == cs_to:
                self.field_X_to.SetValue(self.field_X_from.GetValue())
                self.field_Y_to.SetValue(self.field_Y_from.GetValue())
            else:
                # сначала переводим координаты в глобальную систему координат, потом в локальную систему cs_to
                mat = np.array(
                    [
                        [cs_from.X_X, cs_from.X_Y, cs_from.X_Z],
                        [cs_from.Y_X, cs_from.Y_Y, cs_from.Y_Z],
                        [cs_from.Z_X, cs_from.Z_Y, cs_from.Z_Z],
                    ]
                )
                a = self._coord_transf(
                    np.array(
                        [self.field_X_from.GetValue(), self.field_Y_from.GetValue()]
                    ),
                    mat,
                )
                mat = np.array(
                    [
                        [cs_to.X_X, cs_to.X_Y, cs_to.X_Z],
                        [cs_to.Y_X, cs_to.Y_Y, cs_to.Y_Z],
                        [cs_to.Z_X, cs_to.Z_Y, cs_to.Z_Z],
                    ]
                )
                mat = np.linalg.inv(mat)
                coords = np.append(a, 1)
                a = np.dot(mat, coords)[:-1]
                self.field_X_to.SetValue(a[0])
                self.field_Y_to.SetValue(a[1])

    def _onClose(self, event):
        self.Hide()