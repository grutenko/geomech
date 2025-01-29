
import wx

from ui.icon import get_art, get_icon

from .equipments import PmEquipment
from .methods import PmMethodsPanel
from .properties import Properties
from .property_classes import PropertyClasses
from .tasks import Tasks

ID_FIND_NEXT = wx.ID_HIGHEST + 250


class PmSettingsWindow(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_FLOAT_ON_PARENT)
        self.SetSize(800, 350)
        self.SetMinSize(wx.Size(400, 200))
        self.SetTitle('Параметры "Физ. Мех. свойства"')
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnParent()

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.notebook = wx.Notebook(self)

        self._pm_methods = PmMethodsPanel(self.notebook)
        self.notebook.AddPage(self._pm_methods, "Методы испытаний")
        self._pm_equipment = PmEquipment(self.notebook)
        self.notebook.AddPage(self._pm_equipment, "Оборудование")
        self._pm_properties_classes = PropertyClasses(self.notebook)
        self.notebook.AddPage(self._pm_properties_classes, "Классы свойств")
        self._pm_properties = Properties(self.notebook)
        self.notebook.AddPage(self._pm_properties, "Свойства")
        self._pm_tasks = Tasks(self.notebook)
        self.notebook.AddPage(self._pm_tasks, "Выполняемые задачи")

        main_sizer.Add(self.notebook, 1, wx.EXPAND)

        self.SetSizer(main_sizer)

        self.Bind(wx.EVT_CLOSE, self._on_close)

        self.Layout()

    def _on_find(self, event):
        dlg = wx.TextEntryDialog(self, "Введите часть названия", "Поиск по разделу")
        dlg.SetIcon(wx.Icon(get_art(wx.ART_FIND)))
        _current_panel = self._right_sizer.GetItem(0).GetWindow()
        q = _current_panel.get_last_q()
        dlg.SetValue(q if q != None else "")
        if dlg.ShowModal() == wx.ID_OK:
            _current_panel.start_find(dlg.GetValue())

    def _on_find_next(self, event): ...

    def _on_close(self, event):
        self.Hide()
