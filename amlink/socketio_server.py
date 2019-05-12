import asyncio

import uvicorn

import socketio

# create a Socket.IO server
import amlink

sio = socketio.AsyncServer(async_mode='asgi')

# wrap with ASGI application
app = socketio.ASGIApp(sio)


class MyCustomNamespace(socketio.AsyncNamespace):

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


sio.register_namespace(MyCustomNamespace())

uvicorn.run(app, host='192.168.0.50', port=5000)
