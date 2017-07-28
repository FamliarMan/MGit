#!/usr/bin/python3
import xml.dom.minidom
import os
import sys
import time
import shutil
import signal
from xml.etree import ElementTree as ET
from os.path import expanduser

FILE_NOT_EXIST = 1
XML_CONFIG_ERROR = 2
ARGUMENT_ERROR = 3

curProjectDir = None
configFilePath = None
curModules = []
namePath = {}
Tree = None


def prRed(prt): print("\033[91m {}\033[00m" .format(prt))


def prGreen(prt): print("\033[92m {}\033[00m" .format(prt))


def prYellow(prt): print("\033[93m {}\033[00m" .format(prt))


def prLightPurple(prt): print("\033[94m {}\033[00m" .format(prt))


def prPurple(prt): print("\033[95m {}\033[00m" .format(prt))


def prCyan(prt): print("\033[96m {}\033[00m" .format(prt))


def prLightGray(prt): print("\033[97m {}\033[00m" .format(prt))


def prBlack(prt): print("\033[98m {}\033[00m" .format(prt))


# 按下ctrl+c时触发
def handler(signal_num,frame):
    sys.exit(signal_num)


class Config:
    enter = True


class Module:
    path = None
    branch = None
    init_branch = None
    work_branch = None
    git = None
    name = None
    xml_element = None

    def string(self):
        print("Name：" + self.name)
        print("Branch:"+self.branch)
        print("git:"+self.git)
        print("path:"+self.path)
        print()


config = Config()


def check_cur_project():
    if curProjectDir is None:
        print("You should specify a right project name in 'curProject'!")
        sys.exit(XML_CONFIG_ERROR)


# 检查project tag配置是否正确
def check_project(project):
    if project.get("path") is None or project.get("name") is None:
        print("Your project lack name or path!")
        sys.exit(XML_CONFIG_ERROR)


def check_module(mod):
    if (mod.find("name") is None) or (mod.find("initBranch") is None) or (mod.find("git") is None):
        print("Your module lack name or initBranch or git tag! ")
        sys.exit(XML_CONFIG_ERROR)


def get_all_module(project):
    res = []
    global namePath
    modules = project.findall("module")
    for mod in modules:
        check_module(mod)
        mod_config = Module()
        mod_config.name = mod.find("name").text
        mod_config.init_branch = mod.find("initBranch").text
        mod_config.work_branch = mod.find("workBranch").text
        mod_config.git = mod.find("git").text
        mod_config.path = curProjectDir +"/"+ mod_config.name
        mod_config.xml_element = mod
        namePath[mod_config.name] = mod_config.path
        res.append(mod_config)
    return res


# 为每个模块执行命令
def execute_cmd(cmd, is_skip_no_dir=True):
    global curProjectDir
    is_skip = False
    next_module = None
    for index in range(len(curModules)):
        curMod = curModules[index]
        if index < len(curModules) - 1:
            next_module = curModules[index+1]
        if is_skip:
            is_skip = False
            continue
        prYellow("---------%s-----------" % curMod.path)
        # 对应的目录存在，则进入到该目录中去执行
        if os.path.exists(curMod.path):
            os.chdir(curMod.path)
            # 如果传入的是命令列表，则取出每个模块对应的命令
            if isinstance(cmd, list):
                cur_cmd = cmd[index]
            # 如果传入的命令是单条命令，则直接执行
            else:
                cur_cmd = cmd
            os.system(cur_cmd)
            print()
        # 对应目录不存在
        else:
            # 跳过该命令
            if is_skip_no_dir:
                prLightPurple("This module does't exist!")
            # 在根目录执行该命令
            else:
                os.chdir(curProjectDir)
                # 如果传入的是命令列表，则取出每个模块对应的命令
                if isinstance(cmd, list):
                    cur_cmd = cmd[index]
                # 如果传入的命令是单条命令，则直接执行
                else:
                    cur_cmd = cmd
                os.system(cur_cmd)
                print()
        global config
        if config.enter:
            prYellow("\n(%s--->%s)Press enter to continue,s to skip next module,n to stop" % (curMod.name, next_module.name))
            ans = input()
            if ans == "s":
                is_skip = True
            elif ans == "n":
                sys.exit()
            else:
                is_skip = False
    return


def get_tree():
    global Tree
    global configFilePath
    configFilePath = os.path.join(expanduser("~"), ".mgit.xml")
    try:
        Tree = ET.parse(configFilePath)
    except IOError:
        print("Missing .mgit.xml file in your home directory!")
        sys.exit(FILE_NOT_EXIST)


# 从xml中解析信息
def load_info():
    global curProjectDir
    global curModules
    global Tree
    global configFilePath
    get_tree()
    root = Tree.getroot()
    cur_project_name = root.get("curProject")
    if cur_project_name is None:
        print("You didn't set a curProject tag!")
        sys.exit(XML_CONFIG_ERROR)
    all_projects = root.findall("project")
    # 查找当前使用的是那个project
    for project in all_projects:
        check_project(project)
        if project.get("name") == cur_project_name:
            curProjectDir = project.get("path")
            curModules = get_all_module(project)
    if not os.path.exists(curProjectDir):
        print("Wrong path in project,do you want to make it(%s)?(y/n):" % curProjectDir)
        ans = input()
        if ans != "y":
            sys.exit(XML_CONFIG_ERROR)
        else:
            os.mkdir(curProjectDir)
    # 加载配置信息
    global config
    cfg_element = root.find("config")
    if cfg_element is not None:
        enter = cfg_element.find("enter")
        if enter is not None and enter.text is not None:
            if enter.text.lower() == "true":
                config.enter = True
            else:
                config.enter = False


