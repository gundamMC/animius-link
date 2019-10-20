import asyncio

from amlink import utils, connect_engine, network_controller


class SocketServer:
    def __init__(self, link_port, local, pwd, max_clients, engine_ip, engine_port):
        self.host = '127.0.0.1' if local else '0.0.0.0'
        self.link_port = link_port
        self.engine_ip = engine_ip
        self.engine_port = engine_port
        self.pwd = pwd
        self.max_clients = max_clients
        self.engine = self.server = None
        self.pending_requests = {}

    async def main(self):
        self.engine = connect_engine.Connect(self.engine_ip, self.engine_port, self.pwd, self, False)
        self.server = await asyncio.start_server(self.handle_connection, self.host, self.link_port)
        await self.engine.connect()

    def stop_server(self):
        self.server._shutdown_request = True

    async def await_auth(self, reader):
        auth_info = await network_controller.NetworkProtocol.await_receive(reader)
        request_id, command, arguments = network_controller.NetworkProtocol.parse_request(auth_info)
        if command == 'login' and arguments['pwd'] == self.pwd:
            return True, "success", arguments['username']
        else:
            return False, "invalid password", None

    async def handle_connection(self, reader, writer):
        valid_session, auth_message, username = await self.await_auth(reader)

        while valid_session:
            raw_request = await network_controller.NetworkProtocol.await_receive(reader)
            request_id, command, arguments = network_controller.NetworkProtocol.parse_request(raw_request)

            local_commands = {'amlinkExit': utils.amlink_exit,
                              'amlinkCheckUpdate': utils.amlink_check_update,
                              'amlinkCheckInternet': utils.amlink_check_internet}

            if command not in local_commands:

                await self.engine.send_request(request_id, command, arguments)
                link_process = True if command == 'waifuPredict' else False
                self.pending_requests[request_id] = [writer, link_process, username]
            else:
                status, message, data = local_commands[command].__call__()
                response = network_controller.NetworkProtocol.create_response(request_id, status, message, data)
                await network_controller.NetworkProtocol.await_write(writer, response)

        writer.close()
