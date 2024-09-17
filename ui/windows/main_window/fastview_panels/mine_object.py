import wx
import wx.propgrid
from ..fastview_propgrid import FastviewPropgrid

from pony.orm import *
from database import CoordSystem


class MineObjectFastview(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(main_sizer)

        self.propgrid = FastviewPropgrid(self)
        prop = self.propgrid.Append(wx.propgrid.IntProperty("ID", "RID"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.Append(wx.propgrid.StringProperty("Название", "Name"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.Append(wx.propgrid.LongStringProperty("Комментарий", "Comment"))
        prop = self.propgrid.Append(
            wx.propgrid.StringProperty("Система координат", "coord_system")
        )
        self.propgrid.DisableProperty(prop)
        category = self.propgrid.Append(wx.propgrid.PropertyCategory("Ограничения координат", "Coords"))
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("X Мин.", "X_Min"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Y Мин.", "Y_Min"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Z Мин.", "Z_Min"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("X Макс.", "X_Max"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty( "Y Макс.", "Y_Max"))
        self.propgrid.DisableProperty(prop)
        prop = self.propgrid.AppendIn(category, wx.propgrid.FloatProperty("Z Макс.", "Z_Max"))
        self.propgrid.DisableProperty(prop)
        main_sizer.Add(self.propgrid, 1, wx.EXPAND)
        self.propgrid.SetSplitterPosition(200)

        self.Layout()
        self.Hide()

    @db_session
    def start(self, o, bounds=None):
        self.propgrid.SetPropertyValues({
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
        })
        self.Show()

    def end(self):
        self.Hide()