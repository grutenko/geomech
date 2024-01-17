import wx
import database
import typing
import wx.lib.splitter
import wx.dataview
import widgets.entity_link
import widgets.supplied_data_viewer
import widgets.relations_viewer
from dataclasses import dataclass

class Ui_Inspect(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.SetSize((482, 766))
        self.SetTitle("Обзор объекта")

        self.frame_3_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        self.frame_3_menubar.Append(wxglade_tmp_menu, u"Печать")
        self.SetMenuBar(self.frame_3_menubar)

        self.panel_1 = wx.Panel(self, wx.ID_ANY)
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        
        self.split = wx.lib.splitter.MultiSplitterWindow(self.panel_1, style=wx.SP_LIVE_UPDATE)
        self.split.SetOrientation(wx.VERTICAL)
        sizer_1.Add(self.split, 1, wx.EXPAND, 0)

        self.panel_main_info = wx.ScrolledWindow(self.split, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.panel_main_info.SetScrollRate(10, 10)
        sizer_main_info = wx.StaticBoxSizer(wx.StaticBox(self.panel_main_info, wx.ID_ANY, u"Основная информация"), wx.HORIZONTAL)
        self.grid = wx.FlexGridSizer(0, 2, 0, 0)
        sizer_main_info.Add(self.grid, 1, wx.EXPAND, 0)
        self.panel_main_info.SetSizer(sizer_main_info)
        self.split.AppendWindow(self.panel_main_info, 250)

        self.panel_relations = wx.Panel(self.split)
        sizer_relations = wx.StaticBoxSizer(wx.StaticBox(self.panel_relations, wx.ID_ANY, u"Связаные объкты"), wx.HORIZONTAL)
        self.relations = widgets.relations_viewer.RelationViewer(self.panel_relations)
        sizer_relations.Add(self.relations, 1, wx.EXPAND, 0)
        self.panel_relations.SetSizer(sizer_relations)
        self.split.AppendWindow(self.panel_relations, 20)

        self.panel_supplied_data = wx.Panel(self.split)
        sizer_supplied_data = wx.StaticBoxSizer(wx.StaticBox(self.panel_supplied_data, wx.ID_ANY, u"Сопроводительные материалы"), wx.HORIZONTAL)
        self.supplied_data = widgets.supplied_data_viewer.SuppliedData_Viewer(self.panel_supplied_data)
        sizer_supplied_data.Add(self.supplied_data, 1, wx.EXPAND, 0)
        self.panel_supplied_data.SetSizer(sizer_supplied_data)
        self.split.AppendWindow(self.panel_supplied_data, 20)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self.panel_1, wx.ID_ANY, u"ОК")
        self.button_OK.SetDefault()
        sizer_2.Add(self.button_OK, 0, 0, 0)

        self.panel_1.SetSizer(sizer_1)

        sizer_2.Realize()

        self.Layout()
        self.Centre()

@dataclass
class _Field:
    label: str

@dataclass
class _TextField(_Field):
    value: typing.Optional[str]

@dataclass
class _RelationField(_Field):
    related_to: database.Base

class _Inspect(Ui_Inspect):
    def __init__(self, 
                 fields: typing.List[_Field],
                 supplied_data: typing.List[database.SuppliedData] = None,
                 relations: typing.List[typing.Tuple[str, database.Base]] = None,
                 *args, **kwds):
        super().__init__(*args, **kwds)
        if 'title' in kwds:
            self.SetTitle(kwds['title'])
        self.__display_fields(fields)
        if supplied_data != None:
            self.__display_supplied_data(supplied_data)
        if relations != None:
            self.__display_relations(relations)
        self.button_OK.Bind(wx.EVT_BUTTON, lambda _: self.Close())
    
    def __display_fields(self, fields) -> None:
        self.grid.SetRows(len(fields))
        for field in fields:
            name = wx.StaticText(self.panel_main_info, label=field.label)
            name.Wrap(250)
            self.grid.Add(name, 0, wx.ALIGN_RIGHT | wx.ALL, 4)
            if isinstance(field, _TextField):
                value = wx.StaticText(self.panel_main_info, label=str(field.value) if field.value != None else '<Не задано>')
                value.Wrap(200)
            elif isinstance(field, _RelationField):
                if field.related_to != None:
                    value = widgets.entity_link.EntityLink(parent=self.panel_main_info)
                    value.set_entity(field.related_to)
                else: 
                    value = wx.StaticText(self.panel_main_info, label="<Не задано>")
                    value.Wrap(200)
            else:
                raise Exception("Unsupported field class {}.".format(field.__class__.__name__))
            self.grid.Add(value, 0, wx.ALL | wx.CENTER, 4)
        self.grid.Layout()
        self.panel_main_info.FitInside()

    def __display_supplied_data(self, supplied_data) -> None:
        self.split.SetSashPosition(2, 250)
        self.supplied_data.set_data(supplied_data)

    def __display_relations(self, relations) -> None:
        self.split.SetSashPosition(1, 250)
        self.relations.set_relations(relations)

def discharge_measurement_factory(e: database.DischargeMeasurement) -> _Inspect:
    fields = [
        _TextField("Id", e.RID),
        _RelationField("Серия замеров", e.discharge_series),
        _TextField("Замер №", e.SNumber),
        _TextField("Рег. № разгрузки", e.DschNumber),
        _TextField("Рег. № образца керна", e.CoreNumber),
        _TextField("Диаметр образца керна", e.Diameter),
        _TextField("Диаметр образца керна", e.Diameter),
        _TextField("Вес образца керна", e.Weight),
        _TextField("Тензопатрон №", e.CartNumber),
        _TextField("Партия тензопатронов №", e.PartNumber),
        _TextField("Сопр. тензорезистора", "1) {0} Ом, 2) {1} Ом, 3) {2} Ом, 4) {3} Ом".format(e.R1, e.R2, e.R3, e.R4)),
        _TextField("Сопр. компенсационного резистора", str(e.RComp) + ' Ом'),
        _TextField("Коэф. чувств. тензодатчиков", e.Sensitivity),
        _TextField("Замер времени прохождения продольных волн (ультразвуковое профилирование или др.)", "1) {0}, 2) {1}".format(e.TP1_1, e.TP1_2)),
        _TextField("Замер времени прохождения продольных волн (между торцами или др.)", "1) {0}, 2) {1}".format(e.TP2_1, e.TP2_2)),
        _TextField("Замер времени прохождения поверхностных волн", "1) {0}, 2) {1}".format(e.TR_1, e.TR_2)),
        _TextField("Замер времени прохождения поперечных волн", "1) {0}, 2) {1}".format(e.TS_1, e.TS_2)),
        _TextField("Статический коэффициент Пуассона", str(e.PuassonStatic)),
        _TextField("Статический модуль Юнга", str(e.YungStatic)),
        _TextField("Глубина взятия образца керна", str(e.CoreDepth)),
        _TextField("Относительная деформация образца", "1) {0}, 2) {1}, 3) {2}, 4) {3}".format(e.E1, e.E2, e.E3, e.E4)),
        _TextField("Угол коррекции направления напряжений", e.Rotate),
        _TextField("Тип породы", e.RockType)
    ]
    return _Inspect(fields=fields, title=e.__str__(), parent=None)

def discharge_series_factory(e: database.DischargeSeries) -> _Inspect:
    fields = [
        _TextField("ID", e.RID),
        _RelationField("Набор образцов", e.orig_sample_set),
        _TextField("№ серии замеров", e.Number),
        _TextField("Название", e.Name),
        _TextField("Комментарий", e.Comment),
        _TextField("Дата замера", e.MeasureDate)
    ]
    relations = [
        ('Поразгрузочные замеры', e.discharge_measurements)
    ]
    return _Inspect(fields=fields, relations=relations, title="Серия замеров " + str(e.Name), parent=None)

def bore_hole_factory(e: database.BoreHole) -> _Inspect:
    fields = [
        _TextField("ID", e.RID),
        _TextField("№ скважины", e.Number),
        _TextField("Название:", e.Name),
        _TextField("Комментарий:", e.Comment),
        _RelationField("Станция:", e.station),
        _RelationField("Горный объект:", e.mine_object),
        _TextField("Координаты:", "X: {0}, Y: {1}, Z: {2}".format(e.X, e.Y, e.Z)),
        _TextField("Азимут:", e.Azimuth),
        _TextField("Наклон:", e.Tilt),
        _TextField("Диаметр:", str(e.Diameter) + 'м'),
        _TextField("Длина:", str(e.Length) + 'м'),
        _TextField("Дата закладки / начала измерений:", e.StartDate),
        _TextField("Дата завершения измерений:", e.EndDate)
    ]
    relations = [
        ("Исходные наборы образцов", e.orig_sample_sets)
    ]
    return _Inspect(fields=fields, relations=relations, title="Скважина " + str(e.Name), supplied_data=e.supplied_data, parent=None)

def coord_system_factory(e: database.CoordSystem) -> _Inspect:
    fields = [
        _TextField("ID:", e.RID),
        _RelationField("Вышестоящая система координат:", e.parent),
        _TextField("Уровень:", e.Level),
        _TextField("Название:", e.Name),
        _TextField("Комментарий:", e.Comment),
        _TextField("Минимальные координаты:", "X: {0}, Y: {1}, Z: {2}".format(e.X_Min, e.Y_Min, e.Z_Min)),
        _TextField("Максимальные координаты:", "X: {0}, Y: {1}, Z: {2}".format(e.X_Max, e.Y_Max, e.Z_Max)),
        _TextField("Положение начала в вышестоящей системе координат:", "X: {0}, Y: {1}, Z: {2}".format(e.X_0, e.Y_0, e.Z_0))
    ]
    relations = [
        ("Горные объекты", e.mine_objects)
    ]
    return _Inspect(fields=fields, relations=relations, title="Скважина " + str(e.Name), parent=None)

def mine_object_factory(e: database.MineObject) -> _Inspect:
    if e.Type == 'REGION':
        type = 'Регион'
    elif e.Type == 'ROCKS':
        type = 'Горный массив'
    elif e.Type == 'FIELD':
        type = 'Месторождение'
    elif e.Type == 'HORIZON':
        type = 'Горизонт'
    elif e.Type == 'EXCAVATION':
        type = 'Выработка'
    fields = [
        _TextField("ID:", e.RID),
        _RelationField("Вышестоящий горный объект:", e.parent),
        _TextField("Уровень:", e.Level),
        _TextField("Название:", e.Name),
        _TextField("Комментарий:", e.Comment),
        _RelationField("Система координат:", e.coord_system),
        _TextField("Тип:", type),
        _TextField("Минимальные координаты:", "X: {0}, Y: {1}, Z: {2}".format(e.X_Min, e.Y_Min, e.Z_Min)),
        _TextField("Максимальные координаты:", "X: {0}, Y: {1}, Z: {2}".format(e.X_Max, e.Y_Max, e.Z_Max))
    ]
    relations = [
        ("Исходные наборы образцов", e.orig_sample_sets),
        ("Скважины", e.bore_holes),
        ("Станции", e.stations)
    ]
    return _Inspect(fields=fields, relations=relations, title="Горный объект " + e.Name, supplied_data=e.supplied_data, parent=None)

def station_factory(e: database.Station) -> _Inspect:
    fields = [
        _TextField("ID:", e.RID),
        _TextField("№ станции:", e.Number),
        _TextField("Название:", e.Name),
        _TextField("Комментарий:", e.Comment),
        _RelationField("Горный объект:", e.mine_object),
        _TextField("Координаты:", "X: {0}, Y: {1}, Z: {2}".format(e.X, e.Y, e.Z)),
        _TextField("Дата закладки / начала измерений:", e.StartDate),
        _TextField("Дата завершения измерений:", e.EndDate)
    ]
    relations = [
        ("Скважины", e.bore_holes)
    ]
    return _Inspect(fields=fields, relations=relations, title="Станция " + e.Name, supplied_data=e.supplied_data, parent=None)

def orig_sample_set_factory(e: database.OrigSampleSet) -> _Inspect:
    if e.SampleType == 'CORE':
        type = 'Керн'
    elif e.SampleType == 'STUFF':
        type = 'Штуф'
    elif e.SampleType == 'DISPERCE':
        type = 'Дисперсный материал'
    fields = [
        _TextField("ID:", e.RID),
        _TextField("№ набора образцов:", e.Number),
        _TextField("Название:", e.Name),
        _TextField("Комментарий:", e.Comment),
        _TextField("Тип метариала", type),
        _RelationField("Горный объект:", e.mine_object),
        _RelationField("Скважина:", e.bore_hole),
        _TextField("Дата отбора:", e.SetDate)
    ]
    relations = [
        ("Серии замеров", e.discharge_series)
    ]
    return _Inspect(fields=fields, relations=relations, supplied_data=e.supplied_data, title="Набор образцов " + e.Name, parent=None)

__MAPPING__ = {
    database.DischargeMeasurement: discharge_measurement_factory,
    database.DischargeSeries: discharge_series_factory,
    database.BoreHole: bore_hole_factory,
    database.CoordSystem: coord_system_factory,
    database.MineObject: mine_object_factory,
    database.OrigSampleSet: orig_sample_set_factory,
    database.Station: station_factory,
}

__windows: typing.Dict[database.Base, _Inspect] = {}

def __check_class(table_class: typing.Type[database.Base]):
    if not issubclass(table_class, database.Base):
        raise Exception(table_class.__name__ + " is not a database model.")
    if not table_class in __MAPPING__:
        raise Exception("List window for " + table_class.__name__ + " not found.")

def cmd_show(e: database.Base):
    __check_class(type(e))
    global __windows
    if e in __windows:
        __windows[e].Raise()
    else:
        __windows[e] = __MAPPING__[e.__class__](e)
        def _on_close(event):
            event.Skip()
            del __windows[e]
        __windows[e].Bind(wx.EVT_CLOSE, _on_close)
        __windows[e].Show()

def cmd_close(e: database.Base):
    __check_class()
    global __windows
    if e in __windows:
        __windows[e].Close()