import wx

from ui.icon import get_art, get_icon
from version import __GEOMECH_VERSION__

ID_FIND_NEXT = wx.ID_HIGHEST + 1
ID_OBJECTS_TOGGLE = ID_FIND_NEXT + 1
ID_FASTVIEW_TOGGLE = ID_FIND_NEXT + 2
ID_SUPPLIED_DATA_TOGGLE = ID_FIND_NEXT + 3
ID_OPEN_START_TAB = ID_FIND_NEXT + 4
ID_SETTINGS_PM = ID_FIND_NEXT + 6
ID_SETTINGS_CS = ID_FIND_NEXT + 7
ID_DM_TOGGLE = ID_FIND_NEXT + 8
ID_PM_TOGGLE = ID_FIND_NEXT + 9
ID_RB_TOGGLE = ID_FIND_NEXT + 10
ID_IMPORT_BORE_HOLES = ID_FIND_NEXT + 11
ID_IMPORT_STATIONS = ID_FIND_NEXT + 12
ID_TOGGLE_DEVIATIONS = ID_FIND_NEXT + 13
ID_IMPORT_ROCK_BURSTS = ID_FIND_NEXT + 14
ID_SETTINGS_DOCS = ID_FIND_NEXT + 15
ID_CS_TRANS_UTLITY = ID_FIND_NEXT + 16
ID_CS_FIND_MATRIX = ID_FIND_NEXT + 17


class MainMenu(wx.MenuBar):
    def __init__(self):
        super().__init__()
        menu = wx.Menu()
        item = menu.Append(wx.ID_FIND, "Поиск\tCTRL+F")
        item.SetBitmap(get_icon("find", scale_to=16))
        item.Enable(False)
        item = menu.Append(ID_FIND_NEXT, "Искать далее\tCTRL+SHIFT+F")
        item.SetBitmap(get_icon("find", scale_to=16))
        item.Enable(False)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_SAVE, "Сохранить редактор\tCTRL+S")
        item.SetBitmap(get_icon("save", scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_PREVIEW_NEXT, "Следующий редактор\tCTRL+RIGHT")
        item.SetBitmap(get_icon("next", scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_PREVIEW_PREVIOUS, "Предыдущий редактор\tCTRL+LEFT")
        item.SetBitmap(get_icon("back", scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_CLOSE, "Закрыть редактор\tCTRL+W")
        item.SetBitmap(get_icon("delete", scale_to=16))
        item.Enable(False)

        menu.AppendSeparator()
        item = menu.Append(wx.ID_EXIT, "Выйти")

        self.Append(menu, "Файл")

        menu = wx.Menu()
        item = menu.Append(wx.ID_COPY, "Копировать\tCTRL+C")
        item.SetBitmap(get_icon("copy", scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_CUT, "Вырезать\tCTRL+X")
        item.SetBitmap(get_icon("cut", scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_PASTE, "Вставить\tCTRL+V")
        item.SetBitmap(get_icon("paste", scale_to=16))
        item.Enable(False)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_UNDO, "Отменить\tCTRL+Z")
        item.SetBitmap(get_icon("undo", scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_REDO, "Вернуть\tCTRL+Y")
        item.SetBitmap(get_icon("redo", scale_to=16))
        item.Enable(False)
        self.Append(menu, "Правка")

        menu = wx.Menu()
        item = menu.AppendCheckItem(ID_OBJECTS_TOGGLE, "[Объекты] Показать/Скрыть\tCTRL+ALT+O")
        item = menu.AppendCheckItem(ID_FASTVIEW_TOGGLE, "[Быстрый просмотр] Показать/Скрыть\tCTRL+ALT+R")
        item = menu.AppendCheckItem(ID_SUPPLIED_DATA_TOGGLE, "[Сопутствующие материалы] Показать/Скрыть\tCTRL+ALT+D")
        menu.AppendSeparator()
        item = menu.AppendCheckItem(ID_DM_TOGGLE, "[Разгрузка] Показать/Скрыть")
        item = menu.AppendCheckItem(ID_PM_TOGGLE, "[Физ. мех. свойства] Показать/Скрыть")
        item = menu.AppendCheckItem(ID_RB_TOGGLE, "[Горные удары] Показать/Скрыть")
        self.Append(menu, "Вид")

        menu = wx.Menu()
        item = menu.Append(ID_IMPORT_BORE_HOLES, "Импортировать скважины")
        item.SetBitmap(get_icon("import-xls"))
        item = menu.Append(ID_IMPORT_STATIONS, "Импортировать измерительные станции")
        item.SetBitmap(get_icon("import-xls"))
        self.Append(menu, "Импорт")

        menu = wx.Menu()
        item = menu.Append(ID_SETTINGS_PM, "Физ. Мех. свойства")
        item = menu.Append(ID_SETTINGS_CS, "Системы координат")
        item = menu.Append(ID_SETTINGS_DOCS, "Документы")
        self.Append(menu, "Параметры")

        menu = wx.Menu()
        item = menu.Append(ID_CS_TRANS_UTLITY, "Утилита перевода координат")
        item = menu.Append(ID_CS_FIND_MATRIX, "Утилита нахождения матрицы перевода")
        self.Append(menu, "Утилиты")

        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Версия: " + __GEOMECH_VERSION__)
        item.Enable(False)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ABOUT, "О программе")
        item = menu.AppendCheckItem(ID_OPEN_START_TAB, 'Открыть "Начало работы"')
        item.Check(True)
        self.Append(menu, "Справка")
