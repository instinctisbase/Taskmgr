import psutil
import time
import pns
import curses
import os
import threading

#全局函数 用来捕获所有网卡的数据包
capture=threading.Thread(target=pns.capturePacket)
capture.setDaemon(True)
capture.start()

'''使用curses库在终端显示'''
#初始化窗口
stdscr=curses.initscr()

curses.noecho()
curses.cbreak()
curses.curs_set(0)
stdscr.nodelay(1)
stdscr.keypad(True)
#初始化颜色
curses.start_color()
curses.use_default_colors()
curses.init_pair(1, curses.COLOR_WHITE, -1)
curses.init_pair(2, curses.COLOR_RED, -1)
curses.init_pair(3, curses.COLOR_GREEN, -1)
curses.init_pair(4, curses.COLOR_BLUE, -1)

#curses.LINES,curses.COLS,不知为何不能使用,因此使用getmaxyx()
height, width = stdscr.getmaxyx()
#通过proc/diskstats可以获得多个磁盘的详细信息
disk_fp=open("/proc/diskstats")
''' 可以对每个process object调用两回cpu_percent, 都用interval=None做参数. 第一次相当于启动"秒表", 第二次相当于读取"秒表", 所有的调用都是即时返回的, 所以所得到的结果几乎是对同一时间断统计得到的'''
while(1):
    #进程IO部分
    process_iospeed={}
    pids=psutil.pids()
    for pid in pids:
        try:
            pc=psutil.Process(pid)
            io_info1=pc.io_counters()
            process_iospeed[pid]=io_info1
        except Exception:
            pass

    #进程CPU部分
    p_cpu_stat={}
    for pid in pids:
        try:
            pfd=open("/proc/"+str(pid)+"/stat")
            p_cputimeinfo=pfd.readline().split()
            p_totalcputime=int(p_cputimeinfo[13])+int(p_cputimeinfo[14])+int(p_cputimeinfo[15])+int(p_cputimeinfo[16])
            p_cpu_stat[pid]=p_totalcputime
        except Exception:
            pass
    #CPU部分
    fp=open("/proc/stat")
    clist=fp.readline()
    cputimeinfo=clist.split()
    totalcputime1=int(cputimeinfo[1])+int(cputimeinfo[2])+int(cputimeinfo[3])+int(cputimeinfo[4])+int(cputimeinfo[5])+int(cputimeinfo[6])+int(cputimeinfo[7])+int(cputimeinfo[8])+int(cputimeinfo[9])+int(cputimeinfo[10])
    idlecputime1=int(cputimeinfo[4])
    fp.seek(0)

    #磁盘部分
    #使用dict主要是考虑到多磁盘用户，比如笔记本很多都有两个磁盘
    disk_usage={} 
    for i in disk_fp.readlines():
        #列表的第三项为设备名
        devname=i.split()[2] 
        if len(devname)==3:
            if("sda"<=devname<="sdz") or ("hda"<=devname<="hdz"):
                #列表的第十一项为io时间
                in_out_time=i.split()[12] 
                disk_usage[devname]=in_out_time
    disk_fp.seek(0)

    #网卡部分
    bandwidth=psutil.net_if_stats()
    bandwidthusage={} #使用数组存储多网卡的使用率
    io_counter1=psutil.net_io_counters(pernic=True)

    time.sleep(1)

    #CPU部分
    clist=fp.readline()
    cputimeinfo=clist.split()
    totalcputime2=int(cputimeinfo[1])+int(cputimeinfo[2])+int(cputimeinfo[3])+int(cputimeinfo[4])+int(cputimeinfo[5])+int(cputimeinfo[6])+int(cputimeinfo[7])+int(cputimeinfo[8])+int(cputimeinfo[9])+int(cputimeinfo[10])
    idlecputime2=int(cputimeinfo[4])
    cpu_usage=int(100-(idlecputime2-idlecputime1)/(totalcputime2-totalcputime1)*100)
    #进程CPU部分
    pids=psutil.pids()
    for pid in pids:
        try:
            if pid in p_cpu_stat:
                pfd=open("/proc/"+str(pid)+"/stat")
                p_cputimeinfo=pfd.readline().split()
                p_totalcputime=int(p_cputimeinfo[13])+int(p_cputimeinfo[14])+int(p_cputimeinfo[15])+int(p_cputimeinfo[16])
                p_cpu_stat[pid]=(p_totalcputime-p_cpu_stat[pid])/(totalcputime2-totalcputime1)*100
        except Exception:
            pass
        
    #磁盘部分
    for i in disk_fp.readlines():
        devname=i.split()[2]
        if devname in disk_usage:
            in_out_time=i.split()[12]
            #一秒内的使用率读写io时间除以一秒
            usage=(int(in_out_time)-int(disk_usage[devname]))/1000*100
            disk_usage[devname]=usage
            #输出多磁盘中使用率最高的数值
    io_usage=int(max(disk_usage.values()))
    disk_fp.seek(0)

    #网卡部分       
    io_counter2=psutil.net_io_counters(pernic=True)
    for i in bandwidth:
        if bandwidth[i].speed==0:
            continue
        if i in io_counter1 and i in io_counter2: #这一步是防止网卡突然被拔插
            updata=io_counter2[i].bytes_sent-io_counter1[i].bytes_sent
            downdata=io_counter2[i].bytes_recv-io_counter1[i].bytes_recv
            data=max(updata,downdata)  #取上传和下载中较大的作为网卡的使用率
            usage=data*8/1000/1000/bandwidth[i].speed*100
            bandwidthusage[i]=int(usage)
    #输出多网卡中带宽使用率最高的网卡的使用率
    band_usage=int(max(bandwidthusage.values()))

   # cpu_usage=psutil.cpu_percent(interval=1)
    #内存部分
    mem_usage=int(psutil.virtual_memory().percent)
    #进程IO部分
    p_io_dict={}
    pids=psutil.pids() 
    for pid in pids:
        try:
            pc=psutil.Process(pid)
            if pid in process_iospeed:
                io_info2=pc.io_counters()
                io_read=io_info2.read_bytes-process_iospeed[pid].read_bytes
                io_write=io_info2.write_bytes-process_iospeed[pid].write_bytes
                io_speed=max(io_read,io_write) #读取和写入速度，选择较大的输出
            else:
                io_speed=0 
            p_io_dict[pid]=io_speed
        except Exception:
            pass
    #进程网速部分
    socketinfo=pns.socketfile()
    p_netspeed_dict={}
    pids=psutil.pids()
    for pid in pids:
        up,down=pns.processNetSpeed(pid,socketinfo)
        process_netspeed=max(up,down)
        p_netspeed_dict[pid]=process_netspeed

    #每隔一秒将捕获到的数据包清空一次
    pns.clearsoketdict()
    #将进程的所有信息装入列表，并按照CPU使用率排序
    processsort=[]
    pids=psutil.pids() 
    for pid in pids:
        try:
            pc=psutil.Process(pid)
            p_cpu_usage=float('%.1f' % p_cpu_stat[pid])
            p_cpu_usage=str(p_cpu_usage)+"%"
            p_mem_count=int(pc.memory_info().rss)
           
            if p_mem_count/1024>1:
                if p_mem_count/1024/1024>1:
                    if p_mem_count/1024/1024/1024>1:
                        p_mem_count=p_mem_count/1024/1024/1024
                        p_mem_count=float('%.1f' % p_mem_count)
                        p_mem_count=str(p_mem_count)+'GB'
                    else:
                        p_mem_count=p_mem_count/1024/1024
                        p_mem_count=float('%.1f' % p_mem_count)
                        p_mem_count=str(p_mem_count)+'MB'
                else:
                    p_mem_count=p_mem_count=str(p_mem_count/1024)+'KB'
                    p_mem_count=p_mem_count/1024
                    p_mem_count=float('%.1f' % p_mem_count)
                    p_mem_count=str(p_mem_count)+'KB'
            else:               
                p_mem_count=float('%.1f' % p_mem_count)
                p_mem_count=str(p_mem_count)+'B'
           
                
            p_name=pc.name()
            io_speed=p_io_dict[pid]
            if io_speed/1024>1:
                if io_speed/1024/1024>1:
                    if io_speed/1024/1024/1024>1:
                        io_speed=io_speed/1024/1024/1024
                        io_speed=float('%.1f' % io_speed)
                        io_speed=str(io_speed)+'GB/S'
                    else:
                        io_speed=io_speed/1024/1024
                        io_speed=float('%.1f' % p_mem_count)
                        io_speed=str(io_speed)+'MB/S'
                else:
                    io_speed=io_speed/1024
                    io_speed=float('%.1f' % io_speed)
                    io_speed=str(io_speed)+'KB/S'
            else:               
                io_speed=float('%.1f' % io_speed)
                io_speed=str(io_speed)+'B/S'

            p_net=p_netspeed_dict[pid]
            if p_net/1024>1:
                if p_net/1024/1024>1:
                    if p_net/1024/1024/1024>1:
                        p_net=p_net/1024/1024/1024
                        p_net=float('%.1f' % p_net)
                        p_net=str(p_net)+'GB/S'
                    else:
                        p_net=p_net/1024/1024
                        p_net=float('%.1f' % p_net)
                        p_net=str(p_net)+'MB/S'
                else:
                    p_net=p_net/1024
                    p_net=float('%.1f' % p_net)
                    p_net=str(p_net)+'KB/S'
            else:               
                p_net=float('%.1f' % p_net)
                p_net=str(p_net)+'B/S'

            if pid in p_cpu_stat and pid in p_io_dict:
                processsort.append((pid,p_name,p_cpu_usage,p_mem_count,io_speed,p_net))
        except Exception:
            pass

    #将进程信息按照cpu使用率排序
    #processsort.sort(key=lambda x: x[2],reverse=True)
    col=1 #进程的输出从第二行开始
    temp=sorted(processsort, key=lambda x: x[2],reverse = True) 

    #擦干净屏幕重新绘制
    stdscr.clear()
    for p in temp:
        try:
            stdscr.addstr(col,0,str(p[1]),curses.color_pair(1))
            stdscr.addstr(col,int(width/7*2),str(p[0]),curses.color_pair(1))
            stdscr.addstr(col,int(width/7*3),str(p[2]),curses.color_pair(1))
            stdscr.addstr(col,int(width/7*4),str(p[3]),curses.color_pair(1))
            stdscr.addstr(col,int(width/7*5),str(p[4]),curses.color_pair(1))
            stdscr.addstr(col,int(width/7*6),str(p[5]),curses.color_pair(1))
            col=col+1
        except curses.error:
            pass

    try:
        stdscr.addstr(0,0,"进程名称",curses.A_BOLD)
        stdscr.addstr(0,int(width/7*2),"进程号",curses.A_BOLD)
        stdscr.addstr(0,int(width/7*3),"CPU:"+str(cpu_usage)+"%",curses.A_BOLD)
        stdscr.addstr(0,int(width/7*4),"内存:"+str(mem_usage)+"%",curses.A_BOLD)
        stdscr.addstr(0,int(width/7*5),"硬盘:"+str(io_usage)+"%",curses.A_BOLD)
        stdscr.addstr(0,int(width/7*6),"网络:"+str(band_usage)+"%",curses.A_BOLD)
        stdscr.refresh()
    
    except curses.error:
            # let's hope it's just a momentary glitch due to a temporarily
            # reduced window size or something
        pass
    if stdscr.getch()==ord('q'):
        break
  
    



#关闭窗口
curses.echo()
curses.nocbreak()
curses.endwin()




