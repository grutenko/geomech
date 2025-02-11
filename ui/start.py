import os

import wx
from pony.orm import Database

import config
from ui.icon import get_icon

from .validators import TextValidator


class StartDialog(wx.Dialog):
    def __init__(self):
        super().__init__(
            None,
            wx.ID_ANY,
            'База данных "Геомеханика".',
            style=wx.DEFAULT_DIALOG_STYLE,
        )
        self.SetIcon(wx.Icon(get_icon("logo@16")))
        self.CenterOnScreen()

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        grid_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="Логин*")
        grid_sizer.Add(label, 0, wx.EXPAND)
        self.field_login = wx.TextCtrl(self, size=wx.Size(320, -1))
        self.field_login.SetValidator(TextValidator("поле не должно быть пустым", lenMin=1))
        grid_sizer.Add(self.field_login, 0, wx.EXPAND | wx.BOTTOM, border=10)
        label = wx.StaticText(self, label="Пароль*")
        grid_sizer.Add(label, 0, wx.EXPAND)
        self.field_password = wx.TextCtrl(self, size=wx.Size(320, -1), style=wx.TE_PASSWORD)
        self.field_password.SetValidator(TextValidator("поле не должно быть пустым", lenMin=1))
        grid_sizer.Add(self.field_password, 0, wx.EXPAND | wx.BOTTOM, border=10)
        main_sizer.Add(grid_sizer, 1, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=10)
        collapse = wx.CollapsiblePane(self, label="Параметры подключения")
        collapse_pane = collapse.GetPane()
        collapse_sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(collapse_pane, label="Хост*")
        collapse_sizer.Add(label, 0, wx.LEFT | wx.RIGHT, border=10)
        self.field_host = wx.TextCtrl(collapse_pane)
        self.field_host.SetValidator(TextValidator("поле не должно быть пустым", lenMin=1))
        collapse_sizer.Add(self.field_host, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)

        label = wx.StaticText(collapse_pane, label="Порт*")
        collapse_sizer.Add(label, 0, wx.LEFT | wx.RIGHT, border=10)
        self.field_port = wx.SpinCtrl(collapse_pane, max=1000000)
        collapse_sizer.Add(self.field_port, 0, wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)

        label = wx.StaticText(collapse_pane, label="База данных*")
        collapse_sizer.Add(label, 0, wx.LEFT | wx.RIGHT, border=10)
        self.field_database = wx.TextCtrl(collapse_pane)
        self.field_database.SetValidator(TextValidator("поле не должно быть пустым", lenMin=1))
        collapse_sizer.Add(
            self.field_database,
            0,
            wx.EXPAND | wx.BOTTOM | wx.LEFT | wx.RIGHT,
            border=10,
        )

        collapse_pane.SetSizer(collapse_sizer)
        main_sizer.Add(collapse, 0, wx.EXPAND | wx.BOTTOM, border=10)

        btns = wx.StdDialogButtonSizer()
        self.btn_login = wx.Button(self, label="Войти")
        self.btn_login.SetDefault()
        btns.Add(self.btn_login, 0, wx.EXPAND)
        main_sizer.Add(btns, 0, wx.ALIGN_RIGHT | wx.BOTTOM | wx.LEFT | wx.RIGHT, border=10)

        self.SetSizer(main_sizer)

        self.Layout()
        self.Fit()

        self._init()

        self.SetEscapeId(wx.ID_CANCEL)
        self.SetAffirmativeId(wx.ID_OK)

        self.btn_login.Bind(wx.EVT_BUTTON, self._on_login)
        self._old_config_version = False

    def _init(self):
        if "GEOMECH_DEFAULT_HOST" in os.environ:
            host = os.environ["GEOMECH_DEFAULT_HOST"]
        else:
            host = "127.0.0.1"
        if "GEOMECH_DEFAULT_PORT" in os.environ:
            port = str(os.environ["GEOMECH_DEFAULT_PORT"])
        else:
            port = 5432
        if "GEOMECH_DEFAULT_DATABASE" in os.environ:
            database = os.environ["GEOMECH_DEFAULT_DATABASE"]
        else:
            database = "geomech"
        self.field_host.SetValue(host)
        self.field_port.SetValue(port)
        self.field_database.SetValue(database)
        data = config.get("database")
        if data != None:
            if "login" not in data:
                login = data.user
                self._old_config_version = True
            else:
                login = data.login
            self.field_login.SetValue(login)
            self.field_password.SetValue(data.password)
            self.field_host.SetValue(data.host)
            self.field_port.SetValue(data.port)
            self.field_database.SetValue(data.database)

    def _on_login(self, event):
        if not self.Validate():
            return

        self.btn_login.Disable()

        data = {
            "login": self.field_login.GetValue(),
            "password": self.field_password.GetValue(),
            "database": self.field_database.GetValue(),
            "host": self.field_host.GetValue(),
            "port": self.field_port.GetValue(),
        }
        try:
            db = Database()
            db.bind(
                "postgres",
                user=data["login"],
                password=data["password"],
                host=data["host"],
                database=data["database"],
                port=str(data["port"]),
            )
            db.disconnect()
        except Exception as e:
            wx.MessageBox(
                "Введены неверные доступы к базе данных.\n%s" % str(e),
                "Ошибка подключения к базе данных.",
                style=wx.ICON_ERROR | wx.OK | wx.OK_DEFAULT,
            )
        else:
            config.set("database", data, flush_now=True)
            self.EndModal(wx.ID_OK)
        finally:
            self.btn_login.Enable()
