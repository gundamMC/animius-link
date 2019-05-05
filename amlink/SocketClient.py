import json
import queue
import socket
import struct
import threading

import amlink


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


class ClientThread(threading.Thread):
    def __init__(self, ip, port, pwd, sendQueue):
        threading.Thread.__init__(self)
        self.pwd = pwd
        self.client = Client(ip, port)
        self.queue = sendQueue
        self.sendThread = threading.Thread(target=self.send_queue, args=())

    def run(self):
        self.client.connect(self.pwd)
        self.sendThread.start()
        # self.queue.put({'id': 0, 'command': 'getModels', 'arguments': ''})

        while True:
            resp = self.client.recv()
            if resp is None or resp is "":
                continue
            amlink.NetworkHandler.toClient(resp)

    def send_queue(self):
        while True:
            if not self.queue.empty():
                result = self.queue.get()
                print(result, 'queue')
                self.client.send(result['id'], result['command'], result['arguments'])
                self.queue.task_done()

    def stop(self):
        self.sendThread.join()
        self.client.close()


def start_client(ip, port, pwd):
    sendQueue = queue.Queue(0)
    thread = ClientThread(ip, port, pwd, sendQueue)
    thread.run()
    return thread, sendQueue


def parse_ner(sentence, ner):
    # sentence and ner should be two lists of strings
    # e.g.
    # sentence = ['weather', 'in', 'san', 'francisco', 'tonight', 'at', '6', 'pm', '?']
    # ner = ['', '', 'place', 'place', 'time', '', 'time', 'time', '']

    output = {}  # dict of list
    last_label = ''

    for i in range(len(sentence)):
        word = sentence[i]
        label = ner[i]

        if label != '':
            if label == last_label:  # consecutive words
                output[label][-1] = output[label][-1] + ' ' + word
            else:
                if label in output:  # already existing label
                    output[label].append(word)
                else:  # new label
                    output[label] = [word]

        last_label = label

    return output
