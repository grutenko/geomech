# _*_ coding: UTF8 _*_

import wx
from database import (
    DischargeSeries,
    session as dbsession
)
from typing import (
    List
)
import operator
from ui import Ui_DischargeMeasurement_Filter
import mixins
import query_dsl

class DischargeMeasurement_Filter(Ui_DischargeMeasurement_Filter, mixins.OptionalFieldsMixin):
    __filter_by: query_dsl.FilterBy

    __series: List[DischargeSeries];

    def __init__(self, filter_by: query_dsl.FilterBy = query_dsl.FilterBy(), *args, **kwds):
        super().__init__(*args, **kwds)
        mixins.OptionalFieldsMixin.__init__(self, self)
        self.__filter_by = filter_by

        self.__series = dbsession().query(DischargeSeries).all()
        self.field_DSID.Append('-- Не выбрано --')
        for seria in self.__series:
            self.field_DSID.Append(seria.Name)
        self.__set_fields()

    def __set_fields(self):
        dsid = self.__filter_by.find('DSID')
        if not dsid is None:
            for i, seria in enumerate(self.__series):
                if seria.RID == dsid.value:
                    self.field_DSID.Enable(True)
                    self.field_DSID_enabled.SetValue(True)
                    self.field_DSID.Select(i + 1)

        def _set(name, field):
            clause = self.__filter_by.find_by_name(name)
            if not clause is None:
                self.__dict__[field].Enable(True)
                self.__dict__[field].SetValue(clause.value)
                self.__dict__[field + '_enabled'].SetValue(True)

        _set('SNumber_min', 'field_SNumber_min')
        _set('SNumber_max', 'field_SNumber_max')
        _set('Diameter_min', 'field_Diameter_min')
        _set('Diameter_max', 'field_Diameter_max')
        _set('Length_min', 'field_Length_min')
        _set('Length_max', 'field_Length_max')
        _set('Weight_min', 'field_Weight_min')
        _set('Weight_max', 'field_Weight_max')

    def get_filter(self):
        filter_by = []
        _dsid_indx = self.field_DSID.GetSelection()
        if self.field_DSID.IsEnabled() and _dsid_indx > 0:
            filter_by.append(query_dsl.FilterClause('DSID', operator.eq, self.__series[_dsid_indx - 1].RID))

        def _set(field_name, operator, column, clause_name = None):
            if self.__dict__[field_name].IsEnabled():
                filter_by.append(query_dsl.FilterClause(column, operator, self.__dict__[field_name].GetValue(), name=clause_name))

        _set('field_SNumber_min', operator.ge, 'SNumber', 'SNumber_min')
        _set('field_SNumber_max', operator.le, 'SNumber', 'SNumber_max')
        _set('field_Diameter_min', operator.ge, 'Diameter', 'Diameter_min')
        _set('field_Diameter_max', operator.le, 'Diameter', 'Diameter_max')
        _set('field_Length_min', operator.ge, 'Length', 'Length_min')
        _set('field_Length_max', operator.le, 'Length', 'Length_max')
        _set('field_Weight_min', operator.ge, 'Weight', 'Weight_min')
        _set('field_Weight_max', operator.le, 'Weight', 'Weight_max')
        
        return query_dsl.FilterBy(filter_by)