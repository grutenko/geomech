from typing import Dict
from Ui_DischargeMeasurement_Editor import Ui_DischargeMeasurement_Editor
import database as db
from database import (
    DischargeSeries,
    DischargeMeasurement
)
import wx
from pubsub import pub
import re

class _ValidatorBase(wx.Validator):
    def __init__(self):
        super().__init__()

    def TransferToWindow(self):
        return True
    
    def TransferFromWindow(self):
        return True

class TextNotEmptyValidator(_ValidatorBase):
    def Clone(self):
        return TextNotEmptyValidator()

    def Validate(self, parent):
        ctrl = self.GetWindow()
        text = ctrl.GetValue()

        if len(text) == 0:
            wx.MessageBox("Тектовое поле должно быть заполнено!", "Ошибка заполнения!")
            ctrl.SetBackgroundColour("red")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            ctrl.SetBackgroundColour(
                 wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            ctrl.Refresh()
            return True
        
class ChoiseSettedValidator(_ValidatorBase):
    def Clone(self):
        return ChoiseSettedValidator()
    
    def Validate(self, parent):
        ctrl: wx.Choice = self.GetWindow()
        if ctrl.GetSelection() == 0 or ctrl.GetSelection() == wx.NOT_FOUND:
            wx.MessageBox("Поле должно быть заполнено!", "Ошибка заполнения!")
            ctrl.SetBackgroundColour("red")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            ctrl.SetBackgroundColour(
                 wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            ctrl.Refresh()
            return True
        
class NumericGTZeroValidator(_ValidatorBase):
    def Clone(self):
        return NumericGTZeroValidator()
    
    def Validate(self, parent):
        ctrl: wx.SpinCtrl = self.GetWindow()
        if ctrl.IsEnabled() and ctrl.GetValue() <= 0:
            wx.MessageBox("Значение в поле должно быть больше 0", "Ошибка заполнения!")
            ctrl.SetBackgroundColour("red")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            ctrl.SetBackgroundColour(
                 wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            ctrl.Refresh()
            return True

class DischargeMeasurement_Editor(Ui_DischargeMeasurement_Editor):
    _series = {}
    _entity = None

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.button_CANCEL.Bind(wx.EVT_BUTTON, self._OnCancel)

        for item in db.session.query(DischargeSeries).all():
            self._series[item.RID] = self.field_DSID.Append(item.Name, item.RID)

        self.button_SAVE.Bind(wx.EVT_BUTTON, self._OnSave)

        _v = TextNotEmptyValidator()
        self.field_DschNumber.SetValidator(_v.Clone())
        self.field_CoreNumber.SetValidator(_v.Clone())
        self.field_CartNumber.SetValidator(_v.Clone())
        self.field_PartNumber.SetValidator(_v.Clone())
        self.field_RockType.SetValidator(_v.Clone())

        _v = ChoiseSettedValidator()
        self.field_DSID.SetValidator(_v.Clone())

        _v = NumericGTZeroValidator()
        self.field_SNumber.SetValidator(_v.Clone())
        self.field_Diameter.SetValidator(_v.Clone())
        self.field_Length.SetValidator(_v.Clone())
        self.field_Weight.SetValidator(_v.Clone())
        self.field_CoreDepth.SetValidator(_v.Clone())
        self.field_R1.SetValidator(_v.Clone())
        self.field_R2.SetValidator(_v.Clone())
        self.field_R3.SetValidator(_v.Clone())
        self.field_R4.SetValidator(_v.Clone())
        self.field_RComp.SetValidator(_v.Clone())
        self.field_Sensitivity.SetValidator(_v.Clone())
        self.field_TP_1_1.SetValidator(_v.Clone())
        self.field_TP_1_2.SetValidator(_v.Clone())
        self.field_TP_2_1.SetValidator(_v.Clone())
        self.field_TP_2_2.SetValidator(_v.Clone())
        self.field_TR_1.SetValidator(_v.Clone())
        self.field_TR_2.SetValidator(_v.Clone())
        self.field_TS_1.SetValidator(_v.Clone())
        self.field_TS_2.SetValidator(_v.Clone())
        self.field_PuassonStatic.SetValidator(_v.Clone())
        self.field_YungStatic.SetValidator(_v.Clone())
        self.field_E1.SetValidator(_v.Clone())
        self.field_E2.SetValidator(_v.Clone())
        self.field_E3.SetValidator(_v.Clone())
        self.field_E4.SetValidator(_v.Clone())
        self.field_Rotate.SetValidator(_v.Clone())

        self._InitOptionalFields()

    checkBoxFieldMapping: Dict[int, wx.Control] = {}

    def _InitOptionalFields(self):
        checkbox: wx.CheckBox
        for i, (key, checkbox) in enumerate(self.__dict__.items()):
            if re.match(r"field_(.+)_enabled", key):
                field = re.search(r"(.+)_enabled", key).group(1)
                if not field in self.__dict__:
                    raise Exception("Для чекбокса \"" + key + "\" нет соотвествующего поля.")
                self.checkBoxFieldMapping[checkbox.GetId()] = field
                checkbox.Bind(wx.EVT_CHECKBOX, self._OnToggleOptionalFieldCheckbox, id=checkbox.GetId())

    def _OnToggleOptionalFieldCheckbox(self, event: wx.Event):
        checkBox: wx.CheckBox = event.GetEventObject()
        if not checkBox.GetId() in self.checkBoxFieldMapping:
            return
        self.__dict__[ self.checkBoxFieldMapping[checkBox.GetId()] ].Enable( checkBox.IsChecked() )
                

    def SetEntity(self, entity: DischargeMeasurement):
        self._entity = entity
        self.field_RID.SetLabelText(str(entity.RID))
        if entity.DSID in self._series:
            self.field_DSID.Select(self._series[entity.DSID])
        self.field_DSID.Enable(False);
        self.field_SNumber.SetValue(entity.SNumber)
        self.field_DschNumber.SetValue(entity.DschNumber)
        self.field_CoreNumber.SetValue(entity.CoreNumber)
        self.field_Diameter.SetValue(entity.Diameter)
        self.field_Length.SetValue(entity.Length)
        self.field_Weight.SetValue(entity.Weight)
        self.field_CoreDepth.SetValue(entity.CoreDepth)
        self.field_CartNumber.SetValue(entity.CartNumber)
        self.field_PartNumber.SetValue(entity.PartNumber)
        self.field_R1.SetValue(entity.R1)
        self.field_R2.SetValue(entity.R2)
        self.field_R3.SetValue(entity.R3)
        self.field_R4.SetValue(entity.R4)
        self.field_RComp.SetValue(entity.RComp)
        self.field_Sensitivity.SetValue(entity.Sensitivity)

        def _set(field, value):
            if not value is None:
                self.__dict__[field].SetValue(value)
                self.__dict__[field].Enable(True)
                self.__dict__[field + '_enabled'].SetValue(True)

        _set("field_TP_1_1", entity.TP1_1)
        _set("field_TP_1_2", entity.TP1_2)
        _set("field_TP_2_1", entity.TP2_1)
        _set("field_TP_2_2", entity.TP2_2)
        _set("field_TR_1", entity.TR_1)
        _set("field_TR_2", entity.TR_2)
        _set("field_TS_1", entity.TS_1)
        _set("field_TS_2", entity.TS_2)
        _set("field_PuassonStatic", entity.PuassonStatic)
        _set("field_YungStatic", entity.YungStatic)

        self.field_E1.SetValue(entity.E1)
        self.field_E2.SetValue(entity.E2)
        self.field_E3.SetValue(entity.E3)
        self.field_E4.SetValue(entity.E4)
        self.field_Rotate.SetValue(entity.Rotate)
        self.field_RockType.SetValue(entity.RockType)

    def _OnSave(self, event):
        if not self.Validate():
            return

        e = DischargeMeasurement() if self._entity == None else self._entity

        series = db.session.query(DischargeSeries).get(self.field_DSID.GetSelection())
        e.dischange_series = series
        e.SNumber = self.field_SNumber.GetValue()
        e.DschNumber = self.field_DschNumber.GetValue()
        e.CoreNumber = self.field_CoreNumber.GetValue()
        e.Diameter = self.field_Diameter.GetValue()
        e.Length = self.field_Length.GetValue()
        e.Weight = self.field_Weight.GetValue()
        e.CoreDepth = self.field_CoreDepth.GetValue()
        e.CartNumber = self.field_CartNumber.GetValue()
        e.PartNumber = self.field_PartNumber.GetValue()
        e.R1 = self.field_R1.GetValue()
        e.R2 = self.field_R2.GetValue()
        e.R3 = self.field_R3.GetValue()
        e.R4 = self.field_R4.GetValue()
        e.RComp = self.field_RComp.GetValue()
        e.Sensitivity = self.field_Sensitivity.GetValue()

        def _set(prop, field):
            setattr(e, prop, field.GetValue() if field.IsEnabled() else None)

        _set('TP1_1', self.field_TP_1_1)
        _set('TP1_2', self.field_TP_1_2)
        _set('TP2_1', self.field_TP_2_1)
        _set('TP2_2', self.field_TP_2_2)
        _set('TR_1', self.field_TR_1)
        _set('TR_2', self.field_TR_2)
        _set('TS_1', self.field_TS_1)
        _set('TS_2', self.field_TS_2)
        _set('PuassonStatic', self.field_PuassonStatic)
        _set('YungStatic', self.field_YungStatic)

        e.E1 = self.field_E1.GetValue()
        e.E2 = self.field_E1.GetValue()
        e.E3 = self.field_E1.GetValue()
        e.E4 = self.field_E1.GetValue()
        e.Rotate = self.field_Rotate.GetValue()
        e.RockType = self.field_RockType.GetValue()

        if self._entity == None:
            db.session.add(e)

        db.session.flush()
        db.session.commit()
        pub.sendMessage("main.need_refresh")
        self.Close()

    def _OnCancel(self, event):
        self.Close()
