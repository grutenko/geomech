import wx
from typing import List
from ui import (
    Ui_DischargeSeries_List,
    Ui_BoreHoles_List,
    Ui_OrigSampleSets_List
)
from xControlTableView import (
    xControlTableView,
    Column
)
from edit_windows import (
    DischargeSeriesEditor,
    OrigSampleSets_Editor
)
from database import (
    DischargeSeries,
    BoreHole,
    OrigSampleSet,
    MineObject,
    get_session
)
import query_dsl as dsl
from util import commit_changes

def _deletion_dialog(whats: str):
    msg = "Вы  действительно хотите удалить {0}? Это действие необратимо.".format(str(whats))
    dial = wx.MessageDialog(None, msg, 'Подтвердите удаление', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
    return dial.ShowModal()

class DischargeSeries_List(Ui_DischargeSeries_List):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        def _date_modifier(date):
            return str(date)[0:4] + '.' + str(date)[4:6] + '.' + str(date)[6:8]

        available_cols = [
            Column('RID', 'id'),
            Column('OSSID', 'Исходный набор образцов', modifier=lambda ossid: get_session().query(OrigSampleSet).get(ossid).Name),
            Column('Number', '№ серии замеров'),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий'),
            Column('MeasureDate', 'Дата замера', -1, _date_modifier)
        ]
        cols = [
            'RID', 'Number', 'Name', 'MeasureDate'
        ]
        order_by = dsl.OrderBy([
            dsl.OrderClause('MeasureDate', dsl.Direction.DESC)
        ])
        self.__list = xControlTableView[DischargeSeries](
            DischargeSeries,
            available_cols,
            cols,
            order_by,
            parent=self.panel_1,
            on_create=self.__on_create,
            on_edit=self.__on_edit,
            on_delete=self.__on_delete)
        self.list_container.Add(self.__list, wx.EXPAND)
        self.list_container.Layout()
        self.__list.Layout()

    def __on_create(self):
        def _on_save(e):
            self.__list.refresh()
            self.__list.select(e)
        editor = DischargeSeriesEditor(parent=self, on_save=_on_save)
        editor.Show()

    def __on_edit(self, e: DischargeSeries):
        def _on_save(e):
            self.__list.refresh()
            self.__list.select(e)
        editor = DischargeSeriesEditor(parent=self, entity=e, on_save=_on_save)
        editor.Show()

    def __on_delete(self, entities: List[DischargeSeries]):
        if len(entities) == 0:
            return
        ret = _deletion_dialog("серию " + entities[0].Name if len(entities) == 1 else "{0} обьектов".format(len(entities)))
        if ret == wx.ID_YES:
            for e in entities:
                get_session().delete(e)
            commit_changes(self)
            self.__list.refresh()

class BoreHoles_List(Ui_BoreHoles_List):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        def _date_modifier(date):
            return str(date)[0:4] + '.' + str(date)[4:6] + '.' + str(date)[6:8]

        available_cols = [
            Column('RID', 'id'),
            Column('Number', '№ серии замеров'),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий'),
            Column('SID', 'ID измерительной станции'),
            Column('MOID', 'ID горного обьекта'),
            Column('X', 'Коорд. X устья скважины'),
            Column('Y', 'Коорд. Y устья скважины'),
            Column('Z', 'Коорд. Z устья скважины'),
            Column('Azimuth', 'Азимут'),
            Column('Tilt', 'Наклон'),
            Column('Diameter', 'Диаметр'),
            Column('Length', 'Длина'),
            Column('StartDate', 'Дата закладки / начала измерений', -1, _date_modifier),
            Column('EndDate', 'Дата завершения измерений', -1, _date_modifier)
        ]
        cols = [
            'RID', 'Number', 'Name', 'X', 'Y', 'Z', 'StartDate'
        ]
        order_by = dsl.OrderBy([
            dsl.OrderClause('StartDate', dsl.Direction.DESC)
        ])
        self.__list = xControlTableView[BoreHole](
            BoreHole,
            available_cols,
            cols,
            order_by,
            parent=self.panel_1,
            on_create=self.__on_create,
            on_edit=self.__on_edit,
            on_delete=self.__on_delete)
        self.list_container.Add(self.__list, wx.EXPAND)
        self.list_container.Layout()
        self.__list.Layout()

    def __on_create(self):
        '''def _on_save(e):
            self.__list.refresh()
            self.__list.select(e)
        editor = DischargeSeriesEditor(parent=self, on_save=_on_save)
        editor.Show()'''

    def __on_edit(self, e: DischargeSeries):
        '''def _on_save(e):
            self.__list.refresh()
            self.__list.select(e)
        editor = DischargeSeriesEditor(parent=self, entity=e, on_save=_on_save)
        editor.Show()'''

    def __on_delete(self, entities: List[DischargeSeries]):
        if len(entities) == 0:
            return
        ret = _deletion_dialog("скважину " + entities[0].Name if len(entities) == 1 else "{0} обьектов".format(len(entities)))
        if ret == wx.ID_YES:
            for e in entities:
                get_session().delete(e)
            commit_changes(self)
            self.__list.refresh()

class OrigSampleSets_List(Ui_OrigSampleSets_List):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        def _date_modifier(date):
            return str(date)[0:4] + '.' + str(date)[4:6] + '.' + str(date)[6:8]
        
        def _sample_type_modifier(type):
            match type:
                case 'CORE': return 'Керн'
                case 'STUFF': return 'Штуф'
                case 'DISPERCE': return 'Дисперсный материал'

        available_cols = [
            Column('RID', 'id'),
            Column('Number', '№ серии замеров'),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий'),
            Column('SampleType', 'Тип материала образцов', -1, _sample_type_modifier),
            Column('MOID', 'Горный объект', modifier=lambda moid: get_session().query(MineObject).get(moid).Name),
            Column('HID', 'Скважина', modifier=lambda hid: get_session().query(BoreHole).get(hid).Name),
            Column('X', 'Коорд. X устья скважины'),
            Column('Y', 'Коорд. Y устья скважины'),
            Column('Z', 'Коорд. Z устья скважины'),
            Column('SetDate', 'Дата закладки / начала измерений', -1, _date_modifier),
        ]
        cols = [
            'RID', 'Number', 'Name', 'SampleType', 'X', 'Y', 'Z', 'SetDate'
        ]
        order_by = dsl.OrderBy([
            dsl.OrderClause('SetDate', dsl.Direction.DESC)
        ])
        self.__list = xControlTableView[OrigSampleSet](
            OrigSampleSet,
            available_cols,
            cols,
            order_by,
            parent=self.panel_1,
            on_create=self.__on_create,
            on_edit=self.__on_edit,
            on_delete=self.__on_delete)
        self.list_container.Add(self.__list, wx.EXPAND)
        self.list_container.Layout()
        self.__list.Layout()

    def __on_create(self):
        def _on_save(e):
            self.__list.refresh()
            self.__list.select(e)
        editor = OrigSampleSets_Editor(parent=self, on_save=_on_save)
        editor.Show()

    def __on_edit(self, e: DischargeSeries):
        def _on_save(e):
            self.__list.refresh()
            self.__list.select(e)
        editor = OrigSampleSets_Editor(parent=self, entity=e, on_save=_on_save)
        editor.Show()

    def __on_delete(self, entities: List[DischargeSeries]):
        if len(entities) == 0:
            return
        ret = _deletion_dialog("оригинальный набор образцов " + entities[0].Name if len(entities) == 1 else "{0} обьектов".format(len(entities)))
        if ret == wx.ID_YES:
            for e in entities:
                get_session().delete(e)
            commit_changes(self)
            self.__list.refresh()