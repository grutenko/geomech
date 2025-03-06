import urllib.request
import urllib.error
import logging
import dataclasses
import re


@dataclasses.dataclass
class Context:
    url: str
    appname: str
    version: str
    exe_filename: str


__ctx__ = None


def update_init(url, appname, version, exe_filename):
    global __ctx__
    __ctx__ = Context(url, appname, version, exe_filename)


def cmp_version(ver0, ver1):
    ver0_list = list(map(lambda x: int(x), ver0.split(".")))
    ver1_list = list(map(lambda x: int(x), ver1.split(".")))
    for i in range(0, 4):
        if ver0_list[i] > ver1_list[i]:
            return 1
        elif ver0_list[i] < ver1_list[i]:
            return -1
    return 0


def update_check_status():
    global __ctx__
    url = "%s/%s-latest-version.txt" % (__ctx__.url, __ctx__.appname)
    try:
        resp = urllib.request.urlopen(url)
        if resp.getcode() != 200:
            raise Exception("Invalid http response code for %s - %d" % (url, resp.getcode()))
        latest = resp.read().decode("utf-8")
        if re.match(r"^\d.\d.\d.\d\s*$", __ctx__.version) is not None:
            raise Exception("Update invalid target version string: %s" % __ctx__.version)
        if re.match(r"^\d.\d.\d.\d\s*$", latest) is not None:
            raise Exception("Update invalid latest version string: %s" % latest)
    except Exception as e:
        logging.error("Update: %s" % e.__str__())
        print("Update: %s" % e.__str__())
        raise e
    if cmp_version(latest, __ctx__.version) == 1:
        return "AVAILABLE"

    return "NOT_AVAILABLE"


import wx
from .task import Task, Context as TaskContext
import threading
import time
import shutil
import random
import string
import os
import bsdiff4
import tempfile


def generate_random_string(length):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def _job(ctx: TaskContext):
    global __ctx__
    ctx.message = "Копирование исполняемого файла..."
    ctx.progress = -1
    ctx.total = -1
    temp_exe = __ctx__.exe_filename + "-temp-" + generate_random_string(4)
    shutil.copy(__ctx__.exe_filename, temp_exe)
    ctx.message = "Получение списка необходимых изменений..."
    url = "%s/%s-version-list.txt" % (__ctx__.url, __ctx__.appname)
    try:
        resp = urllib.request.urlopen(url)
        if resp.getcode() != 200:
            raise Exception("Invalid http response code for %s - %d" % (url, resp.getcode()))
        _list = resp.read().decode("utf-8")
        _list = _list.strip()
        if len(_list) > 0:
            _list = _list.split("\n")
        else:
            _list = []
        cur_ver_pos = -1
        for index, ver in enumerate(_list):
            if cmp_version(ver, __ctx__.version) == 0:
                cur_ver_pos = index
                break
        if cur_ver_pos == -1:
            raise Exception("Cannot find position for current version.")
        for i, ver in enumerate(_list[cur_ver_pos + 1 :]):
            url = "%s/%s-%s.patch" % (__ctx__.url, ver)
            ctx.progress = i
            ctx.total = len(_list) - cur_ver_pos
            resp = urllib.request.urlopen(url)
            if resp.getcode() != 200:
                raise Exception("Invalid http response code for %s - %d" % (url, resp.getcode()))
            patch = resp.read()
            fd, path = tempfile.mkstemp()
            with os.fdopen(fd, "w") as temp_file:
                temp_file.write(patch)
            bsdiff4.file_patch_inplace(temp_exe, path)
            os.remove(path)
    except:
        os.remove(temp_exe)
        raise


def update_patch_current_exe(parent, cb):

    def _cb(success, is_cancel, data_or_exception):
        cb(success, is_cancel, data_or_exception)

    task = Task("Обновление", _job, _cb)
    task.run()
