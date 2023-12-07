# _*_ coding: UTF8 _*_

import wx
from typing import (
    List,
    Generic,
    TypeVar,
    Type,
    Union
)
from ui import (
    Ui_DischargeSeries_List,
    Ui_BoreHoles_List,
    Ui_OrigSampleSets_List,
    Ui_Stations_List,
    Ui_MineObjects_List,
    Ui_CoordSystems_List
)
from xTableView import (
    xTableView,
    Column
)
from xTreeView import xTreeView
from edit_windows import (
    DischargeSeriesEditor,
    OrigSampleSets_Editor,
    StationsEditor,
    MineObjects_Editor
)
from database import (
    DischargeSeries,
    BoreHole,
    OrigSampleSet,
    MineObject,
    Station,
    CoordSystem,
    Base,
    get_session,
    commit_changes
)
from sqlalchemy.inspection import inspect
from column import Column
import query_dsl as dsl
import authority

_T = TypeVar('_T', bound=Base)

class Base(Generic[_T]):
    def select(e: _T):
        raise NotImplementedError("method select not implemented.")

def _deletion_dialog(whats: str):
    msg = "Вы  действительно хотите удалить {0}? Это действие необратимо.".format(str(whats))
    dial = wx.MessageDialog(None, msg, 'Подтвердите удаление', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
    return dial.ShowModal()

class DischargeSeries_List(Ui_DischargeSeries_List, Base[DischargeSeries]):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        def _date_modifier(_, date):
            return str(date)[0:4] + '.' + str(date)[4:6] + '.' + str(date)[6:8]

        available_cols = [
            Column('RID', 'id', 50),
            Column('OSSID', 'Исходный набор образцов', 350, modifier=lambda e, ossid: e.orig_sample_set.Name),
            Column('Number', '№ серии замеров', 50),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий', 500),
            Column('MeasureDate', 'Дата замера', 250, _date_modifier)
        ]
        cols = [
            'RID', 'Number', 'Name', 'MeasureDate'
        ]
        order_by = dsl.OrderBy([
            dsl.OrderClause('MeasureDate', dsl.Direction.DESC)
        ])
        self.__list = xTableView[DischargeSeries](
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
            get_session().add(e)
            commit_changes(self)
            self.__list.refresh()
            self.__list.select(e)
        editor = DischargeSeriesEditor(parent=self, on_save=_on_save)
        editor.Show()

    def __on_edit(self, e: DischargeSeries):
        def _on_save(e):
            commit_changes(self)
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

    def select(self, e: DischargeSeries):
        self.__list.select(e)

class BoreHoles_List(Ui_BoreHoles_List, Base[BoreHole]):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        def _date_modifier(_, date):
            return str(date)[0:4] + '.' + str(date)[4:6] + '.' + str(date)[6:8]

        available_cols = [
            Column('RID', 'id', 50),
            Column('Number', '№ набора образцов', 350),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий', 500),
            Column('SID', 'ID измерительной станции', 50),
            Column('MOID', 'ID горного обьекта', 50),
            Column('X', 'Коорд. X устья скважины', 50),
            Column('Y', 'Коорд. Y устья скважины', 50),
            Column('Z', 'Коорд. Z устья скважины', 50),
            Column('Azimuth', 'Азимут', 50),
            Column('Tilt', 'Наклон', 50),
            Column('Diameter', 'Диаметр', 50),
            Column('Length', 'Длина', 50),
            Column('StartDate', 'Дата закладки / начала измерений', 250, _date_modifier),
            Column('EndDate', 'Дата завершения измерений', 250, _date_modifier)
        ]
        cols = [
            'RID', 'Number', 'Name', 'X', 'Y', 'Z', 'StartDate'
        ]
        order_by = dsl.OrderBy([
            dsl.OrderClause('StartDate', dsl.Direction.DESC)
        ])
        self.__list = xTableView[BoreHole](
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

    def select(self, e: BoreHole):
        self.__list.select(e)

class OrigSampleSets_List(Ui_OrigSampleSets_List, Base[OrigSampleSet]):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        def _date_modifier(_, date):
            return str(date)[0:4] + '.' + str(date)[4:6] + '.' + str(date)[6:8]
        
        def _sample_type_modifier(_, type):
            if type == 'CORE':
                return 'Керн'
            elif type == 'STUFF':
                return 'Штуф'
            elif type == 'DISPERCE':
                return 'Дисперсный материал'

        def _mine_object_modifier(_, moid):
            def _gen_name_r(o, acc):
                return _gen_name_r(o.parent, '/' + o.Name + acc) if not o.parent is None else o.Name + acc
            
            return _gen_name_r(get_session().query(MineObject).get(moid), '')

        available_cols = [
            Column('RID', 'id', 50),
            Column('Number', '№ серии замеров', 350),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий', 500),
            Column('SampleType', 'Тип материала образцов', 150, _sample_type_modifier),
            Column('MOID', 'Горный объект', 350, modifier=_mine_object_modifier),
            Column('HID', 'Скважина', 350, modifier=lambda hid: get_session().query(BoreHole).get(hid).Name),
            Column('X', 'Коорд. X устья скважины', 50),
            Column('Y', 'Коорд. Y устья скважины', 50),
            Column('Z', 'Коорд. Z устья скважины', 50),
            Column('SetDate', 'Дата закладки / начала измерений', 350, _date_modifier),
        ]
        cols = [
            'RID', 'Number', 'Name', 'SampleType', 'X', 'Y', 'Z', 'SetDate'
        ]
        order_by = dsl.OrderBy([
            dsl.OrderClause('SetDate', dsl.Direction.DESC)
        ])
        self.__list = xTableView[OrigSampleSet](
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
            get_session().add(e)
            commit_changes(self)
            self.__list.refresh()
            self.__list.select(e)
        editor = OrigSampleSets_Editor(parent=self, on_save=_on_save)
        editor.Show()

    def __on_edit(self, e: OrigSampleSet):
        def _on_save(e):
            commit_changes(self)
            self.__list.refresh()
            self.__list.select(e)
        editor = OrigSampleSets_Editor(parent=self, entity=e, on_save=_on_save)
        editor.Show()

    def __on_delete(self, entities: List[OrigSampleSet]):
        if len(entities) == 0:
            return
        ret = _deletion_dialog("оригинальный набор образцов " + entities[0].Name if len(entities) == 1 else "{0} обьектов".format(len(entities)))
        if ret == wx.ID_YES:
            for e in entities:
                get_session().delete(e)
            commit_changes(self)
            self.__list.refresh()

    def select(self, e: OrigSampleSet):
        self.__list.select(e)

class Stations_List(Ui_Stations_List, Base[Station]):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        def _date_modifier(_, date):
            return str(date)[0:4] + '.' + str(date)[4:6] + '.' + str(date)[6:8]

        available_cols = [
            Column('RID', 'id', 50),
            Column('Number', '№ серии замеров', 350),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий', 500),
            Column('MOID', 'Горный объект', 350, modifier=lambda e, moid: e.mine_object.Name),
            Column('X', 'Коорд. X станции', 50),
            Column('Y', 'Коорд. Y станции', 50),
            Column('Z', 'Коорд. Z станции', 50),
            Column('HoleCount', 'Количество скважин', 50),
            Column('StartDate', 'Дата закладки / начала измерений', 250, _date_modifier),
            Column('EndDate', 'Дата завершения измерений', 250, _date_modifier),
        ]
        cols = [
            'RID', 'Number', 'Name', 'X', 'Y', 'Z', 'StartDate'
        ]
        order_by = dsl.OrderBy([
            dsl.OrderClause('StartDate', dsl.Direction.DESC)
        ])
        self.__list = xTableView[Station](
            Station,
            available_cols,
            cols,
            order_by,
            on_create=self.__on_create,
            on_edit=self.__on_edit,
            on_delete=self.__on_delete,
            parent=self.panel_1)
        self.list_container.Add(self.__list, wx.EXPAND)
        self.list_container.Layout()
        self.__list.Layout()

    def select(self, e: Station):
        self.__list.select(e)

    def __on_create(self):
        def _on_save(e):
            get_session().add(e)
            commit_changes(self)
            self.__list.refresh()
            self.__list.select(e)
        editor = StationsEditor(parent=self, on_save=_on_save)
        editor.Show()

    def __on_edit(self, e: OrigSampleSet):
        def _on_save(e):
            commit_changes(self)
            self.__list.refresh()
            self.__list.select(e)
        editor = StationsEditor(parent=self, entity=e, on_save=_on_save)
        editor.Show()

    def __on_delete(self, entities: List[Station]):
        if len(entities) == 0:
            return
        ret = _deletion_dialog("Станция " + entities[0].Name if len(entities) == 1 else "{0} обьектов".format(len(entities)))
        if ret == wx.ID_YES:
            for e in entities:
                get_session().delete(e)
            commit_changes(self)
            self.__list.refresh()

class MineObjects_List(Ui_MineObjects_List, Base[MineObject]):
    __tree: xTreeView

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.__tree = xTreeView(
            MineObject,
            'Level',
            'childrens',
            on_create=self.__on_create,
            on_edit=self.__on_edit,
            on_delete=self.__on_delete,
            parent=self.panel_1)
        self.tree_container.Add(self.__tree, wx.EXPAND)
        self.tree_container.Layout()
        self.__tree.Layout()

    def select(self, e: MineObject):
        self.__tree.select(e)

    def __on_create(self, parent):
        w = MineObjects_Editor(parent=self)
        w.Show()

    def __on_edit(self, e):
        pass

    def __on_delete(self, entities: List[MineObject]):
        if len(entities) == 0:
            return
        ret = _deletion_dialog("Горный объект " + entities[0].Name if len(entities) == 1 else "{0} обьектов".format(len(entities)))
        if ret == wx.ID_YES:
            for e in entities:
                get_session().delete(e)
            commit_changes(self)
            self.__list.refresh()

class CoordSystems_List(Ui_CoordSystems_List, Base[CoordSystem]):
    __tree: xTreeView

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.__tree = xTreeView(
            CoordSystem,
            'Level',
            'childrens',
            flags=authority.CAN_FILTER|authority.CAN_SORT,
            on_create=self.__on_create,
            on_edit=self.__on_edit,
            on_delete=self.__on_delete,
            parent=self.panel_1)
        self.tree_container.Add(self.__tree, wx.EXPAND)
        self.tree_container.Layout()
        self.__tree.Layout()
        self.Layout()

    def select(self, e: CoordSystem):
        self.__tree.select(e)

    def __on_create(self, parent):
        pass

    def __on_edit(self, e):
        pass

    def __on_delete(self, entities: List[CoordSystem]):
        if len(entities) == 0:
            return
        ret = _deletion_dialog("Систему координат " + entities[0].Name if len(entities) == 1 else "{0} обьектов".format(len(entities)))
        if ret == wx.ID_YES:
            for e in entities:
                get_session().delete(e)
            commit_changes(self)
            self.__list.refresh()
