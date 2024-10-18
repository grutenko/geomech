import wx
import wx.propgrid
from pony.orm import *

from database import CoordSystem

from .fastview_propgrid import FastviewPropgrid


class MineObjectFastview(FastviewPropgrid):
    def __init__(self, parent):
        super().__init__(parent)

        prop = self.Append(wx.propgrid.IntProperty("ID", "RID"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("Название", "Name"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.LongStringProperty("Комментарий", "Comment"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("Система координат", "coord_system"))
        self.SetPropertyReadOnly(prop)
        category = self.Append(wx.propgrid.PropertyCategory("Ограничения координат", "Coords"))
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("X Мин. (м)", "X_Min"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("Y Мин. (м)", "Y_Min"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("Z Мин. (м)", "Z_Min"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("X Макс. (м)", "X_Max"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("Y Макс. (м)", "Y_Max"))
        self.SetPropertyReadOnly(prop)
        prop = self.AppendIn(category, wx.propgrid.FloatProperty("Z Макс. (м)", "Z_Max"))
        self.SetPropertyReadOnly(prop)

        self.Layout()
        self.Hide()

    @db_session
    def start(self, o, bounds=None):
        _fields = {
            "RID": o.RID,
            "Name": o.Name,
            "Comment": o.Comment,
            "coord_system": CoordSystem[o.coord_system.RID].Name,
            "X_Min": o.X_Min,
            "Y_Min": o.Y_Min,
            "Z_Min": o.Z_Min,
            "X_Max": o.X_Max,
            "Y_Max": o.Y_Max,
            "Z_Max": o.Z_Max,
        }
        self.SetPropertyValues(_fields)
        self.Update()
        self.Show()

    def end(self):
        self.Hide()
