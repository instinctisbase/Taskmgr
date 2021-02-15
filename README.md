# Taskmgr
linux资源管理
![截图录屏_选择区域_20210215172040](https://user-images.githubusercontent.com/22315321/107927735-5ff9cb80-6fb2-11eb-9b89-bdec3052ffb6.png)

# 项目背景
一直在同时使用Windows和Linux,在对计算机的资源监视方面,感觉linux下的ps和top工具不如Windows下的资管管理器直观，简洁和高效。因此，决定按照Windows下的资源管理器格式写一版Linux下的资源管理器

# 上手指南
下载dist目录下的Taskmgr文件，使用root权限可以直接在Linux下运行，该文件是通过pyinstaller打包，已经包含了所需要的第三方库，该项目仅在deepin20下经过测试，如果使用过程发现bug,请提交反馈。如果你想查看代码，请下载Taskmgr.py和pns.py。

# 技术原理
该项目主要技术难点在于进程部分的网速统计，需要抓取网卡上的所有数据包，并通过/proc/pid/fp找到所有的socket文件对应的inode号。通过inode号和/proc/net/tcp和/proc/net/udp目录下的socket的信息匹配，并将该socket信息和捕获到的数据包进行匹配，最终计算出每个进程的网速。
其余信息通过/proc目录和psutils库得到。具体做法，有时间再写。

# 版本控制
version :0.0.2

# 作者
instinctisbase

