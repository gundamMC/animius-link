import json
import socket
import threading

import amlink


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
        self._send(req)

    def _send(self, msg):
        self.socket.send(str.encode(msg))

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


class ClientThread(threading.Thread):
    def __init__(self, ip, port, pwd):
        threading.Thread.__init__(self)
        self.pwd = pwd
        self.client = Client(ip, port)

    def run(self):
        try:
            self.client.connect(self.pwd)

            while True:
                resp = self.client.recv()
                amlink.NetworkHandler.toClient(resp)

        except:
            return None

    def stop(self):
        self.client.close()


def start_client(ip, port, pwd):
    if __name__ == "amlink.SocketClient":
        thread = ClientThread(ip, port, pwd)
        thread.run()
        return thread


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
