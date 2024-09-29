import wx

from ui.icon import get_art
from version import __GEOMECH_VERSION__

ID_FIND_NEXT = wx.ID_HIGHEST + 1
ID_OBJECTS_TOGGLE = ID_FIND_NEXT + 1
ID_FASTVIEW_TOGGLE = ID_FIND_NEXT + 2
ID_SUPPLIED_DATA_TOGGLE = ID_FIND_NEXT + 3
ID_OPEN_START_TAB = ID_FIND_NEXT + 4
ID_COORD_SYSTEMS_TOGGLE = ID_FIND_NEXT + 5
ID_SETTINGS_PM = ID_FIND_NEXT + 6

class MainMenu(wx.MenuBar):
    def __init__(self):
        super().__init__()
        menu = wx.Menu()
        item = menu.Append(wx.ID_FIND, "Поиск\tCTRL+F")
        item.SetBitmap(get_art(wx.ART_FIND, scale_to=16))
        item.Enable(False)
        item = menu.Append(ID_FIND_NEXT, "Искать далее\tCTRL+SHIFT+F")
        item.SetBitmap(get_art(wx.ART_FIND, scale_to=16))
        item.Enable(False)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_SAVE, "Сохранить редактор\tCTRL+S")
        item.SetBitmap(get_art(wx.ART_FILE_SAVE, scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_PREVIEW_NEXT, "Следующий редактор\tCTRL+RIGHT")
        item.SetBitmap(get_art(wx.ART_GO_FORWARD, scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_PREVIEW_PREVIOUS, "Предыдущий редактор\tCTRL+LEFT")
        item.SetBitmap(get_art(wx.ART_GO_BACK, scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_CLOSE, "Закрыть редактор\tCTRL+W")
        item.SetBitmap(get_art(wx.ART_CLOSE, scale_to=16))
        item.Enable(False)
        
        menu.AppendSeparator()
        item = menu.Append(wx.ID_EXIT, "Выйти")

        self.Append(menu, "Файл")

        menu = wx.Menu()
        item = menu.Append(wx.ID_COPY, "Копировать\tCTRL+C")
        item.SetBitmap(get_art(wx.ART_COPY, scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_CUT, "Вырезать\tCTRL+X")
        item.SetBitmap(get_art(wx.ART_CUT, scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_PASTE, "Вставить\tCTRL+V")
        item.SetBitmap(get_art(wx.ART_PASTE, scale_to=16))
        item.Enable(False)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_UNDO, "Отменить\tCTRL+Z")
        item.SetBitmap(get_art(wx.ART_UNDO, scale_to=16))
        item.Enable(False)
        item = menu.Append(wx.ID_REDO, "Вернуть\tCTRL+Y")
        item.SetBitmap(get_art(wx.ART_REDO, scale_to=16))
        item.Enable(False)
        self.Append(menu, "Правка")

        menu = wx.Menu()
        item = menu.AppendCheckItem(ID_OBJECTS_TOGGLE, "[Объекты] Показать/Скрыть\tCTRL+ALT+O")
        item = menu.AppendCheckItem(ID_FASTVIEW_TOGGLE, "[Быстрый просмотр] Показать/Скрыть\tCTRL+ALT+R")
        item = menu.AppendCheckItem(ID_SUPPLIED_DATA_TOGGLE, "[Сопутствующие материалы] Показать/Скрыть\tCTRL+ALT+D")
        self.Append(menu, "Вид")

        menu = wx.Menu()
        item = menu.Append(ID_SETTINGS_PM, "Физ. Мех. свойства")
        item = menu.Append(wx.ID_ANY, "Системы координат")
        item = menu.Append(wx.ID_ANY, "Документы")
        item = menu.Append(wx.ID_ANY, "Петротипы")
        self.Append(menu, "Параметры")

        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, "Версия: " + __GEOMECH_VERSION__)
        item.Enable(False)
        menu.AppendSeparator()
        item = menu.Append(wx.ID_ABOUT, "О программе")
        item = menu.AppendCheckItem(ID_OPEN_START_TAB, "Открыть \"Начало работы\"")
        item.Check(True)
        self.Append(menu, "?")
