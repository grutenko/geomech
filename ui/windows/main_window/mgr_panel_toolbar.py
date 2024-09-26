import wx


from ui.icon import get_art, get_icon

ID_TOGGLE_OBJECTS = wx.ID_HIGHEST + 150
ID_TOGGLE_FASTVIEW = ID_TOGGLE_OBJECTS + 1
ID_TOGGLE_SUPPLIED_DATA = ID_TOGGLE_OBJECTS + 2
ID_TOGGLE_COORD_SYSTEM = ID_TOGGLE_OBJECTS + 3


class MgrPanelToolbar(wx.ToolBar):
    def __init__(self, parent):
        super().__init__(parent, style=wx.TB_DEFAULT_STYLE | wx.TB_RIGHT | wx.TB_FLAT)

        tool = self.AddCheckTool(
            ID_TOGGLE_OBJECTS,
            "Объекты",
            get_art(wx.ART_HELP_BOOK, scale_to=16),
            shortHelp="Показать/Скрыть объекты",
        )
        tool = self.AddCheckTool(
            ID_TOGGLE_FASTVIEW,
            "Быстрый просмотр",
            get_art(wx.ART_INFORMATION, scale_to=16),
            shortHelp="Показать/Скрыть быстрый просмотр",
        )
        tool = self.AddCheckTool(
            ID_TOGGLE_SUPPLIED_DATA,
            "Сопутствующие материалы",
            get_art(wx.ART_FOLDER, scale_to=16),
            shortHelp="Показать/Скрыть сопутствующие материалы",
        )
        self.AddSeparator()

        self.Realize()
