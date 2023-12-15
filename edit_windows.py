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
from datetime import datetime
from ui import (
    Ui_DischargeMeasurement_Editor,
    Ui_DischargeSeries_Editor,
    Ui_OrigSampleSets_Editor,
    Ui_Stations_Editor,
    Ui_MineObjects_Editor
)
import sqlalchemy
from database import (
    get_session,
    DischargeMeasurement,
    DischargeSeries,
    OrigSampleSet,
    MineObject,
    BoreHole,
    Station,
    gen_name_path,
    dry_commit_changes
)
import mixins
from form_validators import *
from sqlalchemy import func

from database import Base

def _db_error_msg(e):
    dlg=wx.MessageDialog(None, "Ошибка: " + str(e.orig if hasattr(e, 'orig') else e), str(type(e)), wx.OK|wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

class DischargeMeasurementEditor(Ui_DischargeMeasurement_Editor, mixins.OptionalFieldsMixin):
    _entity: DischargeMeasurement
    _series: Dict[int, DischargeSeries] = {}

    def __init__(self,
                 *args,
                 entity: DischargeMeasurement = None,
                 on_save: Callable[[Base], None] = None,
                 **kwds) -> None:
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)

        self.__set_series()

        self._on_save = on_save
        self._entity = entity
        if not entity is None:
            self._set_fields(entity)
        self.__init_validator()

        self.button_Cancel.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.button_Save.Bind(wx.EVT_BUTTON, self.__on_save_click)
        self.btn_addSeries.Bind(wx.EVT_BUTTON, self.__on_add_series_click)
        self.field_DSID.Bind(wx.EVT_CHOICE, self.__on_change_seria)
        self.Bind(wx.EVT_CLOSE, self.__on_close)

    def __on_change_seria(self, event):
        item = event.GetEventObject().GetSelection()
        if item == 0 or item == wx.NOT_FOUND or not item in self._series:
            return
        
        max = (get_session().query(func.max(DischargeMeasurement.SNumber))
         .filter_by(DSID = self._series[item].RID)
         .first())
        self.field_SNumber.SetValue(max[0] + 1 if max[0] != None else 1)

    __new_series = None

    def __on_add_series_click(self, event):
        def _on_add_series(entity):
            item = self.field_DSID.Append('[+] ' + entity.Name, -1)
            self._series[item] = entity
            self.field_DSID.Select(item)
            self.btn_addSeries.Enable(False)
            self.__new_series = entity

        editor = DischargeSeriesEditor(parent=self, on_save=_on_add_series)
        editor.Show()

    def __set_series(self):
        self.field_DSID.Clear()
        self.field_DSID.Append(u'-- Не выбрано --')
        for e in get_session().query(DischargeSeries).all():
            item = self.field_DSID.Append(e.Name, e.RID)
            self._series[item] = e

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
            get_session().add(self._entity)
            dry_commit_changes()
            if not self._on_save is None:
                self._on_save(self._entity)
            self.Close()
        except sqlalchemy.exc.SQLAlchemyError as e:
            _db_error_msg(e)
        finally:
            self.Enable(True)

    def __init_validator(self):
        def _set(field, validator):
            self.__dict__[field].SetValidator(validator)

        _set('field_DSID', ChoiceValidator())
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
            elif t == wx.Choice:
                for item, seria in self._series.items():
                        if seria.RID == value.RID:
                            self.__dict__[field].Select(item)
                            break
            if field + '_enabled' in self.__dict__:
                self.__dict__[field].Enable(True)
                self.__dict__[field + '_enabled'].SetValue(True)

        _set('field_RID', entity.RID)
        _set('field_DSID', entity.discharge_series)
        self.field_DSID.Enable(False)
        self.btn_addSeries.Enable(False)
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
            e.discharge_series = self._series[self.field_DSID.GetSelection()]
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
    _oss: Dict[int, OrigSampleSet]  = {}
    _entity: DischargeSeries = None
    _on_save = None

    __new_orig_sample_set = None

    def __init__(self, 
                 entity: DischargeSeries = None,
                 on_save: Callable[[DischargeSeries], None] = None,
                 *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)

        self._entity = entity
        self._on_save = on_save

        self.__set_orig_sample_set()

        if not entity is None:
            self._entity = entity
            self.__set_fields(entity)

        self.button_CANCEL.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)
        self.btn_add_orig_sample_set.Bind(wx.EVT_BUTTON, self.__on_add_orig_sample_set)

        self.__init_validator()

    def __set_orig_sample_set(self):
        self.field_OSSID.Clear()
        self.field_OSSID.Append('-- Не выбрано --')
        for e in get_session().query(OrigSampleSet).all():
            item = self.field_OSSID.Append(e.Name, e.RID)
            self._oss[item] = e

    def __on_cancel_click(self, event):
        self.Close()

    def __on_save_click(self, event):
        if not self.Validate():
            return
        self._entity = self.__write_entity(DischargeSeries() if self._entity == None else self._entity)
        self.Enable(False)
        try:
            get_session().add(self._entity)
            dry_commit_changes()
            if not self._on_save is None:
                self._on_save(self._entity)
            self.Close()
        except sqlalchemy.exc.SQLAlchemyError as e:
            _db_error_msg(e)
        finally:
            self.Enable(True)

    def __write_entity(self, e: DischargeSeries) -> DischargeSeries:
        e.Number = self.field_Number.GetValue()
        e.Name = self.field_Name.GetValue()
        e.Comment = self.field_Comment.GetValue() if self.field_Comment.IsEnabled() else None
        e.orig_sample_set = self._oss[self.field_OSSID.GetSelection()]
        date: wx.DateTime = self.field_MeasureDate.GetValue()
        date = str(date.GetYear()) + "{:02d}".format(date.GetMonth() + 1) + "{:02d}".format(date.GetDay()) + "000000"
        e.MeasureDate = date

        return e

    def __init_validator(self):
        def _set(field, validator):
            self.__dict__[field].SetValidator(validator)

        _set('field_Number', TextValidator(len_min=1, len_max=255))
        _set('field_Name', TextValidator(len_min=1, len_max=255))
        _set('field_Comment', TextValidator(len_min=1, len_max=255))
        _set('field_OSSID', ChoiceValidator())
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
        for i, oss in self._oss.items():
            if oss.RID == e.OSSID:
                self.field_OSSID.Select(i)
                break
        self.field_OSSID.Enable(False)
        try:
            date = datetime(
                int(str(e.MeasureDate)[0:4]),
                int(str(e.MeasureDate)[4:6]),
                int(str(e.MeasureDate)[6:8]))
        except ValueError:
            wx.MessageBox("Невалидная дата!", "Ошибка!")
            date = datetime.now()
        self.field_MeasureDate.SetValue(date)

    def __on_add_orig_sample_set(self, event):
        def _on_save(e):
            self.__set_orig_sample_set()
            item = self.field_OSSID.Append('[+] ' + e.Name)
            self._oss[item] = e
            self.field_OSSID.Select(item)
        w = OrigSampleSets_Editor(on_save=_on_save, parent=self)
        w.Show()

