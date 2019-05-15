import json
import queue
import socket
import struct
import threading


class Request:

    @staticmethod
    def createReq(id, command, arguments):
        req = {"id": id,
               "command": command,
               "arguments": arguments
               }
        return json.dumps(req)


class Response:

    def __init__(self, id, status, message, data):
        self.id = id
        self.status = status
        self.message = message
        self.data = data

    @classmethod
    def initFromResp(cls, resp):
        respJson = json.loads(resp)
        return cls(respJson["id"], respJson["status"], respJson["message"], respJson['data'])


class Client:
    def __init__(self, ip, port):
        if ip:
            self.ip = ip
        else:
            self.ip = 'localhost'

        if port:
            self.port = port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, pwd):
        self.socket.connect((self.ip, self.port))
        self._send(pwd)

    def send(self, id, command, arguments):
        req = Request.createReq(id, command, arguments)
        print(req)
        self._send(req)

    def _send(self, data):
        data = data.encode('utf-8')
        length = len(data)
        self.socket.sendall(struct.pack('!I', length))
        self.socket.sendall(data)

    def _recvall(self, count):
        buf = b''
        while count:
            newbuf = self.socket.recv(count)
            if not newbuf:
                return None
            buf += newbuf
            count -= len(newbuf)
        return buf

    def _recv(self):
        lengthbuf = self._recvall(4)
        length, = struct.unpack('!I', lengthbuf)
        return self._recvall(length)

    def recv(self):
        try:
            resp = self._recv()
            resp = resp.decode()
            print(resp)
            resp = Response.initFromResp(resp)
            return resp

        finally:
            return None

    def close(self):
        self.socket.close()


def create_client_thread(ip, port, pwd, sendQueue):
    client = Client(ip, port)
    queue = sendQueue
    sendThread = threading.Thread(target=send_queue, args=(client, queue))
    sendThread.daemon = True
    client.connect(pwd)

    sendThread.start()
    # self.queue.put({'id': 0, 'command': 'getModels', 'arguments': ''})

    while True:
        resp = client.recv()
        if resp is None or resp is "":
            continue
        print('Recv:', resp)
        # amlink.NetworkHandler.toClient(resp)


def send_queue(client, queue):
    while True:
        if not queue.empty():
            result = queue.get()
            print(result, 'queue')
            client.send(result['id'], result['command'], result['arguments'])
            queue.task_done()


def start_client(ip, port, pwd):
    sendQueue = queue.Queue(0)
    thread = threading.Thread(target=create_client_thread, args=(ip, port, pwd, sendQueue))
    thread.daemon = True
    thread.start()
    return thread, sendQueue


thread, sendQueue = start_client('127.0.0.1', 5001, 'xAsiimov,test_password')
print('Send getWaifus')
sendQueue.put({'id': '114514', 'command': 'getSystemInfo', 'arguments': ''})

while True:
    pass
