#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, and Dalton Ronan
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

from random import paretovariate
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    def get_host_port(self, url):
        netloc = url.netloc
        try:
            host, port = netloc.split(':')
        except:
            host = netloc
            port = '80'
        return host, port

    def connect(self, host, port):
        host_ip = socket.gethostbyname(host)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host_ip, int(port)))
        return None

    def get_code(self, data):
        status_line = data.split('\r\n')[0]
        status_code = status_line.split()[1]
        return int(status_code)

    def get_headers(self, data):
        headers = data.split('\r\n\r\n')[0]
        return headers

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')
    
    def build_GET_header(self, path, host, port, query=None):
        if not path:
            path = '/'
        if query:
            request_line = 'GET %s HTTP/1.1\r\n' % '?'.join([path, query])
        else:
            request_line = 'GET %s HTTP/1.1\r\n' % path
        if port != 80:
            host_line = 'Host: %s\r\n' % host
        else:
            host_line = 'Host: %s:%s\r\n' % (host, port)
        user_agent = 'User-Agent: agent/0.0.7\r\n'
        accept = 'Accept: */*\r\n'
        connection = 'Connection: close\r\n'
        return request_line + host_line + user_agent + accept + connection + '\r\n'

    def GET(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)
        host, port = self.get_host_port(parsed_url)
        path = parsed_url.path
        query = parsed_url.query
        self.connect(host, port)
        self.sendall(data=self.build_GET_header(path, host, port, query))
        data = self.recvall(self.socket)
        headers = self.get_headers(data)
        code = self.get_code(headers)
        body = self.get_body(data)
        self.close()
        return HTTPResponse(code, body)

    def build_POST_header(self, path, host, port, length=0):
        if not path:
            path = '/'
        request_line = 'POST %s HTTP/1.1\r\n' % path
        if port != 80:
            host_line = 'Host: %s\r\n' % host
        else:
            host_line = 'Host: %s:%s\r\n' % (host, port)
        user_agent = 'User-Agent: agent/0.0.7\r\n'
        accept = 'Accept: */*\r\n'
        connection = 'Connection: close\r\n'
        content_type = 'Content-Type: application/x-www-form-urlencoded\r\n'
        content_length = 'Content-length: %s\r\n' % length
        return request_line + host_line + user_agent + accept + connection + content_type + content_length + '\r\n'

    def build_POST_body(self, args=None):
        body = bytearray()
        if args:
            for arg in args:
                body.extend(arg.encode('utf-8'))
                body.extend('='.encode('utf-8'))
                body.extend(args[arg].encode('utf-8'))
                body.extend('&'.encode('utf-8'))
            body = body[:-1]
        return body

    def POST(self, url, args=None):
        parsed_url = urllib.parse.urlparse(url)
        req_body = self.build_POST_body(args).decode()
        host, port = self.get_host_port(parsed_url)
        path = parsed_url.path
        self.connect(host, port)
        self.sendall(data=self.build_POST_header(path, host, port, len(req_body)) + req_body)
        data = self.recvall(self.socket)
        headers = self.get_headers(data)
        code = self.get_code(headers)
        body = self.get_body(data)
        self.close()
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
