import ui
import config
import wx
import form_validators

__DEFAULTS__ = {
    'ip': '127.0.0.1',
    'port': 3501,
    'name': 'geomech'
}

class DatabaseAccess(ui.Ui_DatabaseAccess):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.field_login.SetValidator(form_validators.TextValidator(len_min=1))
        self.field_password.SetValidator(form_validators.TextValidator(len_min=1))
        self.field_ip.SetValidator(form_validators.TextValidator(pattern=r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"))
        self.SetEscapeId(wx.ID_CANCEL)

    def set_ip_value(self, value):
        self.field_ip.SetValue(value)

    def set_port_value(self, value):
        self.field_port.SetValue(value)

    def set_name_value(self, value):
        self.field_name.SetValue(value)

    def set_login_value(self, value):
        self.field_login.SetValue(value)

    def set_password_value(self, value):
        self.field_password.SetValue(value)
    
    def get_ip(self):
        return self.field_ip.GetValue()
    
    def get_port(self):
        return self.field_port.GetValue()
    
    def get_name(self):
        return self.field_name.GetValue()
    
    def get_login(self):
        return self.field_login.GetValue()
    
    def get_password(self):
        return self.field_password.GetValue()
    
    def get_dsn(self):
        return "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            self.get_login(), 
            self.get_password(), 
            self.get_ip(), 
            self.get_port(), 
            self.get_name())