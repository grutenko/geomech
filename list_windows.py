import typing
import database
import query_dsl
import ui
import wx
import authority
import widgets.event
import widgets.table_view
import edit_windows
import settings
import inspect_windows
import filter_windows
from column import Column
from collections.abc import Sequence 

_T = typing.TypeVar('_T', bound=database.Base)

__all__ = [
    'cmd_show',
    'cmd_close'
]

class Base:
    def select(entities: typing.List[_T]):
        raise NotImplementedError("method select not implemented.")

def _do_delete(
        table: widgets.table_view.TableView,
        entites: typing.List[_T],
        parent,
        table_name: str = None,
        check_relations: typing.List[Column] = []):
    
    def _seq_but_not_str(obj):
        return isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray))
    
    def _check_relations() -> typing.List[str]:
        names = []
        for e in entites:
            for col in check_relations:
                _contain = True
                if _seq_but_not_str(getattr(e, col.name)):
                    _contain = _contain and len(getattr(e, col.name)) > 0
                else:
                    _contain = _contain and getattr(e, col.name) != None
                if _contain:
                    names.append(e.Name if 'Name' in e.__dict__ else e.RID)
        return names
    
    msg = "Вы  действительно хотите удалить {0}объектов? Это действие необратимо.".format(len(entites))
    dial = wx.MessageDialog(None, msg, 'Подтвердите удаление', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
    if dial.ShowModal() == wx.ID_YES:
        names = _check_relations()
        if len(names) > 0:
            raise Exception("Удаление невозможно так как для некоторых обхектов есть связаные данные.")
        for e in entites:
            database.session().delete(e)
        database.commit_all()
        table.reload()

def _do_edit(table: widgets.table_view.TableView, editor_class, parent, e = None):
    def _on_save(e):
        database.session().add(e)
        database.commit_all()
        table.reload()
    w = editor_class(entity=e, on_save=_on_save, parent=parent)
    w.Show()

class DischargeMeasurement_List(Base, ui.Ui_MainWindow):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.list.set_table_class(database.DischargeMeasurement)
        self.list.set_available_cols([
            Column('RID', 'Внутренний идентификатор замера', 50),
            Column('DSID', 'Серия замеров', 350, modifier=lambda e, dsid: e.discharge_series.Name),
            Column('SNumber', 'Порядковый номер замера.', 50),
            Column('DschNumber', 'Регистрационный номер разгрузки', 50),
            Column('CoreNumber', 'Регистрационный номер образца керна', 50),
            Column('Diameter', 'Диаметр образца керна', 50),
            Column('Length', 'Длина образца керна', 50),
            Column('Weight', 'Вес образца керна', 50),
            Column('CartNumber', 'Номер тензопатрона', 50),
            Column('PartNumber', 'Номер партии тензодатчиков', 50),
            Column('R1', 'Сопротивление тензорезистора R1', 50),
            Column('R2', 'Сопротивление тензорезистора R2', 50),
            Column('R3', 'Сопротивление тензорезистора R3', 50),
            Column('R4', 'Сопротивление тензорезистора R4', 50),
            Column('RComp', 'Сопротивление компенсационного резистора', 50),
            Column('Sensitivity', 'Коэффициент чувствительности тензодатчиков', 50),
            Column('TP1_1', 'Замер времени прохождения продольных волн (ультразвуковое профилирование или др.) - 1', 50),
            Column('TP1_2', 'Замер времени прохождения продольных волн (ультразвуковое профилирование или др.) - 2', 50),
            Column('TP2_1', 'Замер времени прохождения продольных волн (между торцами или др.) - 1', 50),
            Column('TP2_2', 'Замер времени прохождения продольных волн (между торцами или др.) - 2', 50),
            Column('TR_1', 'Замер времени прохождения поверхностных волн - 1', 50),
            Column('TR_2', 'Замер времени прохождения поверхностных волн - 2', 50),
            Column('TS_1', 'Замер времени прохождения поперечных волн - 1', 50),
            Column('TS_2', 'Замер времени прохождения поперечных волн - 2', 50),
            Column('PuassonStatic', 'Статический коэффициент Пуассона', 50),
            Column('YungStatic', 'Статический модуль Юнга', 50),
            Column('CoreDepth', 'Глубина взятия образца керна', 50),
            Column('E1', 'Относительная деформация образца - 1', 50),
            Column('E2', 'Относительная деформация образца - 2', 50),
            Column('E3', 'Относительная деформация образца - 3', 50),
            Column('E4', 'Относительная деформация образца - 4', 50),
            Column('Rotate', 'Угол коррекции направления напряжений', 50),
            Column('RockType', 'Тип породы', 500)
        ])
        self.list.set_display_cols([
            'DSID', 'SNumber', 'DschNumber', 'CoreNumber', 'CartNumber', 'PartNumber', 'Rotate', 'RockType'
        ], do_repaint=False)
        self.list.set_order_by(query_dsl.OrderBy([
            query_dsl.OrderClause('DSID', query_dsl.Direction.ASC),
            query_dsl.OrderClause('SNumber', query_dsl.Direction.ASC)
        ]), do_reload=False)
        self.list.reload()
        self.list.Bind(widgets.event.EVT_ENTITY_MANAGE_EVENT, self.__on_manage_entities)

    def __on_manage_entities(self, event):
        if event.type == widgets.event.ManageTypes.NEED_CREATE:
            _do_edit(self.list, edit_windows.DischargeMeasurementEditor, self, None)
        elif event.type == widgets.event.ManageTypes.NEED_EDIT:
            _do_edit(self.list, edit_windows.DischargeMeasurementEditor, self, event.entity)
        elif event.type == widgets.event.ManageTypes.NEED_DELETE:
            _do_delete(self.list, event.entities, self, "Поразгрузочные замеры")
        elif event.type == widgets.event.ManageTypes.NEED_SHOW_DETAIL:
            inspect_windows.cmd_show(event.entity)
        elif event.type == widgets.event.ManageTypes.NEED_FILTER:
            w = filter_windows.DischargeMeasurement_Filter(self.list.get_filter_by(), parent=self)
            ret = w.ShowModal()
            if ret == wx.ID_OK:
                self.list.set_filter_by(w.get_filter())

    def _on_show_stations(self, event):
        cmd_show(database.Station)

    def _on_show_discharge_series(self, event):
        cmd_show(database.DischargeSeries)

    def _on_show_orig_sample_sets(self, event):
        cmd_show(database.OrigSampleSet)

    def _on_show_bore_holes(self, event):
        cmd_show(database.BoreHole)

    def _on_show_coord_system(self, event):
        cmd_show(database.CoordSystem)

    def _on_show_mine_object(self, event):
        cmd_show(database.MineObject)

    def _on_show_settings(self, event):
        w = settings.Settings(parent=self)
        w.ShowModal()

    def select(self, entities: typing.List[_T]):
        self.list.select(entities)

class DischargeSeries_List(Base, ui.Ui_DischargeSeries_List):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.list.set_table_class(database.DischargeSeries)
        self.list.set_available_cols([
            Column('RID', 'id', 50),
            Column('OSSID', 'Исходный набор образцов', 350, modifier=lambda  e, _: e.orig_sample_set.Name),
            Column('Number', '№ серии замеров', 50),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий', 500),
            Column('MeasureDate', 'Дата замера', 250)
        ])
        self.list.set_display_cols(['RID', 'Number', 'Name', 'MeasureDate'], do_repaint=False)
        self.list.set_order_by(query_dsl.OrderBy([
            query_dsl.OrderClause('MeasureDate', query_dsl.Direction.DESC)
        ]), do_reload=False)
        self.list.reload()
        self.list.Bind(widgets.event.EVT_ENTITY_MANAGE_EVENT, self.__on_manage_entities)

    def __on_manage_entities(self, event):
        if event.type == widgets.event.ManageTypes.NEED_CREATE:
            _do_edit(self.list, edit_windows.DischargeSeriesEditor, self, None)
        elif event.type == widgets.event.ManageTypes.NEED_EDIT:
            _do_edit(self.list, edit_windows.DischargeSeriesEditor, self, event.entity)
        elif event.type == widgets.event.ManageTypes.NEED_DELETE:
            _do_delete(self.list, event.entities, self, "Серии замеров", [Column("discharge_measurements")])
        elif event.type == widgets.event.ManageTypes.NEED_SHOW_DETAIL:
            inspect_windows.cmd_show(event.entity)

    def select(self, entities: typing.List[_T]):
        self.list.select(entities)

class BoreHole_List(Base, ui.Ui_BoreHoles_List):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.list.set_table_class(database.BoreHole)
        self.list.set_available_cols([
            Column('RID', 'id', 50),
            Column('Number', '№ скважины', 350),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий', 500),
            Column('SID', 'Измерительная станция', 350, lambda e, _: e.station.Name),
            Column('MOID', 'Горный объект', 350, lambda e, _: e.mine_object.Name),
            Column('X', 'Коорд. X устья скважины', 50),
            Column('Y', 'Коорд. Y устья скважины', 50),
            Column('Z', 'Коорд. Z устья скважины', 50),
            Column('Azimuth', 'Азимут', 50),
            Column('Tilt', 'Наклон', 50),
            Column('Diameter', 'Диаметр', 50),
            Column('Length', 'Длина', 50),
            Column('StartDate', 'Дата закладки / начала измерений', 250),
            Column('EndDate', 'Дата завершения измерений', 250)
        ])
        self.list.set_display_cols([
            'RID', 'Number', 'Name', 'X', 'Y', 'Z', 'StartDate'
        ], do_repaint=False)
        self.list.set_order_by(query_dsl.OrderBy([
            query_dsl.OrderClause('StartDate', query_dsl.Direction.DESC)
        ]), do_reload=False)
        self.list.reload()
        self.list.Bind(widgets.event.EVT_ENTITY_MANAGE_EVENT, self.__on_manage_entities)

    def __on_manage_entities(self, event):
        if event.type == widgets.event.ManageTypes.NEED_CREATE:
            _do_edit(self.list, edit_windows.BoreHole_Editor, self, None)
        elif event.type == widgets.event.ManageTypes.NEED_EDIT:
            _do_edit(self.list, edit_windows.BoreHole_Editor, self, event.entity)
        elif event.type == widgets.event.ManageTypes.NEED_DELETE:
            _do_delete(self.list, event.entities, self, "Скважины")
        elif event.type == widgets.event.ManageTypes.NEED_SHOW_DETAIL:
            inspect_windows.cmd_show(event.entity)

    def select(self, entities: typing.List[_T]):
        self.list.select(entities)

class CoordSystem_List(Base, ui.Ui_CoordSystems_List):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.tree.set_table_class(database.CoordSystem)
        self.tree.set_child_field("childrens")
        self.tree.set_level_field("Level")
        self.tree.set_flags(authority.CAN_SORT|authority.CAN_FILTER)
        self.tree.reload()
        self.tree.Bind(widgets.event.EVT_ENTITY_MANAGE_EVENT, self.__on_manage_entities)

    def __on_manage_entities(self, event):
        if event.type == widgets.event.ManageTypes.NEED_SHOW_DETAIL:
            inspect_windows.cmd_show(event.entity)

    def select(self, entities: typing.List[_T]):
        if len(entities) > 0:
            self.tree.select(entities[0])

class MineObject_List(Base, ui.Ui_MineObjects_List):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.tree.set_table_class(database.MineObject)
        self.tree.set_child_field("childrens")
        self.tree.set_level_field("Level")
        self.tree.reload()
        self.tree.Bind(widgets.event.EVT_ENTITY_MANAGE_EVENT, self.__on_manage_entities)

    def __on_manage_entities(self, event):
        if event.type == widgets.event.ManageTypes.NEED_CREATE:
            _do_edit(self.tree, edit_windows.MineObjects_Editor, self, None)
        elif event.type == widgets.event.ManageTypes.NEED_EDIT:
            _do_edit(self.tree, edit_windows.MineObjects_Editor, self, event.entity)
        elif event.type == widgets.event.ManageTypes.NEED_DELETE:
            _do_delete(self.tree, event.entities, self, "Горные объекты")
        elif event.type == widgets.event.ManageTypes.NEED_SHOW_DETAIL:
            inspect_windows.cmd_show(event.entity)

    def select(self, entities: typing.List[_T]):
        if len(entities) > 0:
            self.tree.select(entities[0])

class OrigSampleSet_List(Base, ui.Ui_OrigSampleSets_List):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        
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
            
            return _gen_name_r(database.session().query(database.MineObject).get(moid), '')

        self.list.set_table_class(database.OrigSampleSet)
        self.list.set_available_cols([
            Column('RID', 'id', 50),
            Column('Number', '№ серии замеров', 350),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий', 500),
            Column('SampleType', 'Тип материала образцов', 150, _sample_type_modifier),
            Column('MOID', 'Горный объект', 350, modifier=_mine_object_modifier),
            Column('HID', 'Скважина', 350, modifier=lambda  e, _: e.bore_hole.Name if e.bore_hole != None else "<нет>"),
            Column('X', 'Коорд. X устья скважины', 50),
            Column('Y', 'Коорд. Y устья скважины', 50),
            Column('Z', 'Коорд. Z устья скважины', 50),
            Column('SetDate', 'Дата закладки / начала измерений', 350),
        ])
        self.list.set_display_cols([
            'RID', 'Number', 'Name', 'SampleType', 'X', 'Y', 'Z', 'SetDate'
        ], do_repaint=False)
        self.list.set_order_by(query_dsl.OrderBy([
            query_dsl.OrderClause('SetDate', query_dsl.Direction.DESC)
        ]), do_reload=False)
        self.list.reload()
        self.list.Bind(widgets.event.EVT_ENTITY_MANAGE_EVENT, self.__on_manage_entities)

    def __on_manage_entities(self, event):
        if event.type == widgets.event.ManageTypes.NEED_CREATE:
            _do_edit(self.list, edit_windows.OrigSampleSets_Editor, self, None)
        elif event.type == widgets.event.ManageTypes.NEED_EDIT:
            _do_edit(self.list, edit_windows.OrigSampleSets_Editor, self, event.entity)
        elif event.type == widgets.event.ManageTypes.NEED_DELETE:
            _do_delete(self.list, event.entities, self, "Наборы образцов", [Column('discharge_series')])
        elif event.type == widgets.event.ManageTypes.NEED_SHOW_DETAIL:
            inspect_windows.cmd_show(event.entity)

    def select(self, entities: typing.List[_T]):
        self.list.select(entities)

class Station_List(Base, ui.Ui_Stations_List):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.list.set_table_class(database.Station)
        self.list.set_available_cols([
            Column('RID', 'id', 50),
            Column('Number', '№ серии замеров', 350),
            Column('Name', 'Название', 500),
            Column('Comment', 'Комментарий', 500),
            Column('MOID', 'Горный объект', 350, modifier=lambda  e, _: e.mine_object.Name),
            Column('X', 'Коорд. X станции', 50),
            Column('Y', 'Коорд. Y станции', 50),
            Column('Z', 'Коорд. Z станции', 50),
            Column('HoleCount', 'Количество скважин', 50),
            Column('StartDate', 'Дата закладки / начала измерений', 250),
            Column('EndDate', 'Дата завершения измерений', 250),
        ])
        self.list.set_display_cols([
            'RID', 'Number', 'Name', 'X', 'Y', 'Z', 'StartDate'
        ], do_repaint=False)
        self.list.set_order_by(query_dsl.OrderBy([
            query_dsl.OrderClause('StartDate', query_dsl.Direction.DESC)
        ]), do_reload=False)
        self.list.reload()
        self.list.Bind(widgets.event.EVT_ENTITY_MANAGE_EVENT, self.__on_manage_entities)

    def __on_manage_entities(self, event):
        if event.type == widgets.event.ManageTypes.NEED_CREATE:
            _do_edit(self.list, edit_windows.StationsEditor, self, None)
        elif event.type == widgets.event.ManageTypes.NEED_EDIT:
            _do_edit(self.list, edit_windows.StationsEditor, self, event.entity)
        elif event.type == widgets.event.ManageTypes.NEED_DELETE:
            _do_delete(self.list, event.entities, self, "Станции")
        elif event.type == widgets.event.ManageTypes.NEED_SHOW_DETAIL:
            inspect_windows.cmd_show(event.entity)

    def select(self, entities: typing.List[_T]):
        self.list.select(entities)

__windows: typing.Dict[typing.Type[_T], Base] = {}

__MAPPING__ = {
    database.DischargeMeasurement: DischargeMeasurement_List,
    database.DischargeSeries: DischargeSeries_List,
    database.BoreHole: BoreHole_List,
    database.CoordSystem: CoordSystem_List,
    database.MineObject: MineObject_List,
    database.OrigSampleSet: OrigSampleSet_List,
    database.Station: Station_List,
}

def __check_class(table_class: typing.Type[_T]):
    if not issubclass(table_class, database.Base):
        raise Exception(table_class.__name__ + " is not a database model.")
    if not table_class in __MAPPING__:
        raise Exception("List window for " + table_class.__name__ + " not found.")

def cmd_show(table_class: typing.Type[_T], with_selection: typing.List[_T] = None) -> Base:
    __check_class(table_class)
    global __windows
    if table_class in __windows:
        __windows[table_class].Raise()
    else:
        parent = __windows[database.DischargeMeasurement] if database.DischargeMeasurement in __windows else None
        __windows[table_class] = __MAPPING__[table_class](parent=parent)
        __windows[table_class].Show()
        def _on_close(event):
            event.Skip()
            del __windows[table_class]
        __windows[table_class].Bind(wx.EVT_CLOSE, _on_close)
    if with_selection != None:
        __windows[table_class].select(with_selection)

    return __windows[table_class]

def cmd_close(table_class: typing.Type[_T]):
    __check_class(table_class)
    global __windows
    if table_class in __windows:
        __windows[table_class].Close()