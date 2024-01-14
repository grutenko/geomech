import wx
import database
import typing
import widgets.entity_link
import widgets.supplied_data_viewer

class Ui_Inspect(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.SetSize((400, 491))
        self.SetTitle("frame_3")

        # Menu Bar
        self.frame_3_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        self.frame_3_menubar.Append(wxglade_tmp_menu, u"Экспортировать")
        self.SetMenuBar(self.frame_3_menubar)
        # Menu Bar end

        self.panel_1 = wx.Panel(self, wx.ID_ANY)

        sizer_1 = wx.BoxSizer(wx.VERTICAL)

        self.window_1 = wx.SplitterWindow(self.panel_1, wx.ID_ANY, style=wx.SP_3D | wx.SP_LIVE_UPDATE)
        self.window_1.SetMinimumPaneSize(20)
        sizer_1.Add(self.window_1, 1, wx.EXPAND, 0)

        self.panel_2 = wx.ScrolledWindow(self.window_1, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.panel_2.SetScrollRate(10, 10)

        self.grid = wx.FlexGridSizer(0, 2, 0, 0)

        self.window_1_pane_2 = wx.Panel(self.window_1, wx.ID_ANY)

        sizer_3 = wx.StaticBoxSizer(wx.StaticBox(self.window_1_pane_2, wx.ID_ANY, u"Сопутствующие материалы"), wx.VERTICAL)

        self.supplied_data = widgets.supplied_data_viewer.SuppliedData_Viewer(self.window_1_pane_2, wx.ID_ANY)
        sizer_3.Add(self.supplied_data, 1, wx.EXPAND, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self.button_OK = wx.Button(self.panel_1, wx.ID_ANY, u"ОК")
        self.button_OK.SetDefault()
        sizer_2.Add(self.button_OK, 0, 0, 0)

        sizer_2.Realize()

        self.window_1_pane_2.SetSizer(sizer_3)

        self.panel_2.SetSizer(self.grid)

        self.window_1.SplitHorizontally(self.panel_2, self.window_1_pane_2)

        self.panel_1.SetSizer(sizer_1)

        self.Layout()

class _Inspect(Ui_Inspect):
    _entity: database.Base
    __rows: int = 0

    def __init__(self, entity: database.Base, *args, **kwds):
        super().__init__(*args, **kwds)
        self._entity = entity
        self._set_fields(self._entity)
        self.button_OK.Bind(wx.EVT_BUTTON, self.__on_button_ok)

    def __on_button_ok(self, event):
        self.Close()

    def _text_value(self, label: str):
        v = wx.StaticText(self.panel_2, label=str(label))
        v.Wrap(200)
        return v
    
    def _relation_value(self, e: database.Base):
        link = widgets.entity_link.EntityLink(parent=self.panel_2)
        link.set_entity(e)
        return link

    def _add_field(self, label: str, value):
        self.__rows += 1
        self.grid.SetRows(self.__rows)
        name = wx.StaticText(self.panel_2, label=str(label))
        name.Wrap(250)
        self.grid.Add(name, 0, wx.ALIGN_RIGHT | wx.ALL, 4)
        self.grid.Add(value, 0, wx.ALL | wx.CENTER, 4)
        self.grid.Layout()
        self.panel_2.FitInside()

    def _set_name(self, name: str):
        self.SetTitle(name)

    def _set_fields(self, e: database.Base):
        raise NotImplementedError("Method _set_fields() not implemented in class {0}".format(self.__class__.__name__))
    
    def Bind(self, event, handler, source=None, id=wx.ID_ANY, id2=wx.ID_ANY):
        return super().Bind(event, handler, source, id, id2)
    
class _DischargeMeasurement_Inspect(_Inspect):
    def _set_fields(self, e: database.DischargeMeasurement):
        self.SetSize((500, 600))
        self._set_name("Замер №" + str(e.RID))
        self._add_field("ID:", self._text_value(e.RID))
        self._add_field("Серия замеров:", self._relation_value(e.discharge_series))
        self._add_field("№ замера:", self._text_value(e.SNumber))
        self._add_field("Рег. № разгрузки:", self._text_value(e.DschNumber))
        self._add_field("Рег. № образца керна:", self._text_value(e.CoreNumber))
        self._add_field("Диаметр образца керна:", self._text_value(e.Diameter))
        self._add_field("Диаметр образца керна:", self._text_value(e.Diameter))
        self._add_field("Вес образца керна:", self._text_value(e.Weight))
        self._add_field("Тензопатрон №:", self._text_value(e.CartNumber))
        self._add_field("Партия тензопатронов №:", self._text_value(e.PartNumber))
        self._add_field("Сопр. тензорезистора:", self._text_value("1) {0} Ом, 2) {1} Ом, 3) {2} Ом, 4) {3} Ом".format(e.R1, e.R2, e.R3, e.R4)))
        self._add_field("Сопр. компенсационного резистора:", self._text_value(str(e.RComp) + ' Ом'))
        self._add_field("Коэф. чувств. тензодатчиков:", self._text_value(e.Sensitivity))
        self._add_field("Замер времени прохождения продольных волн (ультразвуковое профилирование или др.):", self._text_value("1) {0}, 2) {1}".format(e.TP1_1, e.TP1_2)))
        self._add_field("Замер времени прохождения продольных волн (между торцами или др.):", self._text_value("1) {0}, 2) {1}".format(e.TP2_1, e.TP2_2)))
        self._add_field("Замер времени прохождения поверхностных волн:", self._text_value("1) {0}, 2) {1}".format(e.TR_1, e.TR_2)))
        self._add_field("Замер времени прохождения поперечных волн:", self._text_value("1) {0}, 2) {1}".format(e.TS_1, e.TS_2)))
        self._add_field("Статический коэффициент Пуассона:", self._text_value(str(e.PuassonStatic)))
        self._add_field("Статический модуль Юнга:", self._text_value(str(e.YungStatic)))
        self._add_field("Глубина взятия образца керна:", self._text_value(str(e.CoreDepth)))
        self._add_field("Относительная деформация образца:", self._text_value("1) {0}, 2) {1}, 3) {2}, 4) {3}".format(e.E1, e.E2, e.E3, e.E4)))
        self._add_field("Угол коррекции направления напряжений:", self._text_value(str(e.Rotate)))
        self._add_field("Тип породы:", self._text_value(str(e.RockType)))

def _date_modifier(date):
    return str(date)[0:4] + '.' + str(date)[4:6] + '.' + str(date)[6:8]

class _DischargeSeries_Inspect(_Inspect):
    def _set_fields(self, e: database.DischargeSeries):
        self._set_name("Серия замеров " + str(e.Name))
        self._add_field("ID:", self._text_value(e.RID))
        self._add_field("Набор образцов:", self._relation_value(e.orig_sample_set))
        self._add_field("№ серии замеров:", self._text_value(e.Number))
        self._add_field("Название:", self._text_value(e.Name))
        self._add_field("Комментарий:", self._text_value(e.Comment))
        self._add_field("Дата замера:", self._text_value(_date_modifier(e.MeasureDate)))

class _BoreHole_Inspect(_Inspect):
    def _set_fields(self, e: database.BoreHole):
        self._set_name("Скважина " + str(e.Name))
        self._add_field("ID:", self._text_value(e.RID))
        self._add_field("№ скважины:", self._text_value(e.Number))
        self._add_field("Название:", self._text_value(e.Name))
        self._add_field("Комментарий:", self._text_value(e.Comment))
        self._add_field("Станция:", self._relation_value(e.station))
        self._add_field("Горный объект:", self._relation_value(e.mine_object))
        self._add_field("Координаты:", self._text_value("X: {0}, Y: {1}, Z: {2}".format(e.X, e.Y, e.Z)))
        self._add_field("Азимут:", self._text_value(e.Azimuth))
        self._add_field("Наклон:", self._text_value(e.Tilt))
        self._add_field("Диаметр:", self._text_value(str(e.Diameter) + 'м'))
        self._add_field("Дата закладки / начала измерений:", self._text_value(_date_modifier(e.StartDate)))
        self._add_field("Дата завершения измерений:", self._text_value(_date_modifier(e.EndDate) if e.EndDate != None else '<нет>'))

        self.supplied_data.set_data_owner(e)

class _CoordSystem_Inspect(_Inspect):
    def _set_fields(self, e: database.DischargeMeasurement):
        self._set_name("Система координат " + str(e.Name))
        self._add_field("ID:", self._text_value(e.RID))
        self._add_field("Вышестоящая система координат:", self._relation_value(e.parent) if e.parent != None else self._text_value("<нет>"))
        self._add_field("Уровень системы координат:", self._text_value(str(e.Level)))
        self._add_field("Название:", self._text_value(e.Name))
        self._add_field("Комментарий:", self._text_value(e.Comment))
        self._add_field("Минимальные координаты:", self._text_value("X: {0}, Y: {1}, Z: {2}".format(e.X_Min, e.Y_Min, e.Z_Min)))
        self._add_field("Максимальные координаты:", self._text_value("X: {0}, Y: {1}, Z: {2}".format(e.X_Max, e.Y_Max, e.Z_Max)))
        self._add_field("Положение начала в вышестоящей системе координат:", self._text_value("X: {0}, Y: {1}, Z: {2}".format(e.X_0, e.Y_0, e.Z_0)))

class _MineObject_Inspect(_Inspect):
    def _set_fields(self, e: database.MineObject):
        self._set_name("Горный объект " + str(e.Name))
        self._add_field("ID:", self._text_value(e.RID))
        self._add_field("Вышестоящий горный объект:", self._relation_value(e.parent) if e.parent != None else self._text_value("<нет>"))
        self._add_field("Уровень системы координат:", self._text_value(str(e.Level)))
        self._add_field("Название:", self._text_value(e.Name))
        self._add_field("Комментарий:", self._text_value(e.Comment))
        self._add_field("Система координат:", self._relation_value(e.coord_system))
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
        self._add_field("Тип:", self._text_value(type))
        self._add_field("Минимальные координаты:", self._text_value("X: {0}, Y: {1}, Z: {2}".format(e.X_Min, e.Y_Min, e.Z_Min)))
        self._add_field("Максимальные координаты:", self._text_value("X: {0}, Y: {1}, Z: {2}".format(e.X_Max, e.Y_Max, e.Z_Max)))
        
        self.supplied_data.set_data_owner(e)

class _OrigSampleSetInspect(_Inspect):
    def _set_fields(self, e: database.DischargeMeasurement):
        self._set_name("Набор образцов " + str(e.Name))
        self._add_field("ID:", self._text_value(e.RID))
        self._add_field("№ набора образцов:", self._text_value(e.Number))
        self._add_field("Название:", self._text_value(e.Name))
        self._add_field("Комментарий:", self._text_value(e.Comment))
        if e.SampleType == 'CORE':
            type = 'Керн'
        elif e.SampleType == 'STUFF':
            type = 'Штуф'
        elif e.SampleType == 'DISPERCE':
            type = 'Дисперсный материал'
        self._add_field("Тип метариала", self._text_value(type))
        self._add_field("Горный объект:", self._relation_value(e.mine_object))
        self._add_field("Скважина:", self._relation_value(e.bore_hole))
        self._add_field("Дата отбора:", self._text_value(_date_modifier(e.SetDate)))

        self.supplied_data.set_data_owner(e)

class _Station_Inspect(_Inspect):
    def _set_fields(self, e: database.DischargeMeasurement):
        self._set_name("Станция " + str(e.Name))
        self._add_field("ID:", self._text_value(e.RID))
        self._add_field("№ станции:", self._text_value(e.Number))
        self._add_field("Название:", self._text_value(e.Name))
        self._add_field("Комментарий:", self._text_value(e.Comment))
        self._add_field("Горный объект:", self._relation_value(e.mine_object))
        self._add_field("Координаты:", self._text_value("X: {0}, Y: {1}, Z: {2}".format(e.X, e.Y, e.Z)))
        self._add_field("Дата закладки / начала измерений:", self._text_value(_date_modifier(e.StartDate)))
        self._add_field("Дата завершения измерений:", self._text_value(_date_modifier(e.EndDate) if e.EndDate != None else '<нет>'))

        self.supplied_data.set_data_owner(e)

__MAPPING__ = {
    database.DischargeMeasurement: _DischargeMeasurement_Inspect,
    database.DischargeSeries: _DischargeSeries_Inspect,
    database.BoreHole: _BoreHole_Inspect,
    database.CoordSystem: _CoordSystem_Inspect,
    database.MineObject: _MineObject_Inspect,
    database.OrigSampleSet: _OrigSampleSetInspect,
    database.Station: _Station_Inspect,
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
        __windows[e] = __MAPPING__[e.__class__](e, parent=None)
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