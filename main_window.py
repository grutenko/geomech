import wx
from typing import List
from database import (
    DischargeMeasurement,
    DischargeSeries,
    get_session
)
from ui import (
    Ui_MainWindow,
    Ui_DischargeMesurement_Inspect,
)
from edit_windows import (
    DischargeMeasurementEditor,
    OrigSampleSets_Editor,
    DischargeSeriesEditor
)
from filter_windows import DischargeMeasurement_Filter
from list_windows import (
    DischargeSeries_List,
    BoreHoles_List,
    OrigSampleSets_List,
    Stations_List,
    MineObjects_List,
    CoordSystems_List,
    Base
)
from xTableView import (
    xTableView,
    Column
)
from settings import Settings
from util import commit_changes
import query_dsl

def _deletion_dialog(whats: str):
    msg = "Вы  действительно хотите удалить {0}? Это действие необратимо.".format(str(whats))
    dial = wx.MessageDialog(None, msg, 'Подтвердите удаление', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
    return dial.ShowModal()

class _Inspect(Ui_DischargeMesurement_Inspect):
    __entity: DischargeMeasurement

    def __init__(self, entity: DischargeMeasurement, *args, **kwds):
        super().__init__(*args, **kwds)
        self.__entity = entity
        self.__set_fields()

    def __set_fields(self):
        self.field_RID.SetLabel(str(self.__entity.RID))
        self.field_DSID.SetLabel(self.__entity.dischange_series.Name)
        self.field_DSID.Wrap(300)
        self.field_SNumber.SetLabel(str(self.__entity.SNumber))
        self.field_DschNumber.SetLabel(str(self.__entity.DschNumber))
        self.field_CoreNumber.SetLabel(str(self.__entity.CoreNumber))
        self.field_Diameter.SetLabel(str(self.__entity.Diameter) + 'мм')
        self.field_Length_.SetLabel(str(self.__entity.Length) + 'мм')
        self.field_Weight.SetLabel(str(self.__entity.Weight) + 'г')
        self.field_CartNumber.SetLabel(str(self.__entity.CartNumber))
        self.field_PartNumber.SetLabel(str(self.__entity.CartNumber))
        self.field_CoreDepth.SetLabel(str(self.__entity.CoreDepth) + 'м')
        self.field_R.SetLabel('1) ' + str(self.__entity.R1) + 'Ом' + ', ' + '2) ' + str(self.__entity.R2) + 'Ом' + ', ' + '3) ' + str(self.__entity.R3) + 'Ом' + ', ' + '4) ' + str(self.__entity.R4) + 'Ом' + ', ')
        self.field_RComp.SetLabel(str(self.__entity.RComp))
        self.field_Sensitivity.SetLabel(str(self.__entity.Sensitivity))
        _tp1 = ""
        if not self.__entity.TP1_1 is None:
            _tp1 += "1)" + str(self.__entity.TP1_1) + "мс"
        if not self.__entity.TP1_2 is None:
            _tp1 += ", 2)" + str(self.__entity.TP1_2) + "мс"
        self.field_TP_1.SetLabel(_tp1)
        _tp2 = ""
        if not self.__entity.TP2_1 is None:
            _tp2 += "1)" + str(self.__entity.TP2_1) + "мс"
        if not self.__entity.TP2_2 is None:
            _tp2 += ", 2)" + str(self.__entity.TP2_2) + "мс"
        self.field_TP_2.SetLabel(_tp2)
        _tr = ""
        if not self.__entity.TR_1 is None:
            _tr += "1)" + str(self.__entity.TR_1) + "мс"
        if not self.__entity.TR_2 is None:
            _tr += ", 2)" + str(self.__entity.TR_2) + "мс"
        self.field_TR.SetLabel(_tr)
        _ts = ""
        if not self.__entity.TS_1 is None:
            _tr += "1)" + str(self.__entity.TS_1) + "мс"
        if not self.__entity.TS_2 is None:
            _tr += ", 2)" + str(self.__entity.TS_2) + "мс"
        self.field_TS.SetLabel(_ts)
        if not self.__entity.PuassonStatic is None:
            self.field_PuassonStatic.SetLabel(str(self.__entity.PuassonStatic))
        if not self.__entity.YungStatic is None:
            self.field_PuassonStatic.SetLabel(str(self.__entity.YungStatic))

class MainWindow(Ui_MainWindow, Base[DischargeMeasurement]):
    __list: xTableView
    __detail_entity: DischargeMeasurement = None
    __inspector: _Inspect = None

    _discharge_series_list: DischargeSeries_List = None
    _bore_holes_list: BoreHoles_List = None
    _orig_sample_sets_list: OrigSampleSets_List = None
    _stations_list: Stations_List = None
    _mine_objects_list: MineObjects_List = None
    _coord_systems_list: CoordSystems_List = None

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        available_cols = [
            Column('RID', 'Внутренний идентификатор замера', 50),
            Column('DSID', 'Серия замеров', 350, modifier=lambda dsid: get_session().query(DischargeSeries).get(dsid).Name),
            Column('SNumber', 'Порядковый номер замера.', 50),
            Column('DschNumber', 'Регистрационный номер разгрузки', 350),
            Column('CoreNumber', 'Регистрационный номер образца керна', 350),
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
            Column('RockType', 'Тип породы', 250)
        ]
        cols = [
            'SNumber', 'DschNumber', 'CoreNumber', 'CartNumber', 'PartNumber', 'R1', 'R2', 'R3', 'R4', 'RComp', 'Sensitivity'
        ]
        order_by = query_dsl.OrderBy([
            query_dsl.OrderClause('SNumber', query_dsl.Direction.DESC)
        ])
        self.__list = xTableView[DischargeMeasurement](
            DischargeMeasurement,
            available_cols,
            cols,
            order_by,
            filter_window=DischargeMeasurement_Filter,
            parent=self.window_1_pane_1,
            on_edit=self.__on_edit, 
            on_create=self.__on_create,
            on_delete=self.__on_delete,
            on_dbclick=self.__ondbclick,
            on_deselect=self.__ondeselect
        )
        self.list_container.Add(self.__list, wx.EXPAND)
        self.list_container.Layout()
        self.__list.Layout()

        self._discharge_series_list: DischargeSeries_List = None
        self._bore_holes_list: BoreHoles_List = None
        self._orig_sample_sets_list: OrigSampleSets_List = None
        self._stations_list: Stations_List = None
        self._mine_objects_list: MineObjects_List = None
        self._coord_systems_list: CoordSystems_List = None

    def __on_edit(self, e: DischargeMeasurement):
        editor = DischargeMeasurementEditor(parent=self, entity=e, on_save=lambda _: self.__list.refresh())
        editor.Show()

    def __on_create(self):
        def _on_save(e: DischargeMeasurement):
            self.__list.refresh()
            self.__list.select(e)
        editor = DischargeMeasurementEditor(parent=self, on_save=_on_save)
        editor.Show()

    def __on_delete(self, entities: List[DischargeMeasurement]):
        if len(entities) == 0:
            return
        ret = _deletion_dialog("замер №" + entities[0].DschNumber if len(entities) == 1 else "{0} обьектов".format(len(entities)))
        if ret == wx.ID_YES:
            for e in entities:
                get_session().delete(e)
            commit_changes(self)
            self.__list.refresh()
            self.__remove_details()

    def __ondbclick(self, e: DischargeMeasurement):
        if not self.__inspector is None:
            self.__remove_details()
        self.__detail_entity = e
        self.__inspector = _Inspect(entity=e, parent=self.window_1_pane_2)
        self.detail_container.Add(self.__inspector)
        self.window_1_pane_2.Layout()
        self.Layout()

    def __remove_details(self):
        if self.__detail_entity is None or self.__inspector is None:
            return
        self.detail_container.Detach(self.__inspector)
        self.__inspector.Destroy()
        self.__inspector = None
        self.__detail_entity = None

    def __ondeselect(self, e: DischargeMeasurement):
        if self.__detail_entity == e:
            self.__remove_details()

    def __open_list_window(self, property, class_name):
        if not self.__dict__[property] is None:
            self.__dict__[property].Raise()
        else:
            setattr(self, property, class_name(parent=self))
            def _on_close(e):
                self.__dict__[property].Destroy()
                self.__dict__[property] = None
            getattr(self, property).Bind(wx.EVT_CLOSE, _on_close)
            getattr(self, property).Show()

    def _on_show_discharge_series(self, event):
        self.__open_list_window('_discharge_series_list', DischargeSeries_List)

    def _on_show_bore_holes(self, event):
        self.__open_list_window('_bore_holes_list', BoreHoles_List)

    def _on_show_orig_sample_sets(self, event):
        self.__open_list_window('_orig_sample_sets_list', OrigSampleSets_List)

    def _on_show_stations(self, event):
        self.__open_list_window('_stations_list', Stations_List)

    def _on_show_mine_object(self, event):
        self.__open_list_window('_mine_objects_list', MineObjects_List)

    def _on_show_coord_system(self, event):
        self.__open_list_window('_coord_systems_list', CoordSystems_List)

    def _on_create_discharge_measurement(self, event):
        w = DischargeMeasurementEditor(parent=self, on_save=lambda: self.__list.refresh())
        w.Show()

    def _on_create_orig_sample_sets(self, event):
        w = OrigSampleSets_Editor(parent=self)
        w.Show()

    def _on_create_discharge_series(self, event):
        w = DischargeSeriesEditor(parent=self)
        w.Show()

    def _on_show_settings(self, event):
        w = Settings(parent=self)
        w.ShowModal()

    def select(self, e: DischargeMeasurement):
        self.__list.select(e)