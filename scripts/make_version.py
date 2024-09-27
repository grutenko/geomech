import os
from os.path import *
from datetime import date
import subprocess

if __name__ == "__main__":
    today = date.today()
    proc = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
    hash = int(proc, base=16)
    version = "%d.%d.%d.%d" % (today.year, today.month, today.day, hash)
    dir = dirname(realpath(__file__))
    with open(join(dir, "../version.py"), "w") as f:
        f.write('__GEOMECH_VERSION__ = "{version}"'.format(version=version))
    print(version)
