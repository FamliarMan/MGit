# 多模块git管理脚本
本脚本基于python3.0

### 支持功能
1. add 能够把所有模块的改动文件都暂存起来，每个模块实际执行git add -A
2. status 能够查看所有模块的状态，实际每个模块执行 git status
3. pull 能够从远程拉取分支最新数据到本地，实际执行git pull
4. push 能够将本地提交推送到远程分支，实际执行git push
5. checkout [branch] 将所有模块切换到一个分支，实际执行git checkout
6. branch 查看当前所有模块所在的分支名称,实际执行git branch
7. log [module name] 该命令能够对指定的module执行git log命令,如果module name为空则对所有module执行该命令。
8. clone 能够重新clone一个新的工程
9. path 能够打印当前工程所在的目录
10. each 能够以交互式方式对每一个模块输入命令
11. wb  work branch 缩写，能快速切换到正在工作的分支
12. ib init branch 缩写，能快速切换到所有初始分支

### 特殊参数
> -t  [工程名称] 切换当前工作的工程
  -f 忽略配置文件中的“enter“配置项，强制一次性对所有模块执行命令
  -c 对每一个模块执行自定义命令如：-c git status
  

### 配置文件
首先要在家目录下新建一个文件.mgit.xml,没有会报错。
```

<setting curProject="memory"> 
    <project name="multi_menu" path="/home/jianglei/AndroidStudioProjects/multi_menu/">
        <module>
            <name>2dfire_share</name>
            <!--初始分支,便于合并develop分支最新代码-->
            <initBranch>restdev</initBranch>
            <!--开发分支-->
            <workBranch>feature/mutil_menu</workBranch>
            <git>git@git.2dfire-inc.com:background_manage_new/2dfire_share.git</git>
        </module>
        <module>
            <name>FireWaiterModule</name>
            <initBranch>restdev</initBranch>
            <workBranch>feature/mutil_menu</workBranch>
            <git>git@git.2dfire-inc.com:2ye-android/fire_waiter_android.git</git>
        </module>
        <module>
            <name>GoodsModule</name>
            <initBranch>develop</initBranch>
            <workBranch>feature/mutil_menu</workBranch>
            <git>git@git.2dfire-inc.com:background_manage_android/ManagerGoods.git</git>
        </module>
        <module>
            <name>LoginModule</name>
            <initBranch>develop</initBranch>
            <workBranch>feature/mutil_menu</workBranch>
            <git>git@git.2dfire-inc.com:tdf_module_android/TDFLoginModule.git</git>
        </module>
        <module>
            <name>ManagerApp</name>
            <initBranch>restdev</initBranch>
            <workBranch>feature/mutil_menu</workBranch>
            <git>git@git.2dfire-inc.com:background_manage_new/background-rest_phone.git</git>
        </module>
        <module>
            <name>ManagerBase</name>
            <initBranch>develop</initBranch>
            <workBranch>feature/mutil_menu</workBranch>
            <git>git@git.2dfire-inc.com:background_manage_android/ManagerBase.git</git>
        </module>
	......
    </project>

	<config>
		
	<!--如果每个模块执行命令都希望用户自己按回车确认，配置为true，否则会自动对所有模块执行该命令，但可以使用-f参数改变属性-->
   	 <enter>true</enter>
	</config>
</setting>
```

### 别名配置
由于脚本是python写的,且只支持python3，每次运行都要使用python 的命令，非常麻烦，推荐使用别名
如 alias mgit='python3  (install home )/mgit.py',这样就可以直接使用mgit add,mgit status,mgit pull,mgit push,mgit checkout，非常方便。

