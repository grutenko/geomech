import wx

from ui.icon import get_art

class MainToolbar(wx.ToolBar):
    def __init__(self, parent):
        super().__init__(parent, style=wx.TB_FLAT | wx.TB_HORZ_TEXT)

        tool = self.AddTool(wx.ID_SAVE, "Сохранить", get_art(wx.ART_FILE_SAVE, scale_to=16), "Сохранить активный редактор")
        tool.Enable(False)
        self.AddSeparator()
        tool = self.AddTool(wx.ID_COPY, "Копировать", get_art(wx.ART_COPY, scale_to=16), "Копировать")
        tool.Enable(False)
        tool = self.AddTool(wx.ID_CUT, "Вырезать", get_art(wx.ART_CUT, scale_to=16), "Вырезать")
        tool.Enable(False)
        tool = self.AddTool(wx.ID_PASTE, "Вставить", get_art(wx.ART_PASTE, scale_to=16), "Вставить")
        tool.Enable(False)
        self.AddSeparator()
        tool = self.AddTool(wx.ID_UNDO, "Отменить", get_art(wx.ART_UNDO, scale_to=16), "Отменить")
        tool.Enable(False)
        tool = self.AddTool(wx.ID_REDO, "Вернуть", get_art(wx.ART_REDO, scale_to=16), "Вернуть")
        tool.Enable(False)

        self.Realize()