def get_branches():
    for curMod in curModules:
        if not os.path.exists(curMod.path):
            continue
        os.chdir(curMod.path)
        r = os.popen('git branch')
        lines = r.read().splitlines(False)
        for line in lines:
            if line.startswith('*'):
                curMod.branch = line[2:]
    return


def pull():
    check_cur_project()
    print("Please make sure all your change is commit(y/n):")
    answer = input()
    if answer != 'y':
        return
    execute_cmd('git pull')


def push():
    check_cur_project()
    print("Please make sure all your change is commit(y/n):")
    answer = input()
    if answer != 'y':
        return
    execute_cmd('git push')


def checkout():
    check_cur_project()
    if len(sys.argv) < 3:
        print("Please specific a branch to checkout!")
        return
    execute_cmd('git checkout '+sys.argv[2])


def add():
    check_cur_project()
    print("Are you sure you want to add all changed files to stage?(y/n)")
    answer = input()
    if answer != 'y':
        return
    execute_cmd('git add -A')


def branch():
    check_cur_project()
    execute_cmd('git branch')


def log():
    check_cur_project()
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
    check_cur_project()
    execute_cmd('git status')


def cfg():
    get_tree()
    if len(sys.argv) < 4:
        print("Lack argument!")
        sys.exit(ARGUMENT_ERROR)
    # 设置当前使用的工程名称
    if sys.argv[2] == "-project":

        all_projects = Tree.getroot().findall("project")
        # 查找当前使用的是那个project
        has_project = False
        for project in all_projects:
            if project.get("name") == sys.argv[3]:
                has_project = True
        if not has_project:
            prRed("Wrong project name")
            sys.exit(XML_CONFIG_ERROR)
        Tree.getroot().set("curProject", sys.argv[3])
        Tree.write(configFilePath)
        print("Switch to project:"+sys.argv[3])
    else:
        print("Wrong Argument!")


def clone():
    global curProjectDir
    check_cur_project()
    print(curProjectDir)
    if len(os.listdir(curProjectDir)) != 0:
        print("Directory: %s isnt't empty,do you want to clear it?(y/n):" % curProjectDir)
        answer = input()
        if answer != 'y':
            return
        shutil.rmtree(curProjectDir)
        os.mkdir(curProjectDir)
    cmds = []
    for curMod in curModules:
        cmd = 'git clone -b ' + curMod.init_branch + ' ' + curMod.git + '  ' + curMod.name
        cmds.append(cmd)
        # os.system('git clone -b ' + curMod.init_branch + ' ' + curMod.git + '  ' + curMod.name)
        # if config.enter:
        #     print("\nPress enter to continue,q to quit ")
        #     ans = input()
        #     if ans == 'q':
        #         return
    execute_cmd(cmds, False)


# 打印当前工程所在路径
def path():
    print(curProjectDir)


# 遍历每一个模块然后进行相应的操作
def each():
    for curMod in curModules:
        prYellow("---------%s-----------" % curMod.path)
        if not os.path.exists(curMod.path):
            continue
        os.chdir(curMod.path)
        os.system('git status')
        prYellow("\n( "+curMod.name+" :q for quit,n  or enter for next or others for command to execute)")
        print(":", end='')
        cmd = input()
        while cmd != 'q' and cmd != 'n' and cmd != '':
            print("---------%s-----------" % curMod.path)
            os.system(cmd)
            prYellow("\n(q for quit,n or enter for next or others for command to execute)")
            print(":", end='')
            cmd = input()
        if cmd == 'q':
            sys.exit(0)
        # 继续执行下一个模块的操作
        elif cmd == 'n':
            continue
        else:
            continue


def repeat():
    if len(sys.argv) < 3:
        prRed("Please specify a command to execute!")
        sys.exit(ARGUMENT_ERROR)
    cmd = ""
    for arg in sys.argv[2:]:
        cmd += arg
        cmd += " "
    execute_cmd(cmd)


# 检出该项目的初始分支或工作分支
def checkout_init_or_work_branch(is_init_branch = True):
    prRed("Please make sure you commit all your files(y/n):")
    ans = input()
    if ans == 'n':
        return
    cmds = []
    global curModules
    for index in range(len(curModules)):
        mod = curModules[index]
        if is_init_branch:
            cmd = "git checkout " + mod.init_branch
        else:
            cmd = "git checkout " + mod.work_branch
        cmds.append(cmd)
    execute_cmd(cmds)


def cmd_dispatch():
    global curModules
    if len(sys.argv) == 1:
        print("You didn't specify any option!")
        return
    if sys.argv[1] == "status":
        get_branches()
        status()
    elif sys.argv[1] == "pull":
        get_branches()
        pull()
    elif sys.argv[1] == "push":
        get_branches()
        push()
    elif sys.argv[1] == "checkout":
        get_branches()
        checkout()
    elif sys.argv[1] == "add":
        get_branches()
        add()
    elif sys.argv[1] == "branch":
        get_branches()
        branch()
    elif sys.argv[1] == "log":
        get_branches()
        log()
    elif sys.argv[1] == "config":
        cfg()
    elif sys.argv[1] == "clone":
        clone()
    elif sys.argv[1] == "path":
        path()
    elif sys.argv[1] == "each":
        each()
    elif sys.argv[1] == "repeat":
        repeat()
    elif sys.argv[1] == "wb":
        checkout_init_or_work_branch(False)
    elif sys.argv[1] == "ib":
        checkout_init_or_work_branch(True)

    else:
        print("Wrong Argument!")

    return


def main():
    signal.signal(signal.SIGINT, handler)
    load_info()
    cmd_dispatch()

main()

