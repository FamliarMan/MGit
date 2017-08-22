#!/usr/bin/python3
import xml.dom.minidom
import os
import sys
import time
import shutil
import signal
import getopt
from xml.etree import ElementTree as ET
from os.path import expanduser

FILE_NOT_EXIST = 1
XML_CONFIG_ERROR = 2
ARGUMENT_ERROR = 3

curProjectDir = None
configFilePath = None
curModules = []
curProjects = []
namePath = {}
Tree = None


def prRed(prt): print("\033[91m {}\033[00m".format(prt))


def prGreen(prt): print("\033[92m {}\033[00m".format(prt))


def prYellow(prt): print("\033[93m {}\033[00m".format(prt))


def prLightPurple(prt): print("\033[94m {}\033[00m".format(prt))


def prPurple(prt): print("\033[95m {}\033[00m".format(prt))


def prCyan(prt): print("\033[96m {}\033[00m".format(prt))


def prLightGray(prt): print("\033[97m {}\033[00m".format(prt))


def prBlack(prt): print("\033[98m {}\033[00m".format(prt))


# 按下ctrl+c时触发
def handler(signal_num, frame):
    sys.exit(signal_num)


class Config:
    enter = True


class Project:
    name = ""
    path = ""


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
        print("Branch:" + self.branch)
        print("git:" + self.git)
        print("path:" + self.path)
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
        mod_config.path = curProjectDir + "/" + mod_config.name
        mod_config.xml_element = mod
        namePath[mod_config.name] = mod_config.path
        res.append(mod_config)
    return res


# 为每个模块执行命令
def execute_cmd(cmd, is_skip_no_dir=True):
    global curProjectDir
    global config
    for index in range(len(curModules)):
        curMod = curModules[index]
        if config.enter:
            prRed("\nNext is module[%s],s to skip,n to stop,enter to continue:" % curMod.name)
            ans = input()
            if ans == 's':
                continue
            elif ans == 'n':
                return
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
    return


def get_tree():
    global Tree
    global configFilePath
    configFilePath = os.path.abspath(".")+"/.mgit.xml"
    # 全局配置文件
    globalFilePath = os.path.join(expanduser("~"), ".mgit.xml")
    if not os.path.exists(configFilePath):
        if not os.path.exists(globalFilePath):
            prRed("Can't find .mgit.xml file in your home directory nor project directory!")
            sys.exit(FILE_NOT_EXIST)
        else:
            configFilePath = globalFilePath
    try:
        Tree = ET.parse(configFilePath)
    except xml.etree.ElementTree.ParseError:
        prRed("You should configure your .mgit.xml right!\n"+"path:"+configFilePath)
        sys.exit(XML_CONFIG_ERROR)


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
        # 顺便记录下各个项目的信息
        p = Project()
        p.name = project.get("name")
        p.path = project.get("path")
        curProjects.append(p)
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


def checkout(new_branch):
    check_cur_project()
    if len(sys.argv) < 3:
        print("Please specific a branch to checkout!")
        return
    execute_cmd('git checkout ' + new_branch)


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


def log(module_name):
    check_cur_project()
    if module_name is None:
        execute_cmd('git log')
    elif module_name not in namePath:
        print("The module name is wrong!")
        return
    else:
        module_path = namePath[module_name]
        os.chdir(module_path)
        os.system('git log')


def status():
    check_cur_project()
    execute_cmd('git status')


def switch_project(new_project):
    get_tree()
    # 设置当前使用的工程名称
    all_projects = Tree.getroot().findall("project")
    # 查找当前使用的是那个project
    has_project = False
    for project in all_projects:
        if project.get("name") == new_project:
            has_project = True
    if not has_project:
        prRed("Wrong project name")
        sys.exit(XML_CONFIG_ERROR)
    Tree.getroot().set("curProject", new_project)
    Tree.write(configFilePath)
    print("Switch to project: " + new_project)


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
        prYellow("\n( " + curMod.name + " :q for quit,n  or enter for next or others for command to execute)")
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
            print("\n\n")
            continue
        else:
            print("\n\n")
            continue


def customer_cmd(cmd):
    print(cmd)
    execute_cmd(cmd)


# 检出该项目的初始分支或工作分支
def checkout_init_or_work_branch(is_init_branch=True):
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


