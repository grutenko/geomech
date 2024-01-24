# _*_ coding: UTF8 _*_

from typing import (
    Dict,
    Optional,
    Callable,
    List
)
import wx
import wx.adv
import re
import datetime
from ui import (
    Ui_DischargeMeasurement_Editor,
    Ui_DischargeSeries_Editor,
    Ui_OrigSampleSets_Editor,
    Ui_Stations_Editor,
    Ui_MineObjects_Editor,
    Ui_BoreHole_Editor
)
import sqlalchemy
from database import (
    session as dbsession,
    DischargeMeasurement,
    DischargeSeries,
    OrigSampleSet,
    MineObject,
    BoreHole,
    Station,
    CoordSystem,
)
import widgets.relation_selector
import mixins
from form_validators import *
from sqlalchemy import func

from database import Base, commit_all, dry_commit_all

def _db_error_msg(e):
    dlg=wx.MessageDialog(None, "Ошибка: " + str(e.orig if hasattr(e, 'orig') else e), str(type(e)), wx.OK|wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

class DischargeMeasurementEditor(Ui_DischargeMeasurement_Editor, mixins.OptionalFieldsMixin):
    _entity: DischargeMeasurement

    def __init__(self,
                 *args,
                 entity: DischargeMeasurement = None,
                 on_save: Callable[[Base], None] = None,
                 **kwds) -> None:
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)

        self._on_save = on_save
        self._entity = entity
        self.__init_validator()

        (self.field_DSID
         .set_table_class(DischargeSeries)
         .set_name_generator(lambda e: e.Name)
         .set_can_create(True)
         .set_editor(DischargeSeriesEditor))
        
        if entity != None:
            self._set_fields(entity)

        self.button_Cancel.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.button_Save.Bind(wx.EVT_BUTTON, self.__on_save_click)
        self.field_DSID.Bind(widgets.relation_selector.EVT_RELATION_SELECTOR_SELECT, self.__on_change_seria)
        self.Bind(wx.EVT_CLOSE, self.__on_close)

    def __on_change_seria(self, event):
        if event.is_new:
            return
        
        max = (dbsession().query(func.max(DischargeMeasurement.SNumber))
         .filter_by(DSID = event.entity.RID)
         .first())
        self.field_SNumber.SetValue(max[0] + 1 if max[0] != None else 1)

    def __on_close(self, event):
        event.Skip()

    def __on_cancel_click(self, event):
        self.Close()

    def __on_save_click(self, event):
        if not self.Validate():
            return
        self._entity = self.__write_entity(DischargeMeasurement() if self._entity == None else self._entity)
        self.Enable(False)
        try:
            dbsession().add(self._entity)
            dry_commit_all()
            if not self._on_save is None:
                self._on_save(self._entity)
            self.Close()
        
        finally:
            self.Enable(True)

    def __init_validator(self):
        def _set(field, validator):
            self.__dict__[field].SetValidator(validator)

        _set('field_DSID', RelationSelectorValidator())
        _set('field_DschNumber', TextValidator(len_min=1, len_max=255))
        _set('field_CoreNumber', TextValidator(len_min=1, len_max=255))
        _set('field_CartNumber', TextValidator(len_min=1, len_max=255))
        _set('field_PartNumber', TextValidator(len_min=1, len_max=255))
        _set('field_RockType', TextValidator(len_min=1, len_max=255))
        _set('field_SNumber', NumericValidator(is_positive=True))
        _set('field_Diameter', NumericValidator(is_positive=True))
        _set('field_Length', NumericValidator(is_positive=True))
        _set('field_Weight', NumericValidator(is_positive=True))
        _set('field_CoreDepth', NumericValidator(is_positive=True))
        _set('field_R1', NumericValidator(is_positive=True))
        _set('field_R2', NumericValidator(is_positive=True))
        _set('field_R3', NumericValidator(is_positive=True))
        _set('field_R4', NumericValidator(is_positive=True))
        _set('field_RComp', NumericValidator(is_positive=True))
        _set('field_Sensitivity', NumericValidator(is_positive=True))
        _set('field_TP_1_1', NumericValidator(is_positive=True))
        _set('field_TP_1_2', NumericValidator(is_positive=True))
        _set('field_TP_2_1', NumericValidator(is_positive=True))
        _set('field_TP_2_2', NumericValidator(is_positive=True))
        _set('field_TR_1', NumericValidator(is_positive=True))
        _set('field_TR_2', NumericValidator(is_positive=True))
        _set('field_TS_1', NumericValidator(is_positive=True))
        _set('field_TS_2', NumericValidator(is_positive=True))
        _set('field_PuassonStatic', NumericValidator(is_positive=True, max=1))
        _set('field_YungStatic', NumericValidator(is_positive=True))
        _set('field_E1', NumericValidator())
        _set('field_E2', NumericValidator())
        _set('field_E3', NumericValidator())
        _set('field_E4', NumericValidator())
        _set('field_Rotate', NumericValidator(min=-180, max=180, message="Значение: -180 >= a >= 180"))

    def _set_fields(self, entity: DischargeMeasurement):
        def _set(field, value):
            if value == None:
                return

            t = type(self.__dict__[field])
            if t == wx.StaticText:
                self.__dict__[field].SetLabelText(str(value))
            elif t == wx.SpinCtrl or t == wx.SpinCtrlDouble:
                self.__dict__[field].SetValue(value)
            elif t == wx.TextCtrl:
                self.__dict__[field].SetValue(value)
            elif t == widgets.relation_selector.RelationSelector:
                self.__dict__[field].select(value)

            if field + '_enabled' in self.__dict__:
                self.__dict__[field].Enable(True)
                self.__dict__[field + '_enabled'].SetValue(True)

        _set('field_RID', entity.RID)
        _set('field_DSID', entity.discharge_series)
        self.field_DSID.Enable(False)
        _set('field_SNumber', entity.SNumber)
        _set('field_DschNumber', entity.DschNumber)
        _set('field_CoreNumber', entity.CoreNumber)
        _set('field_Diameter', entity.Diameter)
        _set('field_Length', entity.Length)
        _set('field_Weight', entity.Weight)
        _set('field_CoreDepth', entity.CoreDepth)
        _set('field_CartNumber', entity.CartNumber)
        _set('field_PartNumber', entity.PartNumber)
        _set('field_R1', entity.R1)
        _set('field_R2', entity.R2)
        _set('field_R3', entity.R3)
        _set('field_R4', entity.R4)
        _set('field_RComp', entity.RComp)
        _set('field_Sensitivity', entity.Sensitivity)
        _set('field_TP_1_1', entity.TP1_1)
        _set('field_TP_1_2', entity.TP1_2)
        _set('field_TP_2_1', entity.TP2_1)
        _set('field_TP_2_2', entity.TP2_2)
        _set('field_TR_1', entity.TR_1)
        _set('field_TR_2', entity.TR_2)
        _set('field_TS_1', entity.TS_1)
        _set('field_TS_2', entity.TS_2)
        _set("field_PuassonStatic", entity.PuassonStatic)
        _set("field_YungStatic", entity.YungStatic)
        _set("field_E1", entity.E1)
        _set("field_E2", entity.E2)
        _set("field_E3", entity.E3)
        _set("field_E4", entity.E4)
        _set("field_Rotate", entity.Rotate)
        _set("field_RockType", entity.RockType)

    def __write_entity(self, e: DischargeMeasurement) -> DischargeMeasurement:
        if self.field_DSID.IsEnabled():
            e.discharge_series = self.field_DSID.get_selected_entity()
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

        return e

