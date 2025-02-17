import wx
from ui.icon import get_icon
from ui.validators import TextValidator
from .dialog_properties import RockBurstDialogPropeties
from pony.orm import db_session, select
from database import MineObject, RockBurst, RBType


class RockBurstDialog(wx.Dialog):
    @db_session
    def __init__(self, parent):
        super().__init__(parent)
        self.SetIcon(wx.Icon(get_icon("logo")))
        self.SetTitle("Добавить горный удар")
        self.SetSize(400, 600)
        self.CenterOnScreen()

        sz = wx.BoxSizer(wx.VERTICAL)
        main_sz = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Месторождение")
        main_sz.Add(label, 0, wx.EXPAND)
        self.fields = []
        self.field_field = wx.Choice(self)
        for o in select(o for o in MineObject if o.Type == "FIELD"):
            self.field_field.Append(o.Name)
            self.fields.append(o)
        main_sz.Add(self.field_field, 0, wx.EXPAND | wx.BOTTOM, border=10)
        label = wx.StaticText(self, label="Тип")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_type = wx.Choice(self)
        self.types = []
        for o in select(o for o in RBType):
            self.field_type.Append(o.Name)
            self.types.append(o)
        main_sz.Add(self.field_type, 0, wx.EXPAND | wx.BOTTOM, border=10)
        label = wx.StaticText(self, label="Номер")
        main_sz.Add(label, 0, wx.EXPAND)
        self.field_number = wx.TextCtrl(self)
        self.field_number.SetValidator(TextValidator(lenMin=1, lenMax=255))
        main_sz.Add(self.field_number, 0, wx.EXPAND | wx.BOTTOM, border=10)
        self.field_dynamic = wx.CheckBox(self, label="Динамическое событие")
        main_sz.Add(self.field_dynamic, 0, wx.EXPAND | wx.BOTTOM, border=10)
        label = wx.StaticText(self, label="Основные свойства")
        main_sz.Add(label, 0, wx.EXPAND)
        self.properties = RockBurstDialogPropeties(self)
        main_sz.Add(self.properties, 1, wx.EXPAND)
        sz.Add(main_sz, 1, wx.EXPAND | wx.ALL, border=10)
        line = wx.StaticLine(self)
        sz.Add(line, 0, wx.EXPAND)
        btn_sz = wx.StdDialogButtonSizer()
        self.btn_save = wx.Button(self, label="Сохранить")
        btn_sz.Add(self.btn_save)
        sz.Add(btn_sz, 0, wx.EXPAND | wx.ALL, border=10)
        self.SetSizer(sz)
        self.Layout()
