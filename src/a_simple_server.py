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


class TestHTTPHandle(BaseHTTPRequestHandler):

    def writeBack(self, data):
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
        result = {"data": "收到啦"}
        self.writeBack(result)
        return


class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
    pass

def start_server(ip, port):

    myServer = ThreadingHttpServer((ip, int(port)), TestHTTPHandle)
    print('初始化完毕，准备接收任务')
    myServer.serve_forever()
    
if __name__ == '__main__':
    start_server(SERVER_IP, SERVER_PORT)