class DischargeSeriesEditor(Ui_DischargeSeries_Editor, mixins.OptionalFieldsMixin):
    _entity: DischargeSeries = None
    _on_save = None

    def __init__(self, 
                 entity: DischargeSeries = None,
                 on_save: Callable[[DischargeSeries], None] = None,
                 *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)

        self._entity = entity
        self._on_save = on_save

        (self.field_OSSID
         .set_table_class(OrigSampleSet)
         .set_name_generator(lambda e: e.Name)
         .set_can_create(True)
         .set_editor(OrigSampleSets_Editor))

        if not entity is None:
            self._entity = entity
            self.__set_fields(entity)

        self.button_CANCEL.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)

        self.__init_validator()

    def __on_cancel_click(self, event):
        self.Close()

    def __on_save_click(self, event):
        if not self.Validate():
            return
        self._entity = self.__write_entity(DischargeSeries() if self._entity == None else self._entity)
        self.Enable(False)
        try:
            dbsession().add(self._entity)
            dry_commit_all()
            if not self._on_save is None:
                self._on_save(self._entity)
            self.Close()
        
        finally:
            self.Enable(True)

    def __write_entity(self, e: DischargeSeries) -> DischargeSeries:
        e.Number = self.field_Number.GetValue()
        e.Name = self.field_Name.GetValue()
        e.Comment = self.field_Comment.GetValue() if self.field_Comment.IsEnabled() else None
        e.orig_sample_set = self.field_OSSID.get_selected_entity()
        date: wx.DateTime = self.field_MeasureDate.GetValue()
        e.MeasureDate =  datetime.date(date.GetYear(), date.GetMonth() + 1, date.GetDay())

        return e

    def __init_validator(self):
        def _set(field, validator):
            self.__dict__[field].SetValidator(validator)

        _set('field_Number', TextValidator(len_min=1, len_max=255))
        _set('field_Name', TextValidator(len_min=1, len_max=255))
        _set('field_Comment', TextValidator(len_min=1, len_max=255))
        _set('field_OSSID', RelationSelectorValidator())
        _set('field_MeasureDate', DateValidator(max=wx.DateTime.Now()))

    def __set_fields(self, entity: DischargeSeries):
        e = entity
        self.field_RID.SetLabelText(str(e.RID))
        self.field_Number.SetValue(e.Number)
        self.field_Name.SetValue(e.Name)
        if e.Comment != None:
            self.field_Comment.Enable(True)
            self.field_Comment.SetValue(e.Comment)
            self.field_Comment_enabled.SetValue(True)
        self.field_OSSID.select(entity.orig_sample_set)
        self.field_OSSID.Enable(False)
        self.field_MeasureDate.SetValue(e.MeasureDate)

