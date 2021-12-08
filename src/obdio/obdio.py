import obd
import socketio
import uvicorn

class OBDio(obd.Async):
    """
        The OBDio class extends the obd.Async class. It does not have an __init__ method so that
        arguments match up with obd.Async/OBD. Upon creation of an OBDio object a connection to 
        the vehicle will be initiated but is not guarenteed (at least in my experience).
    """
    def create_server(self, **kwargs):
        """
            Creates the python-socketio Server instance using same arguments and sets up some default 
            events from the python-OBD API. 
        """
        self.socket = socketio.AsyncServer(**kwargs, async_mode='asgi')
        sio = self.socket

        @sio.event
        async def status(sid, data):
            await sio.emit('status', self.status(), room=sid)

        @sio.event
        async def is_connected(sid):
            await sio.emit('is_connected', self.is_connected(), room=sid)

        @sio.event
        async def port_name(sid):
            await sio.emit('port_name', self.port_name(), room=sid)

        @sio.event
        async def supports(sid, cmd):
            await sio.emit('supports', self.supports(obd.commands[cmd]), room=sid)

        @sio.event
        async def protocol_id(sid):
            await sio.emit('protocol_id', self.protocol_id(), room=sid)

        @sio.event
        async def protocol_name(sid):
            await sio.emit('protocol_name', self.protocol_name(), room=sid)

        @sio.event
        async def supported_commands(sid):
            await sio.emit('supported_commands', self.supported_commands, room=sid)

        @sio.event
        async def query(sid, cmd):
            await sio.emit('query', self.query(obd.commands[cmd]), room=sid)

        @sio.event
        async def start(sid):
            self.start()

        @sio.event
        async def stop(sid, data):
            self.stop()

        @sio.event
        async def watch(sid, commands):
            self.stop()
            commands = list(commands)
            for cmd in commands:
                self.watch(obd.commands[cmd], self.watch_callback)
            self.start()

        @sio.event
        async def unwatch(sid, commands):
            self.stop()
            commands = list(commands)
            for cmd in commands:
                self.unwatch(obd.commands[cmd])
            self.start()

        @sio.event
        async def unwatch_all(sid):
            self.stop()
            self.unwatch_all()

        @sio.event
        async def has_name(sid, name):
            await sio.emit('has_name', obd.commands.has_name(name), room=sid)
        
        @sio.event
        async def close(sid):
            self.close()

        return sio

    def watch_callback(response):
        """ Placeholder watch response callback. Should be reassigned with a custom implementation by the user of the module. """
        pass

    def create_event(self, name, handler):
        """ Create custom events by name and custom handler logic """
        sio = self.socket
        @sio.on(name)
        async def custom_event(sid, data=None):
            await handler(sid, data)

    def serve_static(self, static_files):
        """ To set your server's static content before running the server """
        self.static_files = static_files

    def run_server(self, **config):
        """ To start the server on some host:port at a later time so more events can be defined on top of whats already there. """
        
        # Check for static content
        if hasattr(self, 'static_files'):
            static = self.static_files
        else:
            static = {}

        app = socketio.ASGIApp(self.socket, static_files=static)
        uvicorn.run(app, **config)