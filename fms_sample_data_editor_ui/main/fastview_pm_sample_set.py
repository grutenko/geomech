import wx
import wx.propgrid
from pony.orm import db_session
from database import MineObject, Petrotype, PetrotypeStruct
from ui.datetimeutil import decode_date


class FastviewPmSampleSet(wx.propgrid.PropertyGrid):
    def __init__(self, parent):
        super().__init__(parent, style=wx.propgrid.PG_SPLITTER_AUTO_CENTER | wx.propgrid.PG_TOOLBAR)

        self.SetSplitterPosition(150)
        prop = self.Append(wx.propgrid.IntProperty("ID", "RID"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("Название", "Name"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.LongStringProperty("Комментарий", "Comment"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.BoolProperty("Реальные данные", "RealDetails"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("Месторождение", "Field"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.DateProperty("Дата отбора", "SetDate"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.DateProperty("Дата испытания", "TestDate"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("Петротип", "Petrotype"))
        self.SetPropertyReadOnly(prop)
        prop = self.Append(wx.propgrid.StringProperty("Структура петротипа", "PetrotypeStruct"))
        self.SetPropertyReadOnly(prop)

        self.Hide()

    @db_session
    def start(self, o):
        fields = {
            "RID": o.RID,
            "Name": o.Name,
            "Comment": o.Comment if o.Comment is not None else "",
            "RealDetails": o.RealDetails,
            "Field": MineObject[o.mine_object.RID].Name,
            "SetDate": decode_date(o.SetDate) if o.SetDate is not None else None,
            "TestDate": decode_date(o.TestDate) if o.TestDate is not None else None,
            "Petrotype": PetrotypeStruct[o.petrotype_struct.RID].petrotype.Name,
            "PetrotypeStruct": PetrotypeStruct[o.petrotype_struct.RID].Name,
        }
        self.SetPropertyValues(fields)
        self.Show()
