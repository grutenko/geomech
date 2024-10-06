import wx

from ui.icon import get_art, get_icon

class MainToolbar(wx.ToolBar):
    def __init__(self, parent):
        super().__init__(parent, style=wx.TB_DEFAULT_STYLE | wx.TB_HORZ_TEXT | wx.TB_DOCKABLE | wx.TB_FLAT)

        tool = self.AddTool(wx.ID_SAVE, "Сохранить", get_icon("save", scale_to=16), "Сохранить активный редактор")
        tool.Enable(False)
        self.AddSeparator()
        tool = self.AddTool(wx.ID_COPY, "Копировать", get_icon("copy", scale_to=16), "Копировать")
        tool.Enable(False)
        tool = self.AddTool(wx.ID_CUT, "Вырезать", get_icon("cut", scale_to=16), "Вырезать")
        tool.Enable(False)
        tool = self.AddTool(wx.ID_PASTE, "Вставить", get_icon("paste", scale_to=16), "Вставить")
        tool.Enable(False)
        self.AddSeparator()
        tool = self.AddTool(wx.ID_UNDO, "Отменить", get_icon("undo", scale_to=16), "Отменить")
        tool.Enable(False)
        tool = self.AddTool(wx.ID_REDO, "Вернуть", get_icon("redo", scale_to=16), "Вернуть")
        tool.Enable(False)

        self.Realize()