class OrigSampleSets_Editor(Ui_OrigSampleSets_Editor, mixins.OptionalFieldsMixin):
    __entity: OrigSampleSet = None
    __on_save: Callable[[OrigSampleSet], None] = None

    def __init__(self,
                 entity: OrigSampleSet = None,
                 on_save: Callable[[OrigSampleSet], None] = None, *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)

        self.__entity = entity
        self.__on_save = on_save

        (self.field_MOID
         .set_table_class(MineObject)
         .set_name_generator(lambda e: e.Comment)
         .set_can_create(True)
         .set_editor(MineObjects_Editor))
        
        (self.field_HID
         .set_table_class(BoreHole)
         .set_name_generator(lambda e: e.Name)
         .set_can_create(True)
         .set_editor(BoreHole_Editor))

        if not self.__entity is None:
            self.__set_fields()

        if entity == None:
            self.supplied_data.Enable(False)
        else:
            self.supplied_data.set_data_owner(entity)

        self.__init_validator()

        self.button_CANCEL.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)

    def __set_fields(self):
        e = self.__entity
        self.field_RID.SetLabelText(str(e.RID))
        self.field_Number.SetValue(e.Number)
        self.field_Name.SetValue(e.Name)
        if e.Comment != None:
            self.field_Comment.Enable(True)
            self.field_Comment.SetValue(e.Comment)
            self.field_Comment_enabled.SetValue(True)
        if e.SampleType == 'CORE':
            self.field_SampleType.Select(0)
        elif e.SampleType == 'STUFF':
            self.field_SampleType.Select(1)
        elif e.SampleType == 'DISPERCE':
            self.field_SampleType.Select(2)
        self.field_X.SetValue(e.X)
        self.field_Y.SetValue(e.Y)
        self.field_Z.SetValue(e.Z)
        self.field_HID.select(e.bore_hole)
        self.field_HID.Enable(False)
        self.field_MOID.select(e.mine_object)
        self.field_MOID.Enable(False)
        self.field_SetDate.SetValue(e.SetDate)

    def __init_validator(self):
        def _set(field, validator):
            self.__dict__[field].SetValidator(validator)

        _set('field_Number', TextValidator(len_min=1, len_max=255))
        _set('field_Name', TextValidator(len_min=1, len_max=255))
        _set('field_Comment', TextValidator(len_min=1, len_max=255))
        _set('field_HID', RelationSelectorValidator())
        _set('field_MOID', RelationSelectorValidator())
        _set('field_SetDate', DateValidator(max=wx.DateTime.Now()))
        _set('field_X', NumericValidator())
        _set('field_Y', NumericValidator())
        _set('field_Z', NumericValidator())

    def __on_cancel_click(self, event):
        self.Close()

    def __on_save_click(self, event):
        if not self.Validate():
            return
        self.__entity = self.__write_entity(OrigSampleSet() if self.__entity == None else self.__entity)
        self.Enable(False)
        try:
            dbsession().add(self.__entity)
            dry_commit_all()
            if not self.__on_save is None:
                self.__on_save(self.__entity)
            self.Close()
        
        finally:
            self.Enable(True)

    def __write_entity(self, e: OrigSampleSet) -> OrigSampleSet:
        e.Number = self.field_Number.GetValue()
        e.Name = self.field_Name.GetValue()
        e.Comment = self.field_Comment.GetValue() if self.field_Comment.IsEnabled() else None
        e.X = self.field_X.GetValue()
        e.Y = self.field_Y.GetValue()
        e.Z = self.field_Z.GetValue()
        s = self.field_SampleType.GetSelection()
        if s == 0:
            e.SampleType = 'CORE'
        elif s == 1:
            e.SampleType = 'STUFF'
        elif s == 2:
            e.SampleType = 'DISPERCE'
        e.bore_hole = self.field_HID.get_selected_entity()
        e.mine_object = self.field_MOID.get_selected_entity()
        date: wx.DateTime = self.field_SetDate.GetValue()
        e.SetDate =  datetime.date(date.GetYear(), date.GetMonth() + 1, date.GetDay())

        return e
    
