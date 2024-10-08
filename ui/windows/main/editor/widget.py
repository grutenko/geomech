import pubsub.pub
import wx
from wx.lib.agw.flatnotebook import *
from typing import Protocol, runtime_checkable, Optional, Tuple
import pubsub

from database import *

from ui.class_config_provider import ClassConfigProvider

import wx
import wx.lib.newevent
from wx.lib.agw.flatnotebook import *
from ui.windows.main.identity import Identity

__CONFIG_VERSION__ = 1


@runtime_checkable
class EditorProto(Protocol):
    def get_identity(self) -> Identity | None: ...
    def get_title(self) -> str: ...
    def get_icon(self) -> Tuple[str, wx.Bitmap]: ...
    def can_save(self) -> bool: ...
    def can_copy(self) -> bool: ...
    def can_cut(self) -> bool: ...
    def can_paste(self) -> bool: ...
    def can_undo(self) -> bool: ...
    def can_redo(self) -> bool: ...
    def save(self): ...
    def copy(self): ...
    def cut(self): ...
    def paste(self): ...
    def undo(self): ...
    def redo(self): ...
    def on_select(self): ...
    def on_deselect(self): ...
    def on_close(self) -> bool: ...
    def is_changed(self) -> bool: ...


EditorNBStateChangedEvent, EVT_ENB_STATE_CHANGED = wx.lib.newevent.NewEvent()
EditorClosedEvent, EVT_ENB_EDITOR_CLOSED = wx.lib.newevent.NewEvent()
EditorSavedEvent, EVT_ENB_EDITOR_SAVED = wx.lib.newevent.NewEvent()


class BasicEditor(wx.Panel):
    def __init__(self, notebook, title="Редактор", identity=None):
        super().__init__(notebook.get_native())
        self._identity = identity
        self._title = title

    def notify_state_changed(self):
        wx.PostEvent(self, EditorNBStateChangedEvent(target=self))

    def get_identity(self) -> Identity | None:
        return self._identity

    def get_title(self) -> str:
        return self._title

    def get_icon(self):
        return None

    def can_save(self) -> bool:
        return False

    def can_copy(self) -> bool:
        return False

    def can_cut(self) -> bool:
        return False

    def can_paste(self) -> bool:
        return False

    def can_undo(self) -> bool:
        return False

    def can_redo(self) -> bool:
        return False

    def save(self): ...
    def copy(self): ...
    def cut(self): ...
    def paste(self): ...
    def undo(self): ...
    def redo(self): ...
    def on_select(self): ...
    def on_deselect(self): ...
    def on_close(self) -> bool:
        return True

    def is_changed(self) -> bool:
        return False

    def is_read_only(self) -> bool:
        return False


