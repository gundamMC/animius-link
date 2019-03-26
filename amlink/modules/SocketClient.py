import socket
import json
import threading


class Request:

    @staticmethod
    def createReq(id, command, arguments):
        req = {"id": id,
               "command": command,
               "arguments": arguments
               }
        return json.dumps(req).encode("utf-8")


class Response:

    def __init__(self, id, status, message, data):
        self.id = id
        self.status = status
        self.message = message
        self.data = data

    @classmethod
    def initFromResp(cls, resp):
        try:
            respJson = json.loads(resp)
            return cls(respJson["id"], respJson["status"], respJson["message"], respJson['data'])
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

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._connect(pwd)

    def _connect(self, pwd):
        self.client.connect((self.ip, self.port))
        self._send(pwd)

        thread = _ClientThread(self)
        thread.start()

    def send(self, id, command, arguments):
        req = Request.createReq(id, command, arguments)
        self._send(req)

    def _send(self, msg):
        self.client.send(msg)

    def close(self):
        self.client.close()


class _ClientThread(threading.Thread):
    def __init__(self, client):
        super(_ClientThread, self).__init__()
        self.client = client

    def run(self):
        try:
            while True:
                resp = self.client.recv(65535)
                resp = resp.decode()
                resp = Response.initFromResp(resp)
                handel_recv(resp)

        except:
            return None


def handel_recv(resp):
    id = resp.id
    status = resp.status
    message = resp.message
    data = resp.data

    pass
