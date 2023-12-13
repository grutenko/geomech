import wx
import database
import typing
import widgets.entity_link

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

        self.panel_2 = wx.ScrolledWindow(self.panel_1, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
        self.panel_2.SetScrollRate(10, 10)
        sizer_1.Add(self.panel_2, 1, wx.EXPAND, 0)

        self.grid = wx.FlexGridSizer(0, 2, 0, 0)

        sizer_2 = wx.StdDialogButtonSizer()
        sizer_1.Add(sizer_2, 0, wx.ALIGN_RIGHT | wx.ALL, 10)

        self.button_OK = wx.Button(self.panel_1, wx.ID_ANY, u"ОК")
        self.button_OK.SetDefault()
        sizer_2.Add(self.button_OK, 0, 0, 0)

        sizer_2.Realize()

        self.panel_2.SetSizer(self.grid)

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
        name.Wrap(150)
        self.grid.Add(name, 0, wx.ALIGN_RIGHT | wx.ALL, 4)
        self.grid.Add(value, 0, wx.ALL | wx.CENTER, 4)
        self.grid.Layout()

    def _set_name(self, name: str):
        self.SetTitle(name)

    def _set_fields(self, e: database.Base):
        raise NotImplementedError("Method _set_fields() not implemented in class {0}".format(self.__class__.__name__))
    
    def Bind(self, event, handler, source=None, id=wx.ID_ANY, id2=wx.ID_ANY):
        return super().Bind(event, handler, source, id, id2)
    
class _DischargeMeasurement_Inspect(_Inspect):
    def _set_fields(self, e: database.DischargeMeasurement):
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

class _CoordSystem_Inspect(_Inspect):
    def _set_fields(self, e: database.DischargeMeasurement):
        self._set_name("Система координат " + str(e.Name))
        self._add_field("ID:", self._text_value(e.RID))

class _MineObject_Inspect(_Inspect):
    def _set_fields(self, e: database.DischargeMeasurement):
        self._set_name("Горный объект " + str(e.Name))
        self._add_field("ID:", self._text_value(e.RID))

class _OrigSampleSetInspect(_Inspect):
    def _set_fields(self, e: database.DischargeMeasurement):
        self._set_name("Набор образцов " + str(e.Name))
        self._add_field("ID:", self._text_value(e.RID))

class _Station_Inspect(_Inspect):
    def _set_fields(self, e: database.DischargeMeasurement):
        self._set_name("Станция " + str(e.Name))
        self._add_field("ID:", self._text_value(e.RID))

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