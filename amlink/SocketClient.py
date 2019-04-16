import json
import socket
import threading

import amlink


class Request:

    @staticmethod
    def createReq(id, uid, command, arguments):
        req = {"id": id,
               "uid": uid,
               "command": command,
               "arguments": arguments
               }
        return json.dumps(req).encode("utf-8")


class Response:

    def __init__(self, id, uid, status, message, data):
        self.id = id
        self.uid = uid
        self.status = status
        self.message = message
        self.data = data

    @classmethod
    def initFromResp(cls, resp):
        try:
            respJson = json.loads(resp)
            return cls(respJson["id"], respJson["uid"], respJson["status"], respJson["message"], respJson['data'])
        except:
            return None


class Client:
    def __init__(self, ip, port, pwd):
        if ip:
            self.ip = ip
        else:
            self.ip = 'localhost'

        if port:
            self.port = port

        if pwd:
            self.pwd = pwd
        else:
            self.pwd = ''

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect(pwd)

    def _connect(self, pwd):
        self.socket.connect((self.ip, self.port))
        self._send(pwd)

    def send(self, id, uid, command, arguments):
        req = Request.createReq(id, uid, command, arguments)
        self._send(req)

    def _send(self, msg):
        self.socket.send(msg)

    def recv(self):
        try:
            resp = self._recv()
            resp = resp.decode()
            resp = Response.initFromResp(resp)
            return resp
        except:
            return None

    def _recv(self, mtu=65535):
        return self.socket.recv(mtu)

    def close(self):
        self.socket.close()


class _ClientThread(threading.Thread):
    def __init__(self, ip, port, pwd):
        super(_ClientThread, self).__init__()
        self.client = Client(ip, port, pwd)

    def run(self):
        try:

            while True:
                resp = self.client.recv()
                handel_recv(resp)
        except:
            return None

    def stop(self):
        self.client.close()


def handel_recv(resp):
    id = resp.id
    uid = resp.uid
    status = resp.status
    message = resp.message
    data = resp.data

    if message == 'success':
        intent = data['intent']
        ner = parse_ner(data['ner'])
        return_value = amlink.module_controller.intents[intent].__call__(ner, uid)
        amlink.NetworkHandler.toClient(id, status, message, return_value)
    else:
        return ''


def parse_ner(ner):
    output = []
    last_label = ''

    for i in ner:
        word = i[0]
        label = i[1]

        if label != '':
            if label == last_label:  # consecutive words
                index = len(output[label]) - 1
                output[label][index] = output[label][index], word
            else:
                output[label].append(word)

        last_label = label

    return output


def start_client(ip, port, pwd):
    thread = _ClientThread(ip, port, pwd)
    thread.start()
    return thread