# 添加一个新模块
def add_module(module_name):
    global curProjectDir
    for mod in curModules:
        if module_name == mod.name:
            os.chdir(curProjectDir)
            cmd = 'git clone -b ' + mod.init_branch + ' ' + mod.git + '  ' + mod.name
            os.system(cmd)
            return
    prRed("Wrong module name")


# 大致列出当前分支信息
def list_info():
    global curModules
    for mod in curModules:
        prYellow("-------------------------------------------------------")
        print("name:         " + mod.name)
        print("work branch:  " + mod.work_branch)
        print("init branch:  " + mod.init_branch)
        print("git:          " + mod.git)
        print("\n")


def list_project():
    for p in curProjects:
        prYellow("-----------------------------------------")
        prRed(p.name)
        print(p.path)


def help():
    txt = \
        """
        -h or --help:                  Print the help content.
        -t or --target [project name]: switch the working project.
        -f or --force:                 Force to overwrite the 'enter' tag in xml file,and always opposite. 
        -c or --command:[custom cmd]:  Execute the customer git commands for all modules,for example: -c git status.
        ---------------------------------------------------------------------------------------
        add                 Add files of all the module to the index,just like 'git add'.
        status              Show the working tree status of every module,just like 'git status'.
        pull                Fetch from and integrate with another repository or a local branch
                                for every module,just like 'git pull'.
        push                Update remote refs along with associated objects for every module, 
                                just like 'git push'.
        checkout [branch]   Switch the branches of all the modules to a new branch.
        branch              Print all the branches of every module.
        log [module]        Print the log of the specific module,and if module is empty,execute 'git log' 
                                for every module.
        clone               Clone a new project to local,you should config it in the .mgit.xml first.
        path                Print the directory of current working project.
        each                Execute commands in interaction mode.
        wb                  Switch the branches of all the modules to the work branch configured 
                                in the .mgit.xml.
        ib                  Switch the branches of all the modules to the init branch configured 
                                in the .mgit.xml.
        am [new module]     Add a new module to project,you should config the module in .mgit.xml first.
        list                List the information of every module.
        project             List all the projects configured in the .mgit.xml
        """
    print(txt)


def cmd_dispatch():
    global curModules
    try:
        options, args = getopt.getopt(sys.argv[1:], "hft:c", ["help", "target=", "command"])
        for name, value in options:
            if name in ("-h", "--help"):
                # help
                help()
                break
            elif name in ("-t", "--target"):
                switch_project(value)
                break
            elif name in ("-f", "--force"):
                config.enter = not config.enter
            elif name in ("-c", "--command"):
                customer_command = ""
                for i in args:
                    customer_command += (i + " ")
                customer_cmd(customer_command)
                return
        for i in range(len(args)):
            cmd = args[i]
            if cmd == "status":
                get_branches()
                status()
                break
            elif cmd == "pull":
                get_branches()
                pull()
                break
            elif cmd == "push":
                get_branches()
                push()
                break
            elif cmd == "checkout":
                if i + 1 >= len(args):
                    raise getopt.GetoptError('Wrong argument')
                new_branch = args[i + 1]
                get_branches()
                checkout(new_branch)
                break
            elif cmd == "add":
                get_branches()
                add()
                break
            elif cmd == "branch":
                get_branches()
                branch()
                break
            elif cmd == "log":
                get_branches()
                if i + 1 >= len(args):
                    log(None)
                else:
                    log(args[i + 1])
                break
            elif cmd == "clone":
                clone()
                break
            elif cmd == "path":
                path()
                break
            elif cmd == "each":
                each()
                break
            elif cmd == "wb":
                checkout_init_or_work_branch(False)
                break
            elif cmd == "ib":
                checkout_init_or_work_branch(True)
                break
            elif cmd == "am":
                if i + 1 >= len(args):
                    prRed("Wrong argument,please specify a module name you want to add")
                else:
                    add_module(args[i + 1])
                break
            elif cmd == "list":
                list_info()
                break
            elif cmd == "project":
                list_project()
                break
            else:
                prRed("Wrong argument,please refer to '-h or --help'")
    except getopt.GetoptError:
        prRed("Wrong argument,please refer to '-h or --help'")


def main():
    signal.signal(signal.SIGINT, handler)
    load_info()
    cmd_dispatch()


main()
