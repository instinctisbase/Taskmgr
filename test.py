import curses
import os
import tempfile
import psutil
import time

'''
#进程部分
 可以对每个process object调用两回cpu_percent, 都用interval=None做参数. 第一次相当于启动"秒表", 第二次相当于读取"秒表", 所有的调用都是即时返回的, 所以所得到的结果几乎是对同一时间断统计得到的
 
process_iospeed={}
pids=psutil.pids()
for pid in pids:
    pc=psutil.Process(pid)
    #启动ji
    pc.cpu_percent()
    io_info1=pc.io_counters()
    process_iospeed[pid]=io_info1


time.sleep(1)

col=1 #进程的输出从第二行开始
processsort=[]
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
        p_cpu_usage=pc.cpu_percent()
        print(p_cpu_usage)
        p_mem_count=pc.memory_info().rss
        p_name=pc.name()
        #将process_iospeed={}改造存储进程的所有信息
        processsort.append((pid,p_name,p_cpu_usage,p_mem_count,io_speed))
    except Exception:
        pass

#将进程信息按照cpu使用率排序
processsort.sort(key=lambda x: x[2],reverse=True)
print(processsort)
print("\n")'''
'''
while(1):
    fp=open("/proc/stat")
    clist=fp.readline()
    cputimeinfo=clist.split()
    totalcputime1=int(cputimeinfo[1])+int(cputimeinfo[2])+int(cputimeinfo[3])+int(cputimeinfo[4])+int(cputimeinfo[5])+int(cputimeinfo[6])+int(cputimeinfo[7])+int(cputimeinfo[8])+int(cputimeinfo[9])+int(cputimeinfo[10])
    idlecputime1=int(cputimeinfo[4])
    pids=psutil.pids()
    p_cpu_stat={}
    for pid in pids:
        pfd=open("/proc/"+str(pid)+"/stat")
        p_cputimeinfo=pfd.readline().split()
        p_totalcputime=int(p_cputimeinfo[13])+int(p_cputimeinfo[14])+int(p_cputimeinfo[15])+int(p_cputimeinfo[16])
        p_cpu_stat[pid]=p_totalcputime

    time.sleep(1)
    fp.seek(0)
    clist=fp.readline()
    cputimeinfo=clist.split()
    totalcputime2=int(cputimeinfo[1])+int(cputimeinfo[2])+int(cputimeinfo[3])+int(cputimeinfo[4])+int(cputimeinfo[5])+int(cputimeinfo[6])+int(cputimeinfo[7])+int(cputimeinfo[8])+int(cputimeinfo[9])+int(cputimeinfo[10])
    idlecputime2=int(cputimeinfo[4])
    cpu_usage=int(100-(idlecputime2-idlecputime1)/(totalcputime2-totalcputime1)*100)
    pids=psutil.pids()
    for pid in pids:
        if pid in p_cpu_stat:
            pfd=open("/proc/"+str(pid)+"/stat")
            p_cputimeinfo=pfd.readline().split()
            p_totalcputime=int(p_cputimeinfo[13])+int(p_cputimeinfo[14])+int(p_cputimeinfo[15])+int(p_cputimeinfo[16])
            p_cpu_stat[pid]=p_totalcputime-p_cpu_stat[pid]
    print(p_cpu_stat)
    '''

bandwidth=psutil.net_if_stats()
bandwidthusage={} #使用数组存储多网卡的使用率
io_counter1=psutil.net_io_counters(pernic=True)
print(bandwidth)
print("\n")
print(io_counter1)









