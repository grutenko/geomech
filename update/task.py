from dataclasses import dataclass
from threading import Thread, Lock, Event
from typing import Callable, Any, TypeAlias
import wx


@dataclass
class Context:
    lock: Lock
    was_cancelled: Event
    progress: int = -1
    total: int = -1
    message: str = None
    status: str = "in_progress"
    exc: Exception = None
    retval: Any = None


_Job: TypeAlias = Callable[[Context], Any]
_Cb: TypeAlias = Callable[[bool, bool, Any], None]


class Task(wx.Frame):
    def __init__(self, title, job: _Job, cb: _Cb):
        self.job = job
        self.cb = cb
        self.thread = None
        self.ctx = None
        self._close_silence = False
        super().__init__(
            None, title=title, size=wx.Size(300, 150), style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
        )
        self.timer = wx.Timer(self)
        sz = wx.BoxSizer(wx.VERTICAL)
        main_sz = wx.BoxSizer(wx.VERTICAL)
        self.msg = wx.StaticText(self, label="Выполняется...")
        main_sz.Add(self.msg, 0, wx.EXPAND)
        self.gauge = wx.Gauge(self, style=wx.GA_HORIZONTAL | wx.GA_PROGRESS, size=wx.Size(300, 50))
        main_sz.Add(self.gauge, 0, wx.EXPAND)
        sz.Add(main_sz, 1, wx.EXPAND | wx.ALL, border=10)
        line = wx.StaticLine(self)
        sz.Add(line, 0, wx.EXPAND)
        btn_sz = wx.StdDialogButtonSizer()
        self.cancel_btn = wx.Button(self, label="Отмена")
        btn_sz.Add(self.cancel_btn)
        sz.Add(btn_sz, 0, wx.RIGHT)
        self.SetSizer(sz)
        self.Layout()
        self.Fit()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.Bind(wx.EVT_TIMER, self.on_alarm)

    def on_alarm(self, event):
        with self.ctx.lock:
            if self.ctx.status == "in_progress":
                if self.ctx.progress == -1:
                    self.gauge.Pulse()
                else:
                    self.gauge.SetRange(self.ctx.total)
                    self.gauge.SetValue(self.ctx.progress)
                self.gauge.Update()
                if self.ctx.message is not None:
                    self.msg.SetLabelText(self.ctx.message)
            else:
                if self.ctx.status == "failed":
                    self.cb(False, False, self.ctx.exc)
                elif self.ctx.status == "success":
                    self.cb(True, self.ctx.was_cancelled.is_set(), self.ctx.retval)
                self._close_silence = True
                self.Destroy()

    def cancel(self):
        rc = wx.MessageBox("Действительно отменить?", "Подтвердите отмену", style=wx.YES | wx.NO | wx.NO_DEFAULT | wx.ICON_ASTERISK)
        if rc == wx.YES:
            self.ctx.was_cancelled.set()

    def on_close(self, event):
        if not self._close_silence:
            self.cancel()
        else:
            event.Skip()

    def on_cancel(self, event):
        self.cancel()

    def run(self):
        self.Show()

        self.ctx = Context(Lock(), Event())

        def _task(job):
            retval = None
            try:
                retval = job(self.ctx)
            except Exception as e:
                with self.ctx.lock:
                    self.ctx.status = "failed"
                    self.ctx.exc = e
            else:
                with self.ctx.lock:
                    self.ctx.status = "success"
                    self.ctx.retval = retval

        self.thread = Thread(target=_task, args=(self.job,))
        self.thread.start()
        self.timer.Start(100)
