import wx


from ui.widgets.grid_new import *
from ui.widgets.grid_new.widget import Column
from ui.windows.main.identity import Identity
from ui.class_config_provider import ClassConfigProvider
from ui.icon import get_art
from .widget import *
from dataclasses import dataclass, field


class BaseEditor(wx.Panel):
    def __init__(
        self,
        parent,
        title,
        identity,
        model,
        menubar,
        toolbar,
        statusbar,
    ):
        super().__init__(parent.get_native())
        self.o = identity.o
        self._identity = identity
        self._title = title

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.editor = GridEditor(self, model, menubar, toolbar, statusbar)
        main_sizer.Add(self.editor, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()

        self._bind_all()

    def _bind_all(self):
        self.editor.Bind(EVT_GRID_EDITOR_STATE_CHANGED, self._on_editor_state_changed)

    def _on_editor_state_changed(self, event):
        wx.PostEvent(self, EditorNBStateChangedEvent(target=self))

    def get_identity(self) -> Identity | None:
        return self._identity

    def get_title(self) -> str:
        return self._title

    def get_icon(self):
        return 'data-sheet', get_icon('data-sheet', scale_to=16)

    def can_save(self) -> bool:
        return self.editor.can_save()

    def can_copy(self) -> bool:
        return self.editor.can_copy()

    def can_cut(self) -> bool:
        return self.editor.can_cut()

    def can_paste(self) -> bool:
        return self.editor.can_paste()

    def can_undo(self) -> bool:
        return self.editor.can_undo()

    def can_redo(self) -> bool:
        return self.editor.can_redo()

    def save(self):
        self.editor.save()

    def copy(self):
        self.editor.copy()

    def cut(self):
        self.editor.cut()

    def paste(self):
        self.editor.paste()

    def undo(self):
        self.editor.undo()

    def redo(self):
        self.editor.redo()

    def is_changed(self) -> bool:
        return self.editor.is_changed()

    def on_select(self):
        self.editor.apply_controls()

    def on_deselect(self):
        self.editor.remove_controls()

    def on_close(self) -> bool:
        if self.can_save():
            ret = wx.MessageBox(
                "Редактор имеет несохраненные изменения. Сохранить?",
                "Подтвердите закрытие",
                style=wx.YES | wx.NO | wx.CANCEL | wx.YES_DEFAULT | wx.ICON_INFORMATION,
            )
            if ret == wx.CANCEL:
                return False
            elif ret == wx.YES:
                try:
                    self.save()
                except:
                    return False
        self.editor.end()
        return True

    def is_read_only(self):
        return False
