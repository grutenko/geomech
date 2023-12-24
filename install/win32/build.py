import os
import subprocess
import typing
import yaml

__ROOT__ = os.path.realpath(
        os.path.dirname(
            os.path.abspath(__file__)) + "/../..")

def run_cmd(args: typing.List):
    print(" ".join(args))
    result = subprocess.run(args, stdout=subprocess.PIPE)
    print(result.stdout.decode())
    return result

def read_version():
    with open("{}/install/win32/version.yml".format(__ROOT__), 'r', encoding='utf-8') as f:
        version = yaml.load(f, yaml.CFullLoader)
        print(version)
        return version["Version"]
    
__TARGET__ = "geomech-v{}".format(read_version())

def main():
    ret = run_cmd([
          "create-version-file",
          "{}/install/win32/version.yml".format(__ROOT__),
          "--outfile={}/build/generated-version.txt".format(__ROOT__)
    ])
    if ret.returncode != 0:
        exit()
    run_cmd([
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--add-data={}/icons/*;icons".format(__ROOT__),
        "--add-data={}/geomech.ico;geomech.ico".format(__ROOT__),
        "--version-file={}/build/generated-version.txt".format(__ROOT__),
        "--manifest={}/install/win32/geomech.exe.manifest".format(__ROOT__),
        "--icon={}/geomech.ico".format(__ROOT__),
        "--workpath={}/build".format(__ROOT__),
        "--distpath={}/dist".format(__ROOT__),
        "--name={}".format(__TARGET__),
        "--specpath={}/build".format(__ROOT__, __TARGET__),
        "{}/geomech.py".format(__ROOT__)
    ])

if __name__ == '__main__':
    main()