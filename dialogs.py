import ui
import wx
import form_validators
from database import Credentials

__DEFAULTS__ = {
    'ip': '127.0.0.1',
    'port': 3501,
    'name': 'geomech'
}

class DatabaseAccess(ui.Ui_DatabaseAccess):
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.field_user.SetValidator(form_validators.TextValidator(len_min=1))
        self.field_password.SetValidator(form_validators.TextValidator(len_min=1))
        self.field_host.SetValidator(form_validators.TextValidator(pattern=r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"))
        self.SetEscapeId(wx.ID_CANCEL)

    credentials: Credentials = Credentials()

    def setCredentials(self, credentials: Credentials):
        self.credentials = credentials
        if credentials.user != None:
            self.field_user.SetValue(credentials.user)
        if credentials.password != None:
            self.field_password.SetValue(credentials.password)
        if credentials.host != None:
            self.field_host.SetValue(credentials.host)
        if credentials.port != None:
            self.field_port.SetValue(credentials.port)
        if credentials.database != None:
            self.field_database.SetValue(credentials.database)

    def getCredentials(self) -> Credentials:
        c = self.credentials
        c.user = self.field_user.GetValue()
        c.password = self.field_password.GetValue()
        c.host = self.field_host.GetValue()
        c.port = self.field_port.GetValue()
        c.database = self.field_database.GetValue()
        return c

    