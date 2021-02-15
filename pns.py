import pcap
import dpkt
import socket
import codecs
import struct

import psutil
import itertools
import sys
import time
import os
import re
import threading
import copy

'''该模块的作用是获取每个进程的网速'''

socketdict={}

def capturePacket():
    global socketdict
    pc=pcap.pcap()
    for ptime,pdata in pc:
        edata=dpkt.ethernet.Ethernet(pdata)#解包，解出数据链层
        if not isinstance(edata.data,dpkt.ip.IP):#判断是否有IP层，如果只是arp协议只有数据链层
            continue
        ipdata=edata.data #解出IP层
        if not isinstance(ipdata.data,(dpkt.tcp.TCP,dpkt.udp.UDP)): #判断该数据包属于TCP或者UDP
            continue
        tran_data=ipdata.data#解出传输层
        #将socket的五元祖作为key,长度作为value存入字典
        socketflag=(socket.inet_ntoa(ipdata.src),str(tran_data.sport),str(ipdata.p),socket.inet_ntoa(ipdata.dst),str(tran_data.dport))
        length=len(ipdata)  #流量是按数据帧大小来计算的
        
        if socketflag in socketdict: #数据帧的长度
            socketdict[socketflag]=socketdict[socketflag]+length
        else:
            socketdict[socketflag]=length
       

#将/proc/net/tcp和/proc/net/udp中的socket的五元祖信息作为value,inode号作为key存入字典                        
def socketfile():
    socdict={}
    tcppath="/proc/net/tcp"
    tcpfile=open(tcppath,"r")
    tcplines=tcpfile.readlines()
    for line in tcplines[1:]:
        slist=line.split()
        inodenumber=slist[9]
        locip=slist[1].split(":")[0]
        #获取本地ip 因为是大端，要改成小端
        localip=str(int(locip[6:8],16))+"."+str(int(locip[4:6],16))+"."+str(int(locip[2:4],16))+"."+str(int(locip[0:2],16))
        #获取本地端口
        locport=slist[1].split(":")[1]
        localport=str(int(locport,16))
        fip=slist[2].split(":")[0]
        #获取远方IP
        farip=str(int(fip[6:8],16))+"."+str(int(fip[4:6],16))+"."+str(int(fip[2:4],16))+"."+str(int(fip[0:2],16))
        #获取远方端口
        fport=slist[2].split(":")[1]
        farport=str(int(fport,16))
        tcpkey=(localip,localport,str(6),farip,farport)
        socdict[inodenumber]=tcpkey #将inode号作为键，对应的socket 五元祖作为值
    tcpfile.close()

    udppath="/proc/net/udp"
    udpfile=open(udppath,"r")
    udplines=udpfile.readlines()
    for line in udplines[1:]:
        slist=line.split()
        inodenumber=slist[9]
        locip=slist[1].split(":")[0]
        #获取本地ip 因为是大端，要改成小端
        localip=str(int(locip[6:8],16))+"."+str(int(locip[4:6],16))+"."+str(int(locip[2:4],16))+"."+str(int(locip[0:2],16))
        #获取本地端口
        locport=slist[1].split(":")[1]
        localport=str(int(locport,16))
        fip=slist[2].split(":")[0]
        #获取远方IP
        farip=str(int(fip[6:8],16))+"."+str(int(fip[4:6],16))+"."+str(int(fip[2:4],16))+"."+str(int(fip[0:2],16))
        #获取远方端口
        fport=slist[2].split(":")[1]
        farport=str(int(fport,16))
        udpkey=(localip,localport,str(17),farip,farport)
        socdict[inodenumber]=udpkey #将inode号作为键，对应的socket 五元祖作为值
    udpfile.close()
    return socdict

#计算每个进程的网速
def processNetSpeed(pid,socketinfo):
    
    global socketdict 
    #tempdict=list(socketdict)
    socketkeylist=list(socketdict.keys())
    path="/proc/"+str(pid)+"/fd" #进程的文件描述符的绝对路径
    upnetspeed=0
    downnetspeed=0
    if not os.path.exists(path): #判断路径是否存在
        return upnetspeed,downnetspeed
      
    filelist=os.listdir(path)
    for filename in filelist:
        pathname=os.path.join(path,filename)
        #if not os.path.exists(pathname): #判断路径是否存在
        #   continue
        try:
            if os.path.islink(pathname):
                if(os.readlink(pathname).split(":")[0]=='socket'):
                    inodenumber= re.findall("\d+",os.readlink(pathname))[0] #通过正则表达式找出inode               
                    #socketinfo=socketfile()
                    if inodenumber in socketinfo: #找到进程的socket信息                    
                        #t=socketinfo[inodenumber]
                        #tempdict=copy.deepcopy(socketdict)
                        if socketinfo[inodenumber] in socketkeylist:
                            upnetspeed=upnetspeed+socketdict[socketinfo[inodenumber]]
                        
                        temp=(socketinfo[inodenumber][3],socketinfo[inodenumber][4],socketinfo[inodenumber][2],socketinfo[inodenumber][0],socketinfo[inodenumber][1])
                        if temp in socketkeylist:
                            downnetspeed=downnetspeed+socketdict[temp]
        except Exception:
            pass
                        
                    
    return upnetspeed,downnetspeed

#清空soketdict
def clearsoketdict():
    socketdict.clear()







'''                       
while(1):
    time.sleep(1) #因为收集的是一秒中的上传和下载，因此就是网速
    socketinfo=socketfile()
    ps=psutil.pids()
    for pid in ps:
        up,down=processNetSpeed(pid,socketinfo)
        print("pid:",pid,"    ","up:",up,"   ","down:",down)
        print("\n")
   
    socketdict.clear()
    

def marry(inodenumber,upnetspeed,downnetspeed):
    global socketdict
    socketinfo=socketfile()
    if inodenumber in socketinfo:
        print("找到了")
        socketkey=socketinfo[inodenumber]
        if socketkey in socketdict:
            print("zhaodaole")
            upnetspeed=upnetspeed+socketdict[socketkey]
            return
        temp=(socketkey[3],socketkey[4],socketkey[2],socketkey[0],socketkey[1]) 
        if temp in socketdict:
            downnetspeed=downnetspeed+socketdict[temp]
            return 
    return
    '''
