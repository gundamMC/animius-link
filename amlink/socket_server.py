import asyncio
import json
import struct
import time


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
    def __init__(self, engine_ip, engine_port, pwd):
        self.engine_ip = engine_ip
        self.engine_port = engine_port
        self.pwd = 'p@ssword'
        self.reader = self.writer = None
        asyncio.run(self.connect())

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.engine_ip, self.engine_port)
        await self.send_auth(self.writer)

    async def send_auth(self, writer):
        auth = NetworkProtocol.create_request(None, "login", {"pwd": self.pwd})
        await NetworkProtocol.await_write(writer, auth)
        await self.send_request(None, "getWaifu", "")
        print(await NetworkProtocol.await_receive(self.reader))

    async def send_request(self, id, command, arguments):
        request = NetworkProtocol.create_request(id, command, arguments)
        await NetworkProtocol.await_write(self.writer, request)


class SocketServer:
    def __init__(self, link_port, local, pwd, max_clients, engine_ip, engine_port):
        self.host = '127.0.0.1' if local else '0.0.0.0'
        self.link_port = link_port
        self.pwd = pwd
        self.max_clients = max_clients
        self.server = None
        self.engine = ConnectEngine(engine_ip, engine_port, pwd)

    def start_server(self):
        asyncio.run(self.main())

    def stop_server(self):
        self.server._shutdown_request = True

    async def await_auth(self, reader):
        auth_info = await NetworkProtocol.await_receive(reader)
        request_id, command, arguments = NetworkProtocol.parse_request(auth_info)
        if command == 'login' and arguments['pwd'] == self.pwd:
            return True, "Success"
        else:
            return False, "Invalid password"

    async def handle_connection(self, reader, writer):
        address = writer.get_extra_info('peername')
        valid_session, message = await self.await_auth(reader)

        while valid_session:
            raw_request = await NetworkProtocol.await_receive(reader)
            request_id, command, arguments = NetworkProtocol.parse_request(raw_request)
            # request_id, status, message, data

            # response = NetworkProtocol.create_response(request_id, status, message, data)
            # await SocketServer.await_write(writer, response)

        writer.close()

    async def main(self):
        self.server = await asyncio.start_server(self.handle_connection, self.host, self.link_port)
        await self.server.serve_forever()
