import asyncio
import json
import struct
import threading
import time

from amlink import socket_server, config, socketio_server


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


class NetworkController:

    def __init__(self):
        cfg = config.get_config()
        self.ip = cfg['ip']
        self.socket_port = cfg['socket_port']
        self.socketio_port = cfg['socket.io_port']
        self.engine_port = cfg['engine_port']
        self.engine_passowrd = cfg['engine_password']

        self.socket_server = socket_server.SocketServer(self.socket_port, True, self.engine_passowrd, 10, self.ip,
                                                        self.engine_port)
        socket_server_thread = threading.Thread(target=asyncio.run, args=(self.socket_server.main(),), daemon=True)
        socket_server_thread.start()

        self.socketio = socketio_server.SocketIOServer()
        self.socketio.start('127.0.0.1', self.socketio_port, self.ip, self.engine_port, self.engine_passowrd, )
