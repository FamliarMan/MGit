#!/usr/bin/python3
import xml.dom.minidom
import os
import sys
import time
from os.path import expanduser
curProjectDir = ""
curModules = []
namePath = {}


class Config:
    enter = True


class Module:
    path = ""
    branch = "develop"
    name = ""

config = Config()


# 检查setting tag是否配置正确
def check_root(root):
    if root.hasAttribute("curProject"):
        return True
    print("Your 'setting' tag lack 'curProject' ")
    return False


# 检查project tag配置是否正确
def check_project(project):
    if (not project.hasAttribute("name")) or (not project.hasAttribute("path")):
        print("Your project lack name tag or path tag! ")
        return False
    return True


def get_all_module(project):
    res = []
    global namePath
    modules = project.getElementsByTagName("module")
    for mod in modules:
        moduleVo = Module()
        moduleVo.name = mod.childNodes[0].data.strip('\r').strip('\n').strip()
        moduleVo.path = curProjectDir + moduleVo.name.strip('\r').strip('\n').strip()
        namePath[moduleVo.name] = moduleVo.path
        res.append(moduleVo)
    return res


# 为每个模块执行命令
def execute_cmd(cmd):
    for curMod in curModules:
        print("---------%s-----------" % curMod.path)
        os.chdir(curMod.path)
        os.system(cmd)
        print()
        global config
        if config.enter:
            print("Press Enter To Continue")
            input()
    return


# 从xml中解析信息
def load_info():
    res = []
    global curProjectDir
    global curModules
    domTree= xml.dom.minidom.parse(os.path.join(expanduser("~"), ".mgit.xml"))
    setting = domTree.documentElement
    if not check_root(setting):
        return res
    curProjectName = setting.getAttribute("curProject")
    projects = domTree.getElementsByTagName("project")
    for project in projects:
        if not check_project(project):
            return res
        if project.getAttribute("name") == curProjectName:
            curProjectDir = project.getAttribute("path")
            curModules = get_all_module(project)
            if len(curModules) == 0:
                return
            break

    if len(curProjectDir) == 0:  # curProject设置不正确
        print("Your curProject doesn't match any project!")
        return
    configXml = domTree.getElementsByTagName("config")
    if len(configXml) == 0:
        return
    global config
    enter = configXml[0].getElementsByTagName("enter")
    if len(enter) == 0:
        return
    if enter[0].childNodes[0].data == 'true':
        config.enter = True
    else:
        config.enter = False


def get_branches():
    for curMod in curModules:
        os.chdir(curMod.path)
        r = os.popen('git branch')
        lines = r.read().splitlines(False)
        for line in lines:
            if line.startswith('*'):
                curMod.branch = line[2:]
    return


def pull():
    print("Please make sure all your change is commit(y/n):")
    answer = input()
    if answer != 'y':
        return
    execute_cmd('git pull')


def push():
    print("Please make sure all your change is commit(y/n):")
    answer = input()
    if answer != 'y':
        return
    execute_cmd('git push')


def checkout():
    if len(sys.argv) < 3:
        print("Please specific a branch to checkout!")
        return
    execute_cmd('git checkout '+sys.argv[2])


def add():
    print("Are you sure you want to add all changed files to stage?(y/n)")
    answer = input()
    if answer != 'y':
        return
    execute_cmd('git add -A')


def branch():
    execute_cmd('git branch')


def log():
    if len(sys.argv) < 3:
        print("Please specify a module with name!")
        return
    if sys.argv[2] not in namePath:
        print("The module name is wrong!")
        return
    path = namePath[sys.argv[2]]
    os.chdir(path)
    os.system('git log')


def status():
    execute_cmd('git status')


def cmd_dispatch():
    global curModules
    if len(sys.argv) == 1:
        print("You didn't specify any option!")
        return
    if sys.argv[1] == "status":
        status()
    elif sys.argv[1] == "pull":
        pull()
    elif sys.argv[1] == "push":
        pull()
    elif sys.argv[1] == "checkout":
        checkout()
    elif sys.argv[1] == "add":
        add()
    elif sys.argv[1] == "branch":
        branch()
    elif sys.argv[1] == "log":
        log()
    else:
        print("Wrong Argument!")
    return


def main():
    load_info()
    get_branches()
    cmd_dispatch()

main()