class StationsEditor(Ui_Stations_Editor, mixins.OptionalFieldsMixin):
    __entity: Station
    __on_save: Callable[[Station], None]

    def __init__(self, entity: OrigSampleSet = None,
                 on_save: Callable[[OrigSampleSet], None] = None, *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)

        self.__entity = entity
        self.__on_save = on_save

        (self.field_MOID
         .set_table_class(MineObject)
         .set_name_generator(lambda e: e.Comment)
         .set_can_create(True)
         .set_editor(MineObjects_Editor))

        if not self.__entity is None:
            self.__set_fields()

        if entity == None:
            self.supplied_data.Enable(False)
        else:
            self.supplied_data.set_data_owner(entity)

        self.__init_validator()

        self.button_CANCEL.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)

    def __set_fields(self):
        e = self.__entity
        self.field_RID.SetLabelText(str(e.RID))
        self.field_Number.SetValue(e.Number)
        self.field_Name.SetValue(e.Name)
        if e.Comment != None:
            self.field_Comment.SetValue(e.Comment)
            self.field_Comment.Enable(True)
            self.field_Comment_enabled.SetValue(True)
        self.field_X.SetValue(e.X)
        self.field_Y.SetValue(e.Y)
        self.field_Z.SetValue(e.Z)
        self.field_MOID.select(e.mine_object)
        self.field_MOID.Enable(False)
        self.field_HoleCount.SetValue(e.HoleCount)
        self.field_StartDate.SetValue(e.StartDate)
        if e.EndDate != None:
            self.field_EndDate.SetValue(e.EndDate)
            self.field_EndDate.Enable(True)
            self.field_EndDate_enabled.SetValue(True)

    def __on_save_click(self, event):
        if not self.Validate():
            return
        self.__entity = self.__write_entity(Station() if self.__entity == None else self.__entity)
        self.Enable(False)
        try:
            dry_commit_all()
        
        finally:
            self.Enable(True)
        if not self.__on_save is None:
            self.__on_save(self.__entity)
        self.Close()

    def __write_entity(self, e: Station) -> Station:
        e.Number = self.field_Number.GetValue()
        e.Name = self.field_Name.GetValue()
        if self.field_Comment.IsEnabled():
            e.Comment = self.field_Comment.GetValue()
        e.X = self.field_X.GetValue()
        e.Y = self.field_Y.GetValue()
        e.Z = self.field_Z.GetValue()
        e.mine_object = self.field_MOID.get_selected_entity()
        e.HoleCount = self.field_HoleCount.GetValue()
        date: wx.DateTime = self.field_StartDate.GetValue()
        e.StartDate =  datetime.date(date.GetYear(), date.GetMonth() + 1, date.GetDay())
        if self.field_EndDate.IsEnabled():
            date: wx.DateTime = self.field_EndDate.GetValue()
            e.EndDate =  datetime.date(date.GetYear(), date.GetMonth() + 1, date.GetDay())

        return e

    def __on_cancel_click(self, event):
        self.Close()

    def __init_validator(self):
        def _set(field, validator):
            self.__dict__[field].SetValidator(validator)

        _set('field_Number', TextValidator(len_min=1, len_max=255))
        _set('field_Name', TextValidator(len_min=1, len_max=255))
        _set('field_Comment', TextValidator(len_min=1, len_max=255))
        _set('field_MOID', RelationSelectorValidator())
        _set('field_X', NumericValidator())
        _set('field_Y', NumericValidator())
        _set('field_Z', NumericValidator())
        _set('field_HoleCount', NumericValidator())
        _set('field_StartDate', DateValidator(max=wx.DateTime.Now()))
        _set('field_EndDate', DateValidator())

