import wx
import typing
import re

class _Validator(wx.Validator):
    _message: str
    _title: str
    _skip_if_disabled: bool

    def __init__(self, 
                 title: str = u"Ошибка!",
                 message: str = u"Поле заполнено неверно.",
                 skip_if_disabled: bool = True):
        super().__init__()
        self._message = message
        self._title = title
        self._skip_if_disabled = skip_if_disabled

    def TransferToWindow(self):
        return True
    
    def TransferFromWindow(self):
        return True
    
    def _x_validate(self, ctrl: wx.Control):
        raise NotImplementedError('Implement _x_validate in %s.' % (self.__class__.__name__))
    
    def Validate(self, parent):
        ctrl: wx.Control = self.GetWindow()
        if self._skip_if_disabled and not ctrl.IsEnabled():
            return True
        
        if not self._x_validate(ctrl):
            wx.MessageBox(self._message, self._title)
            ctrl.SetBackgroundColour("red")
            ctrl.SetFocus()
            ctrl.Refresh()
            return False
        else:
            ctrl.SetBackgroundColour(
                 wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
            ctrl.Refresh()
            return True
        
    def Clone(self):
        raise NotImplementedError("Implement Clone in %s" % (self.__class__.__name__))
    
class TextValidator(_Validator):
    _len_min: typing.Optional[int]
    _len_max: typing.Optional[int]
    _pattern: typing.Optional[str]

    def __init__(self, 
                 *args,
                 len_min: typing.Optional[int] = 0, 
                 len_max: typing.Optional[int] = None, 
                 pattern: typing.Optional[str] = None,
                 **kwds):
        super().__init__(*args, **kwds)
        self._len_min = len_min
        self._len_max = len_max
        self._pattern = pattern

    def _x_validate(self, ctrl: wx.Control):
        ctrl: wx.TextCtrl
        _valid = True
        if not self._len_min is None:
            _valid = _valid and len(ctrl.GetValue()) >= self._len_min
        if not self._len_max is None:
            _valid = _valid and len(ctrl.GetValue()) <= self._len_max
        if not self._pattern is None:
            _valid = _valid and not re.match(self._pattern, ctrl.GetValue()) is None
        return _valid
    
    def Clone(self):
        c = TextValidator()
        c.__dict__.update(self.__dict__)
        return c
    
class NumericValidator(_Validator):
    _min: typing.Optional[float]
    _max: typing.Optional[float]
    _is_positive: typing.Optional[bool]

    def __init__(self,
                 *args,
                 min: typing.Optional[float] = None,
                 max: typing.Optional[float] = None,
                 is_positive: typing.Optional[bool] = None,
                 **kwds):
        super().__init__(*args, **kwds)
        self._min = min
        self._max = max
        self._is_positive = is_positive

    def _x_validate(self, ctrl: wx.SpinCtrl):
        _valid = True
        if not self._min is None:
            _valid = _valid and ctrl.GetValue() >= self._min
        if not self._max is None:
            _valid = _valid and ctrl.GetValue() <= self._max
        if not self._is_positive is None:
            _valid = _valid and ctrl.GetValue() > 0
        return _valid

    def Clone(self):
        c = NumericValidator()
        c.__dict__.update(self.__dict__)
        return c
    
class ChoiceValidator(_Validator):
    _should_selected: bool

    def __init__(self, should_selected: bool = True, *args, **kwds):
        self._should_selected = should_selected
        super().__init__(*args, **kwds)

    def _x_validate(self, ctrl: wx.Choice):
        _valid = True
        if not self._should_selected is None:
            _valid = _valid and ctrl.GetSelection() != 0
        return _valid

    def Clone(self):
        c = ChoiceValidator()
        c.__dict__.update(self.__dict__)
        return c
    
class DateValidator(_Validator):
    _min: wx.DateTime
    _max: wx.DateTime

    def __init__(self, min: wx.DateTime = None, max: wx.DateTime = None, *args, **kwds):
        self._min = min
        self._max = max
        super().__init__(*args, **kwds)

    def _x_validate(self, ctrl):
        if type(ctrl) == wx.adv.CalendarCtrl:
            date = ctrl.GetDate()
        elif type(ctrl) == wx.adv.DatePickerCtrl:
            date = ctrl.GetValue()
        else:
            raise Exception('Doesnt fit widget for date validation.')
        _valid = True
        if not self._min is None:
            _valid = _valid and self._min <= date
        if not self._max is None:
            _valid = _valid and self._max >= date
        return _valid
    
    def Clone(self):
        c = DateValidator()
        c.__dict__.update(self.__dict__)
        return c