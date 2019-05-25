import socketio
import uvicorn

# create a Socket.IO server
import amlink


class SocketIOServer:

    def __init__(self):

        sio = socketio.AsyncServer(async_mode='asgi')

        # wrap with ASGI application
        app = socketio.ASGIApp(sio)

        class DefaultNamespace(socketio.AsyncNamespace):

            # def __init__(self):
            #     super().__init__()
            #
            #     self.users = []

            async def on_connect(self, sid, environ):
                print('connected')

            async def on_disconnect(self, sid):
                pass

            async def on_auth(self, sid, data):
                print('==========')
                print(data)
                print('==========')

                if 'username' not in data or 'password' not in data:
                    return False

                user = amlink.users.get_user(data['username'])

                if user is None or not user.checkPassword(data['password']):
                    return 'The username or password is incorrect'

                await sio.save_session(sid, {'username': data['username']})
                return True

            async def on_register(self, sid, data):
                if amlink.config['allow_registration']:
                    if 'username' in data and 'password' in data:
                        amlink.users.create_user(data['username'], data['password'])
                        await sio.save_session(sid, {'username': data['username']})

                        return True
                    else:
                        return 'Username and password must be included'
                else:
                    return 'Registration is disabled'

            # async def on_waifu_list(self, sid, data):

        sio.register_namespace(DefaultNamespace())

        uvicorn.run(app, host='192.168.0.50', port=5000)