class BoreHole_Editor(Ui_BoreHole_Editor, mixins.OptionalFieldsMixin):
    __entity: BoreHole = None
    __on_save: Callable[[BoreHole], None]

    def __init__(self, entity: BoreHole = None, on_save: Callable[[BoreHole], None] = None, *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)

        (self.field_MOID
         .set_table_class(MineObject)
         .set_name_generator(lambda e: e.Comment)
         .set_can_create(True)
         .set_editor(MineObjects_Editor))
        
        (self.field_SID
         .set_table_class(Station)
         .set_name_generator(lambda e: e.Name)
         .set_can_create(True)
         .set_editor(StationsEditor))
        
        self.__entity = entity
        self.__on_save = on_save
        if not self.__entity is None:
            self.__set_fields()

        if entity == None:
            self.supplied_data.Enable(False)
        else:
            self.supplied_data.set_data_owner(entity)

        self.__init_validator()

        self.button_CANCEL.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)

    def __init_validator(self):
        def _set(field, validator):
            self.__dict__[field].SetValidator(validator)

        _set('field_Number', TextValidator(len_min=1, len_max=255))
        _set('field_Name', TextValidator(len_min=1, len_max=255))
        _set('field_Comment', TextValidator(len_min=1, len_max=255))
        _set('field_MOID', RelationSelectorValidator())
        _set('field_X', NumericValidator())
        _set('field_Y', NumericValidator())
        _set('field_Z', NumericValidator())
        _set('field_Azimuth', NumericValidator())
        _set('field_Tilt', NumericValidator())
        _set('field_Diameter', NumericValidator())
        _set('field_Length', NumericValidator())
        _set('field_StartDate', DateValidator(max=wx.DateTime.Now()))
        _set('field_EndDate', DateValidator())

    def __set_fields(self):
        e = self.__entity
        self.field_RID.SetLabelText(str(e.RID))
        self.field_Number.SetValue(e.Number)
        self.field_Name.SetValue(e.Name)
        if e.Comment != None:
            self.field_Comment.SetValue(e.Comment)
            self.field_Comment.Enable(True)
            self.field_Comment_enabled.SetValue(True)
        self.field_X.SetValue(e.X)
        self.field_Y.SetValue(e.Y)
        self.field_Z.SetValue(e.Z)
        self.field_MOID.select(e.mine_object)
        self.field_MOID.Enable(False)
        if e.station != None:
            self.field_SID.select(e.station)
        self.field_SID.Enable(False)
        self.field_Azimuth.SetValue(e.Azimuth)
        self.field_Tilt.SetValue(e.Azimuth)
        self.field_Diameter.SetValue(e.Diameter)
        self.field_Length.SetValue(e.Length)
        self.field_StartDate.SetValue(e.StartDate)
        if e.EndDate != None:
            self.field_EndDate.SetValue(e.EndDate)
            self.field_EndDate.Enable(True)
            self.field_EndDate_enabled.SetValue(True)

    def __write_entity(self, e: BoreHole):
        e.Number = self.field_Number.GetValue()
        e.Name = self.field_Name.GetValue()
        if self.field_Comment.IsEnabled():
            e.Comment = self.field_Comment.GetValue()
        e.X = self.field_X.GetValue()
        e.Y = self.field_Y.GetValue()
        e.Z = self.field_Z.GetValue()
        e.mine_object = self.field_MOID.get_selected_entity()
        if self.field_SID.IsEnabled():
            e.station = self.field_SID.get_selected_entity()
        e.Azimuth = self.field_Azimuth.GetValue()
        e.Tilt = self.field_Tilt.GetValue()
        e.Diameter = self.field_Diameter.GetValue()
        e.Length = self.field_Length.GetValue()
        date: wx.DateTime = self.field_StartDate.GetValue()
        e.StartDate =  datetime.date(date.GetYear(), date.GetMonth() + 1, date.GetDay())
        if self.field_EndDate.IsEnabled():
            date: wx.DateTime = self.field_EndDate.GetValue()
            e.EndDate =  datetime.date(date.GetYear(), date.GetMonth() + 1, date.GetDay())
        return e

    def __on_save_click(self, event):
        if not self.Validate():
            return
        self.__entity = self.__write_entity(BoreHole() if self.__entity == None else self.__entity)
        self.Enable(False)
        try:
            dbsession().add(self.__entity)
            dry_commit_all()
        
        finally:
            self.Enable(True)
        if not self.__on_save is None:
            self.__on_save(self.__entity)
        self.Close()

    def __on_cancel_click(self, event):
        self.Close()

