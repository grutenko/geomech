import wx
import typing
import database
import resources
import wx.lib.newevent

from .ui.relation_selector import (
    UI_RelationSelector,
    UI_RelationSelector_Dialog
)

__xRelationSelectorSelect__ = wx.NewEventType()

class xRelationSelectorSelect(wx.PyEvent):
    def __init__(self, **kw):
        wx.PyEvent.__init__(self)
        self.SetEventType(__xRelationSelectorSelect__)
        self._getAttrDict().update(kw)

EVT_RELATION_SELECTOR_SELECT = wx.PyEventBinder(__xRelationSelectorSelect__)

_T = typing.TypeVar('_T', bound=database.Base)

class _RelationSelectorDialog(UI_RelationSelector_Dialog, typing.Generic[_T]):
    _entities = []
    _all_entities = []
    _new_entity: _T = None
    _name_gen: typing.Callable[[_T], str]

    def __init__(self, entities, name_gen, *args, **kwds):
        super().__init__(*args, **kwds)
        self._entities = entities
        self._all_entities = entities
        self._name_gen = name_gen
        self.entities.Bind(wx.EVT_LEFT_UP, self.__on_select)
        self.search.Bind(wx.EVT_SEARCH, self.__on_search)
        self.search.Bind(wx.EVT_SEARCH_CANCEL, self.__on_search_cancel)
        self.__render()

    def __on_search_cancel(self, event):
        self._entities = self._all_entities
        self.__render()

    def __on_search(self, event):
        q = self.search.GetValue()
        self._entities = list(filter(lambda e: self._name_gen(e).find(q) != -1, self._all_entities))
        self.__render()

    def __on_select(self, event):
        self.__update_controls_state()

    def __render(self):
        self.entities.Clear()
        for item in self._entities:
            self.entities.Append(self._name_gen(item))
        self.__update_controls_state()

    def select(self, e: _T):
        for i, item in enumerate(self._entities):
            if item.RID == e.RID:
                self.entities.Select(i)
                break
        self.__update_controls_state()

    def get_selected_entity(self):
        return self._entities[self.entities.GetSelection()]
    
    def __update_controls_state(self):
        self.button_OK.Enable(self.entities.GetSelection() != -1)


class RelationSelector(UI_RelationSelector, typing.Generic[_T]):
    _selected_entity: _T = None
    _new_entity: _T = None

    _table_class: typing.Type[_T] = None
    _name_gen: typing.Callable[[_T], str] = None

    _can_create = False
    _editor = None

    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)

        self.btn_select.Bind(wx.EVT_BUTTON, self.__on_click)
        self.btn_add.Bind(wx.EVT_BUTTON, self.__on_create_click)
        self.btn_remove.Bind(wx.EVT_BUTTON, self.__on_remove_click)

    def __on_remove_click(self, event):
        self._selected_entity = None
        self._new_entity = None
        self.__update_controls_state()

    def __on_create_click(self, event):
        def _on_save(e):
            self._new_entity = e
            self._selected_entity = e
            self.__update_controls_state()
            evt = xRelationSelectorSelect(entity=self._selected_entity, is_new=True)
            wx.PostEvent(self, evt)
        w = self._editor(entity=None, on_save=_on_save, parent=self)
        w.Show()

    def set_table_class(self, table_class: typing.Type[_T]):
        self._table_class = table_class
        return self

    def set_name_generator(self, name_gen: typing.Callable[[_T], str]):
        self._name_gen = name_gen
        return self

    def set_can_create(self, can_create: bool):
        self._can_create = can_create
        self.__update_controls_state()
        return self

    def set_editor(self, editor):
        self._editor = editor
        return self

    def select(self, e: _T):
        self._selected_entity = e
        self.__update_controls_state()

    def __update_controls_state(self):
        label = "<Не выбрано>"
        if not self._selected_entity is None:
            label = self._name_gen(self._selected_entity)
            if self._selected_entity == self._new_entity:
                label = "[Новый] " + label
        self.entity_name.SetLabel(label)
        self.btn_add.Enable(self._new_entity == None and self._selected_entity == None and self._can_create)
        if not self._can_create:
            self.btn_add.SetBitmap(wx.Bitmap(resources.resource_path("icons/padlock.png")))
        self.btn_select.Enable(self._new_entity == None)
        self.btn_remove.Enable(self._selected_entity != None)

    def __on_click(self, event):
        if self._new_entity != None:
            return
        entities = database.get_session().query(self._table_class).all()
        w = _RelationSelectorDialog(
            entities=entities,
            name_gen=self._name_gen,
            parent=self.GetParent())
        if self._selected_entity != None:
            w.select(self._selected_entity)
        if w.ShowModal() == wx.ID_OK:
            self._selected_entity = w.get_selected_entity()
            self.__update_controls_state()
            evt = xRelationSelectorSelect(entity=self._selected_entity, is_new=False)
            wx.PostEvent(self, evt)

    def get_selected_entity(self):
        return self._selected_entity
    
    def selected_entity_is_new(self):
        return self._new_entity != None