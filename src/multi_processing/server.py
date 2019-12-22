'''
Created on Aug 15, 2017

@author: foxbat
'''
import sys
import os
path = os.getcwd()
path = os.path.dirname(path)
sys.path.append(path)

from multiprocessing import Queue, Process
from multiprocessing.managers import BaseManager
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, hashlib, random
from socketserver import ThreadingMixIn
import datetime


SERVER_IP = '192.168.1.102'
SERVER_PORT = 1240

TIME_OUT = 60
MASTER_RESULT_MAP = {}

MASTER_TO_SLAVE_QUEUE = Queue(maxsize = 100)
SLAVE_TO_MASTER_QUEUE = Queue(maxsize = 100)

def mapReduce(MASTER_TO_SLAVE_QUEUE, SLAVE_TO_MASTER_QUEUE):
    # 参数初始化
    print('初始化完毕，准备接收任务')
    # Map步
    while True:
        # 接收新任务,处理
        hasToTask = 0
        while True:
            taskMd5, path, dataList = (
                MASTER_TO_SLAVE_QUEUE).get()
            print('dataList', dataList)
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



class TestHTTPHandle(BaseHTTPRequestHandler):

    def writeBack(self, taskMd5, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        resultData = json.dumps(data).encode('utf-8')
        self.wfile.write(resultData)

    def do_POST(self):
        # 接收网络请求
        # self.rfile._sock.settimeout(60)
        data = self.rfile.read(int(self.headers['content-length']))
        # 将网络请求解析成task
        dataList = json.loads(data.decode('utf-8'))
        print(dataList)
        # 验证用户合法性
        taskMd5 = hashlib.md5(
               (path + str(time.time()) + \
                str(dataList) + str(random.randint(0, 100000000))).\
                              encode(encoding='utf_8')).hexdigest()
        start = time.time()
        validateResult = 'success'
        if validateResult == 'success':
            sucess = 0
            try:
                flag = True
                while flag:
                    if (MASTER_TO_SLAVE_QUEUE).qsize()<20:
                        (MASTER_TO_SLAVE_QUEUE).put(
                            [taskMd5, self.path, dataList])
                        sucess = 1
                        flag = False
                    else :
                        time.sleep(0.01)
                
            except Exception as e:
                print(e)
                sucess = 0
            print("finish putting data into master_to_slave queue")
            if sucess == 1:
                # 准备接收任务
                result = []
                while taskMd5 not in MASTER_RESULT_MAP:
                    # 接收所有结果
                    while True:
                        try :
                            #print('MASTER_RESULT_MAP', MASTER_RESULT_MAP)
                            tempResult = (SLAVE_TO_MASTER_QUEUE).get_nowait()
                            MASTER_RESULT_MAP[tempResult[0]] = tempResult[1]
                        except :
                            break
                    
                    if taskMd5 not in MASTER_RESULT_MAP:
                        end = time.time()
                        if end - start > TIME_OUT:
                            self.writeBack(taskMd5, 'slave 超时没有返回结果')
                            return
                        else:
                            time.sleep(0.01)
                # 再次查找该task的结果，如果有了，回写结果，从结果池里删除，跳出循环，结束线程
                if taskMd5 in MASTER_RESULT_MAP:
                    result = MASTER_RESULT_MAP[taskMd5]
                    self.writeBack(taskMd5, result)
#                     print(len(runTime.MASTER_RESULT_MAP))
                    del MASTER_RESULT_MAP[taskMd5]
                    return
                else:
                    self.writeBack(taskMd5, '在master结果池里找不到返回结果')
                    return
            else:

                self.writeBack(taskMd5, '向MASTER_TO_SLAVE_QUEUE放入数据失败')
                return
        else:
            self.writeBack(taskMd5, validateResult)
            return


class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
    pass




def start_server(ip, port):

    myServer = ThreadingHttpServer((ip, int(port)), TestHTTPHandle)
    print('初始化完毕，准备接收任务')
    myServer.serve_forever()
    
    
if __name__ == '__main__':
#     p = Process(target=start_server, args=(SERVER_IP, SERVER_PORT))
#     p.start()
    #
    for i in range(1):
        p = Process(target=mapReduce, args=(MASTER_TO_SLAVE_QUEUE, SLAVE_TO_MASTER_QUEUE))
        p.start()
    start_server(SERVER_IP, SERVER_PORT)