class MineObjects_Editor(Ui_MineObjects_Editor, mixins.OptionalFieldsMixin):
    __entity: MineObject
    __on_save: Callable[[MineObject], None]

    def __init__(self, entity: MineObject = None, on_save: Callable[[MineObject], None] = None, *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)

        (self.field_PID
         .set_table_class(MineObject)
         .set_name_generator(lambda e: e.Comment)
         .set_can_create(False))
        
        (self.field_CSID
         .set_table_class(CoordSystem)
         .set_name_generator(lambda e: e.Comment)
         .set_can_create(False))
        
        self.__entity = entity
        self.__on_save = on_save
        if not self.__entity is None:
            self.__set_fields()

        if entity == None:
            self.supplied_data.Enable(False)
        else:
            self.supplied_data.set_data_owner(entity)

        self.__init_validator()

        self.button_CANCEL.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)

    def __on_save_click(self, event):
        if not self.Validate():
            return
        self.__entity = self.__write_entity(MineObject() if self.__entity == None else self.__entity)
        self.Enable(False)
        try:
            dbsession().add(self.__entity)
            dry_commit_all()
        
        finally:
            self.Enable(True)
        if not self.__on_save is None:
            self.__on_save(self.__entity)
        self.Close()

    def __on_cancel_click(self, event):
        self.Close()

    def __init_validator(self):
        def _set(field, validator):
            self.__dict__[field].SetValidator(validator)

        _set('field_PID', RelationSelectorValidator())
        _set('field_Name', TextValidator(len_min=1, len_max=255))
        _set('field_Comment', TextValidator(len_min=1, len_max=255))
        _set('field_CSID', RelationSelectorValidator())
        _set('field_X_Min', NumericValidator())
        _set('field_Y_Min', NumericValidator())
        _set('field_Z_Min', NumericValidator())
        _set('field_X_Max', NumericValidator())
        _set('field_Y_Max', NumericValidator())
        _set('field_Z_Max', NumericValidator())

    def __set_fields(self):
        e = self.__entity
        self.field_RID.SetLabelText(str(e.RID))
        self.field_Name.SetValue(e.Name)
        if e.Comment != None:
            self.field_Comment.SetValue(e.Comment)
            self.field_Comment.Enable(True)
            self.field_Comment_enabled.SetValue(True)
        if e.parent != None:
            self.field_PID.select(e.parent)
            self.field_PID.Enable(True)
            self.field_PID_enabled.SetValue(True)
        self.field_PID_enabled.Enable(False)
        self.field_PID.Enable(False)
        self.field_CSID.select(e.coord_system)
        self.field_PID.Enable(False)
        if e.Type == 'REGION':
            self.field_Type.Select(0)
        elif e.Type == 'ROCKS':
            self.field_Type.Select(1)
        elif e.Type == 'FIELD':
            self.field_Type.Select(2)
        elif e.Type == 'HORIZON':
            self.field_Type.Select(3)
        elif e.Type == 'EXCAVATION':
            self.field_Type.Select(3)
        self.field_X_Min.SetValue(e.X_Min)
        self.field_Y_Min.SetValue(e.Y_Min)
        self.field_Z_Min.SetValue(e.Z_Min)
        self.field_X_Max.SetValue(e.X_Max)
        self.field_Y_Max.SetValue(e.Y_Max)
        self.field_Z_Max.SetValue(e.Z_Max)

    def __write_entity(self, e: MineObject):
        e.Name = self.field_Name.GetValue()
        e.Comment = self.field_Comment.GetValue() if self.field_Comment.IsEnabled() else None
        e.parent = self.field_PID.get_selected_entity()
        e.Level = e.parent.Level + 1 if e.parent != None else 0
        e.HCode = str(e.parent.RID).zfill(10) + '.' + str(e.parent.RID).zfill(19) if e.parent != None else '0000000000.0000000000000000000'
        e.coord_system = self.field_CSID.get_selected_entity()
        if self.field_Type.GetSelection() == 0:
            e.Type = 'REGION'
        elif self.field_Type.GetSelection() == 1:
            e.Type = 'ROCKS'
        elif self.field_Type.GetSelection() == 2:
            e.Type = 'FIELD'
        elif self.field_Type.GetSelection() == 3:
            e.Type = 'HORIZON'
        elif self.field_Type.GetSelection() == 4:
            e.Type = 'EXCAVATION'
        e.X_Min = self.field_X_Min.GetValue()
        e.Y_Min = self.field_X_Min.GetValue()
        e.Z_Min = self.field_X_Min.GetValue()
        e.X_Max = self.field_X_Max.GetValue()
        e.Y_Max = self.field_Y_Max.GetValue()
        e.Z_Max = self.field_Z_Max.GetValue()

        return e