class OrigSampleSets_Editor(Ui_OrigSampleSets_Editor, mixins.OptionalFieldsMixin):
    __mine_objects: List[MineObject] = []
    __bore_holes: List[BoreHole] = []
    __entity: OrigSampleSet = None
    __on_save: Callable[[OrigSampleSet], None] = None

    def __init__(self,
                 entity: OrigSampleSet = None,
                 on_save: Callable[[OrigSampleSet], None] = None, *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)

        self.__entity = entity
        self.__on_save = on_save

        self.__load_mine_objects()
        self.__set_mine_objects()
        self.__bore_holes = get_session().query(BoreHole).all()
        for bh in self.__bore_holes:
            self.field_HID.Append(bh.Name)

        if not self.__entity is None:
            self.__set_fields()


        self.__init_validator()

        self.button_CANCEL.Bind(wx.EVT_BUTTON, self.__on_cancel_click)
        self.button_SAVE.Bind(wx.EVT_BUTTON, self.__on_save_click)
        self.btn_add_mine_object.Bind(wx.EVT_BUTTON, self.__on_add_mine_object)

    def __load_mine_objects(self):
        def _load_r(parent):
            if parent is None:
                objects = get_session().query(MineObject).where(MineObject.Level == 0).all()
            else:
                objects = parent.childrens
            for o in objects:
                self.__mine_objects.append(o)
                _load_r(o)
        _load_r(None)

    def __set_mine_objects(self):
        self.field_MOID.Clear()
        for e in self.__mine_objects:
            self.field_MOID.Append(gen_name_path(e, 'parent'))

    def __on_add_mine_object(self, event):
        def _on_save(e):
            index = self.__mine_objects.index(e) + 1 if e.parent != None else 0
            self.__mine_objects.insert(index, e)
            self.__set_mine_objects()
        w = MineObjects_Editor(on_save=_on_save, parent=self)
        w.Show()

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
        self.field_HID.Select(self.__bore_holes.index(e.bore_hole) + 1)
        self.field_HID.Enable(False)
        self.field_MOID.Select(self.__mine_objects.index(e.mine_object) + 1)
        self.field_MOID.Enable(False)
        try:
            date = datetime(
                int(str(e.SetDate)[0:4]),
                int(str(e.SetDate)[4:6]),
                int(str(e.SetDate)[6:8]))
        except ValueError:
            wx.MessageBox("Невалидная дата!", "Ошибка!")
            date = datetime.now()
        self.field_SetDate.SetValue(date)

    def __init_validator(self):
        def _set(field, validator):
            self.__dict__[field].SetValidator(validator)

        _set('field_Number', TextValidator(len_min=1, len_max=255))
        _set('field_Name', TextValidator(len_min=1, len_max=255))
        _set('field_Comment', TextValidator(len_min=1, len_max=255))
        _set('field_HID', ChoiceValidator())
        _set('field_MOID', ChoiceValidator())
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
            get_session().add(self.__entity)
            dry_commit_changes()
            if not self.__on_save is None:
                self.__on_save(self.__entity)
            self.Close()
        except sqlalchemy.exc.SQLAlchemyError as e:
            _db_error_msg(e)
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
        e.bore_hole = self.__bore_holes[self.field_HID.GetSelection() - 1]
        e.mine_object = self.__mine_objects[self.field_MOID.GetSelection() - 1]
        date: wx.DateTime = self.field_SetDate.GetValue()
        date = str(date.GetYear()) + "{:02d}".format(date.GetMonth() + 1) + "{:02d}".format(date.GetDay()) + "000000"
        e.SetDate = date

        return e
    