class EditorNotebook(wx.Panel):
    _instance = None

    @classmethod
    def get_instance(cls):
        return cls._instance

    def __init__(self, parent, menubar, statusbar, toolbar):
        super().__init__(parent)
        self._config_provider = ClassConfigProvider(
            __name__ + "." + self.__class__.__name__, __CONFIG_VERSION__
        )

        self.menubar = menubar
        self.statusbar = statusbar
        self.toolbar = toolbar

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._image_list = wx.ImageList(16, 16)
        self._icons = {}
        self.notebook = FlatNotebook(
            self,
            agwStyle=FNB_X_ON_TAB | FNB_VC8 | FNB_NO_X_BUTTON | FNB_NO_NAV_BUTTONS,
        )
        self.notebook.AssignImageList(self._image_list)
        self._native_ = self.notebook
        main_sizer.Add(self.notebook, 1, wx.EXPAND)
        self.SetSizer(main_sizer)

        self.Layout()

        self.__class__._instance = self

        self._bind_all()
        self._closed_page_identity = None

    def _bind_all(self):
        self.notebook.Bind(EVT_FLATNOTEBOOK_PAGE_CHANGED, self._on_page_changed, self.notebook)
        self.notebook.Bind(EVT_FLATNOTEBOOK_PAGE_CLOSING, self._on_page_closing, self.notebook)
        self.notebook.Bind(EVT_FLATNOTEBOOK_PAGE_CLOSED, self._on_page_closed, self.notebook)

    def get_by_identity(self, _id):
        for i in range(self._native_.GetPageCount()):
            page = self._native_.GetPage(i)
            if page.get_identity() == _id:
                return i, page
        return -1, None

    def select_by_identity(self, _id):
        index, old_page = self.get_by_identity(_id)
        if index != -1:
            old_index = self._native_.GetSelection()
            self._native_.SetSelection(index)
            self._notify_selection_changed(index, old_index)
            return True
        return False
    
    def select_by_index(self, index):
        if index >= 0 and index < self._native_.GetPageCount():
            old_index = self._native_.GetSelection()
            self._native_.SetSelection(index)
            self._notify_selection_changed(index, old_index)

    def get_native(self) -> FlatNotebook:
        return self._native_

    def get_pane_info(self) -> str | None:
        return self._config_provider["aui_pane_info"]

    def save_pane_info(self, info: str):
        self._config_provider["aui_pane_info"] = info
        self._config_provider.flush()

    def _on_page_closing(self, event):
        index = event.GetSelection()
        if index != -1:
            if not self.notebook.GetPage(index).on_close():
                event.Veto()
            else:
                self.notebook.GetPage(index).on_deselect()
                self._closed_page_identity = self.notebook.GetPage(index).get_identity()

    def _on_page_closed(self, event):
        wx.PostEvent(self, EditorNBStateChangedEvent(target=self))
        wx.PostEvent(
            self, EditorClosedEvent(target=self, identity=self._closed_page_identity)
        )

    def _on_page_changed(self, event):
        self._notify_selection_changed(event.GetSelection(), event.GetOldSelection())

    def _notify_selection_changed(self, new_index, old_index):
        if old_index != -1:
            self.notebook.GetPage(old_index).on_deselect()
        if new_index != -1:
            self.notebook.GetPage(new_index).on_select()
        wx.PostEvent(self, EditorNBStateChangedEvent(target=self))

    def _apply_icon(self, name, bitmap):
        if name not in self._icons:
            self._icons[name] = self._image_list.Add(bitmap)
        return self._icons[name]

    def _apply_editor(self, index, editor):
        icon = editor.get_icon()
        if icon != None:
            self._native_.SetPageImage(index, self._apply_icon(icon[0], icon[1]))
        title = (
            editor.get_title()
            if len(editor.get_title()) < 50
            else editor.get_title()[:50] + "..."
        )
        if editor.is_read_only():
            title = "[Чтение] " + title
        self._native_.SetPageText(index, title)
        if editor.is_changed():
            self._native_.SetPageText(index, "[*] " + self._native_.GetPageText(index))
            self._native_.SetPageTextColour(index, wx.Colour(40, 150, 40))
        else:
            self._native_.SetPageTextColour(index, wx.Colour(20, 20, 20))

    def close_editor(self, editor: EditorProto):
        index = self._native_.GetPageIndex(editor)
        if index != -1:
            self._native_.DeletePage(index)

    def add_editor(self, editor: EditorProto):
        self._native_.AddPage(editor, "Вкладка")
        self._apply_editor(self._native_.GetPageCount() - 1, editor)
        old_selection = self.notebook.GetSelection()
        self.notebook.SetSelection(self.notebook.GetPageCount() - 1)
        self._notify_selection_changed(self.notebook.GetSelection(), old_selection)
        editor.Bind(EVT_ENB_STATE_CHANGED, self._on_page_state_changed)
        wx.PostEvent(self, EditorNBStateChangedEvent(target=self))

    def _on_page_state_changed(self, event):
        index = self.notebook.GetPageIndex(event.target)
        self._apply_editor(index, self.notebook.GetPage(index))
        if index != -1 and self.notebook.GetSelection() == index:
            wx.PostEvent(self, EditorNBStateChangedEvent(target=self))

    def can_save(self):
        return (
            self._native_.GetPageCount() > 0
            and self._native_.GetPage(self._native_.GetSelection()).can_save()
        )

    def can_copy(self):
        return (
            self._native_.GetPageCount() > 0
            and self._native_.GetPage(self._native_.GetSelection()).can_copy()
        )

    def can_cut(self):
        return (
            self._native_.GetPageCount() > 0
            and self._native_.GetPage(self._native_.GetSelection()).can_cut()
        )

    def can_paste(self):
        return (
            self._native_.GetPageCount() > 0
            and self._native_.GetPage(self._native_.GetSelection()).can_paste()
        )

    def can_undo(self):
        return (
            self._native_.GetPageCount() > 0
            and self._native_.GetPage(self._native_.GetSelection()).can_undo()
        )

    def can_redo(self):
        return (
            self._native_.GetPageCount() > 0
            and self._native_.GetPage(self._native_.GetSelection()).can_redo()
        )

    def save(self):
        _saved = False
        _editor = None
        if self._native_.GetPageCount() > 0:
            _editor = self._native_.GetPage(self._native_.GetSelection())
            _saved = _editor.save()
        if _saved:
            wx.PostEvent(self, EditorSavedEvent(target=self, editor=_editor))
            pubsub.pub.sendMessage("editor.saved", target=self, editor=_editor)
        

    def copy(self):
        if self._native_.GetPageCount() > 0:
            self._native_.GetPage(self._native_.GetSelection()).copy()

    def cut(self):
        if self._native_.GetPageCount() > 0:
            self._native_.GetPage(self._native_.GetSelection()).cut()

    def paste(self):
        if self._native_.GetPageCount() > 0:
            self._native_.GetPage(self._native_.GetSelection()).paste()

    def undo(self):
        if self._native_.GetPageCount() > 0:
            self._native_.GetPage(self._native_.GetSelection()).undo()

    def redo(self):
        if self._native_.GetPageCount() > 0:
            self._native_.GetPage(self._native_.GetSelection()).redo()

    def go_next_editor(self):
        if self.can_go_next_editor():
            old_index = self.notebook.GetSelection()
            if old_index < self.notebook.GetPageCount() - 1:
                new_index = old_index + 1
            else:
                new_index = 0
            self.notebook.SetSelection(new_index)
            self._notify_selection_changed(new_index, old_index)

    def go_prev_editor(self):
        if self.can_go_prev_editor():
            old_index = self.notebook.GetSelection()
            if old_index > 0:
                new_index = old_index - 1
            else:
                new_index = self.notebook.GetPageCount() - 1
            self.notebook.SetSelection(new_index)
            self._notify_selection_changed(new_index, old_index)

    def can_go_next_editor(self):
        return self.notebook.GetPageCount() > 1

    def can_go_prev_editor(self):
        return self.notebook.GetPageCount() > 1

    def close(self) -> bool:
        self.notebook.DeletePage(self.notebook.GetSelection())

    def can_close(self) -> bool:
        return self.notebook.GetPageCount() > 0
