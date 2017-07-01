# 多模块git管理脚本
本脚本基于python3.0
### 支持功能
1. add 能够把所有模块的改动文件都暂存起来，每个模块实际执行git add -A
2. status 能够查看所有模块的状态，实际每个模块执行 git status
3. pull 能够从远程拉取分支最新数据到本地，实际执行git pull
4. push 能够将本地提交推送到远程分支，实际执行git push
5. checkout [branch] 将所有模块切换到一个分支，实际执行git checkout
6. branch 查看当前所有模块所在的分支名称,实际执行git branch


### 配置文件
首先要在家目录下新建一个文件.mgit.xml,没有会报错。
```
<setting curProject="tmp_app"> <!--配置当前project的名称-->
	<project path ="/home/jianglei/tmp_app/"   
		 name = "tmp_app">  <!--每一个project都要配置path路径和名称name，可以配置多个project，通过curProject指定当前使用的是什么-->
		<!--这里直接配置每个模块的名称,不能错-->	
		<module>2dfire_share</module>

		<module>FireWaiterModule</module>

		<module>GoodsModule</module>

		<module>LoginModule</module>

		<module>ManagerApp</module>

		<module>ManagerBase</module>
	</project>
	<config>
		<!--每个模块执行完命令是否按回车后再执行-->
   	 <enter>true</enter>
	</config>
</setting>
```

### 别名配置
由于脚本是python写的，每次运行都要使用python 的命令，非常麻烦，推荐使用别名
如 alias mgit='python3  (install home )/mgit.py',这样就可以直接使用mgit add,mgit status,mgit pull,mgit push,mgit checkout，非常方便。