class StationsEditor(Ui_Stations_Editor, mixins.OptionalFieldsMixin):
    __entity: Station
    __on_save: Callable[[Station], None]
    __mine_objects: List[MineObject]

    def __init__(self, entity: OrigSampleSet = None,
                 on_save: Callable[[OrigSampleSet], None] = None, *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)

        self.__entity = entity
        self.__on_save = on_save

        def _set_mine_objects_R(parent: MineObject = None, parent_str = ''):
            if parent is None:
                objects = get_session().query(MineObject).where(MineObject.Level == 0).all()
            else:
                objects = parent.childrens
            for o in objects:
                self.__mine_objects.append(o)
                self.field_MOID.Append(parent_str + o.Name)
                _set_mine_objects_R(o, parent_str + o.Name + ' / ')

        self.__mine_objects = []
        _set_mine_objects_R()

        if not self.__entity is None:
            self.__set_fields()

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
        self.field_MOID.Select(self.__mine_objects.index(e.mine_object) + 1)
        self.field_MOID.Enable(False)
        self.button_Moid_Add.Enable(False)
        self.field_HoleCount.SetValue(e.HoleCount)
        try:
            date = datetime(
                int(str(e.StartDate)[0:4]),
                int(str(e.StartDate)[4:6]),
                int(str(e.StartDate)[6:8]))
        except ValueError:
            wx.MessageBox("Невалидная дата!", "Ошибка!")
            date = datetime.now()
        self.field_StartDate.SetValue(date)
        if e.EndDate != None:
            try:
                date = datetime(
                    int(str(e.StartDate)[0:4]),
                    int(str(e.StartDate)[4:6]),
                    int(str(e.StartDate)[6:8]))
            except ValueError:
                wx.MessageBox("Невалидная дата!", "Ошибка!")
                date = datetime.now()
            self.field_EndDate.SetValue(date)
            self.field_EndDate.Enable(True)
            self.field_EndDate_enabled.SetValue(True)

    def __on_save_click(self, event):
        if not self.Validate():
            return
        self.__entity = self.__write_entity(Station() if self.__entity == None else self.__entity)
        self.Enable(False)
        try:
            dry_commit_changes()
        except sqlalchemy.exc.SQLAlchemyError as e:
            _db_error_msg(e)
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
        e.mine_object = self.__mine_objects[self.field_MOID.GetSelection() - 1]
        e.HoleCount = self.field_HoleCount.GetValue()
        date: wx.DateTime = self.field_StartDate.GetValue()
        date = str(date.GetYear()) + "{:02d}".format(date.GetMonth() + 1) + "{:02d}".format(date.GetDay()) + "000000"
        e.StartDate = date
        if self.field_EndDate.IsEnabled():
            date: wx.DateTime = self.field_EndDate.GetValue()
            date = str(date.GetYear()) + "{:02d}".format(date.GetMonth() + 1) + "{:02d}".format(date.GetDay()) + "000000"
            e.EndDate = date

        return e

    def __on_cancel_click(self, event):
        self.Close()

    def __init_validator(self):
        def _set(field, validator):
            self.__dict__[field].SetValidator(validator)

        _set('field_Number', TextValidator(len_min=1, len_max=255))
        _set('field_Name', TextValidator(len_min=1, len_max=255))
        _set('field_Comment', TextValidator(len_min=1, len_max=255))
        _set('field_MOID', ChoiceValidator())
        _set('field_X', NumericValidator())
        _set('field_Y', NumericValidator())
        _set('field_Z', NumericValidator())
        _set('field_HoleCount', NumericValidator())
        _set('field_StartDate', DateValidator(max=wx.DateTime.Now()))
        _set('field_EndDate', DateValidator())

class MineObjects_Editor(Ui_MineObjects_Editor, mixins.OptionalFieldsMixin):
    def __init__(self, entity: MineObject = None, on_save: Callable[[MineObject], None] = None, *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)