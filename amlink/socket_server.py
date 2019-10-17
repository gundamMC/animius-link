import asyncio
import json
import struct
import time

from amlink import utils, module_controller


class NetworkProtocol:
    @staticmethod
    async def await_write(writer, data):
        writer.write(struct.pack('!I', len(data)))
        writer.write(data)
        await writer.drain()

    @staticmethod
    async def await_receive(reader):
        length_buf = await reader.read(4)
        length, = struct.unpack('!I', length_buf)
        return await reader.read(length)

    @staticmethod
    def create_request(request_id, command, arguments):
        if request_id is None:
            request_id = time.time()
        request = {"id": request_id,
                   "command": command,
                   "arguments": arguments
                   }
        return json.dumps(request).encode("utf-8")

    @staticmethod
    def parse_request(request):
        request = request.decode()
        data = json.loads(request)
        return data["id"], data["command"], data["arguments"]

    @staticmethod
    def create_response(response_id, status, message, data):
        response = {"id": response_id,
                    "status": status,
                    "message": message,
                    "data": data
                    }
        return json.dumps(response).encode("utf-8")

    @staticmethod
    def parse_response(response):
        response = response.decode()
        data = json.loads(response)
        print(response)
        return data["id"], data["status"], data["message"], data["data"]


class ConnectEngine:
    def __init__(self, socket_server, engine_ip, engine_port, pwd):
        self.socket_server = socket_server
        self.engine_ip = engine_ip
        self.engine_port = engine_port
        self.pwd = pwd
        self.reader = self.writer = None
        asyncio.run(self.connect())

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.engine_ip, self.engine_port)
        valid_session, auth_message = await self.send_auth(self.writer)

        while valid_session:
            raw_response = await NetworkProtocol.await_receive(self.reader)
            response_id, message, status, data = NetworkProtocol.parse_response(raw_response)

            if response_id in self.socket_server.pending_requests:
                link_process = self.socket_server.pending_requests[response_id][1]
                username = self.socket_server.pending_requests[response_id][2]

                if link_process and 'intent' in data.keys and 'ner' in data.keys:
                    intent = data['intent']
                    ner = self.parse_ner(data['ner'][0], data['ner'][1])
                    return_value = module_controller.intents[intent].__call__(ner, username)
                    return_value['intent'] = intent
                else:
                    return_value = data

                response = NetworkProtocol.create_response(response_id, message, status, json.dumps(return_value))
                await NetworkProtocol.await_write(self.socket_server.pending_requests[response_id][0], response)
                self.socket_server.pending_requests.pop(response_id, None)

    async def send_auth(self, writer):
        auth = NetworkProtocol.create_request(None, "login", {"pwd": self.pwd})
        await NetworkProtocol.await_write(writer, auth)
        return True, "success"

    async def send_request(self, request_id, command, arguments):
        request = NetworkProtocol.create_request(request_id, command, arguments)
        await NetworkProtocol.await_write(self.writer, request)

    @staticmethod
    def parse_ner(sentence, ner):
        # sentence and ner should be two lists of strings
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


class SocketServer:
    def __init__(self, link_port, local, pwd, max_clients, engine_ip, engine_port):
        self.host = '127.0.0.1' if local else '0.0.0.0'
        self.link_port = link_port
        self.pwd = pwd
        self.max_clients = max_clients
        self.server = None
        self.engine = ConnectEngine(self, engine_ip, engine_port, pwd)
        self.pending_requests = {}

    def start_server(self):
        asyncio.run(self.main())

    def stop_server(self):
        self.server._shutdown_request = True

    async def await_auth(self, reader):
        auth_info = await NetworkProtocol.await_receive(reader)
        request_id, command, arguments = NetworkProtocol.parse_request(auth_info)
        if command == 'login' and arguments['pwd'] == self.pwd:
            return True, "success", arguments['username']
        else:
            return False, "invalid password", None

    async def handle_connection(self, reader, writer):
        valid_session, auth_message, username = await self.await_auth(reader)

        while valid_session:
            raw_request = await NetworkProtocol.await_receive(reader)
            request_id, command, arguments = NetworkProtocol.parse_request(raw_request)

            local_commands = {'amlinkExit': utils.amlink_exit,
                              'amlinkCheckUpdate': utils.amlink_check_update,
                              'amlinkCheckInternet': utils.amlink_check_internet}

            if command not in local_commands:

                await self.engine.send_request(request_id, command, arguments)
                link_process = False if command == 'waifuPredict' else True
                self.pending_requests[request_id] = [writer, link_process, username]
            else:
                status, message, data = local_commands[command].__call__()
                response = NetworkProtocol.create_response(request_id, status, message, data)
                await NetworkProtocol.await_write(writer, response)

        writer.close()

    async def main(self):
        self.server = await asyncio.start_server(self.handle_connection, self.host, self.link_port)
        await self.server.serve_forever()
