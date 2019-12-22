'''
Created on 2017年9月20日

@author: xxlu

'''
import sys
import os
path = os.getcwd()
path = os.path.dirname(path)
sys.path.append(path)

from multiprocessing import Queue, Process
from multiprocessing.managers import BaseManager
import time
import requests,random


class QueueManager(BaseManager):
    pass

QueueManager.register('master2SlaveQueue')
QueueManager.register('slave2MasterQueue')
# QueueManager.register('hanlp2MasterQueue')
# QueueManager.register('master2HanlpQueue')

MASTER_IP = '192.168.1.203'
MASTER_PORT = 1238
m = QueueManager(
    address=(MASTER_IP, MASTER_PORT), authkey=b'abc')
m.connect()
MASTER_TO_SLAVE_QUEUE = m.master2SlaveQueue()
SLAVE_TO_MASTER_QUEUE = m.slave2MasterQueue()
# runTime.HANLP_TO_MASTER = m.hanlp2MasterQueue()
# runTime.MASTER_TO_HANLP = m.master2HanlpQueue()
ARTICLE_MAP = {}
SUB_TO_CENTER_QUEUE  = Queue()

def mapReduce():
    # 参数初始化
    print('初始化完毕，准备接收任务')
    # Map步
    while True:
        # 接收新任务,处理
        hasToTask = 0
        while True:
            taskMd5, path, dataList = (
                MASTER_TO_SLAVE_QUEUE).get()
            #print('dataList', dataList)
            flag =True
            import time
            time.sleep(0.05)
            while flag :
                if (SLAVE_TO_MASTER_QUEUE).qsize()<20:
                    (SLAVE_TO_MASTER_QUEUE).put( [taskMd5, [dataList, 110]])
                    flag =False
                else :
                    time.sleep(0.01)
            
        # 如果本次既没有任务也没有任何结果，休息一下
        if hasToTask == 0:
            time.sleep(0.001)
if __name__ == '__main__':
    #mapReduce()
    for i in range(10):
        p = Process(target=mapReduce)
        p.start()
    
