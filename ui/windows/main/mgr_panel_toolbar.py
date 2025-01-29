import wx

from ui.icon import get_icon

ID_TOGGLE_OBJECTS = wx.ID_HIGHEST + 150
ID_TOGGLE_FASTVIEW = ID_TOGGLE_OBJECTS + 1
ID_TOGGLE_SUPPLIED_DATA = ID_TOGGLE_OBJECTS + 2
ID_TOGGLE_COORD_SYSTEM = ID_TOGGLE_OBJECTS + 3
ID_TOGGLE_DISCHARGE = ID_TOGGLE_OBJECTS + 4
ID_TOGGLE_PM = ID_TOGGLE_OBJECTS + 5
ID_TOGGLE_ROCK_BURST = ID_TOGGLE_OBJECTS + 6
ID_TOGGLE_CONTAINER = ID_TOGGLE_OBJECTS + 7
ID_TOGGLE_DEVIATION = ID_TOGGLE_OBJECTS + 8


class MgrPanelToolbar(wx.ToolBar):
    def __init__(self, parent):
        super().__init__(parent, style=wx.TB_DEFAULT_STYLE | wx.TB_FLAT | wx.TB_LEFT | wx.TB_RIGHT)

        tool = self.AddTool(ID_TOGGLE_CONTAINER, "База данных", get_icon("book-stack"))
        menu = wx.Menu()
        item = menu.AppendCheckItem(ID_TOGGLE_DISCHARGE, "Разгрузочные замеры", "Показать/Скрыть разгрузка")
        item.SetBitmap(get_icon("check"))
        item = menu.AppendCheckItem(ID_TOGGLE_PM, "[Физ. Мех. Свойства] Наборы замеров (договоры)", "Показать/Скрыть Физ. мех. свойства")
        item.SetBitmap(get_icon("check"))
        item = menu.AppendCheckItem(ID_TOGGLE_ROCK_BURST, "Горные удары", "Показать/Скрыть Горные удары")
        item.SetBitmap(get_icon("check"))
        self._dropdown = menu
        self.AddSeparator()
        tool = self.AddCheckTool(
            ID_TOGGLE_OBJECTS,
            "Объекты",
            get_icon("hierarchy"),
            shortHelp="Показать/Скрыть объекты",
        )
        tool = self.AddCheckTool(
            ID_TOGGLE_FASTVIEW,
            "Быстрый просмотр",
            get_icon("show-property", scale_to=16),
            shortHelp="Показать/Скрыть быстрый просмотр",
        )
        tool = self.AddCheckTool(
            ID_TOGGLE_SUPPLIED_DATA,
            "Сопутствующие материалы",
            get_icon("versions", scale_to=16),
            shortHelp="Показать/Скрыть сопутствующие материалы",
        )
        self.AddStretchableSpace()

        tool = self.AddCheckTool(
            ID_TOGGLE_DEVIATION,
            "Инструмент: Панель отклонений",
            get_icon("deviation", scale_to=16),
            shortHelp="Показать/Скрыть Панель отклонений",
        )

        self.Realize()
