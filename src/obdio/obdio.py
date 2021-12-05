import obd
import socketio
import eventlet

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
        self.socket = socketio.Server(**kwargs)
        sio = self.socket

        @sio.event
        def connect(sid, environ, auth):
            """ Reserved event """
            print("Client connected", sid)

        @sio.event
        def status(sid, data):
            sio.emit('status', self.status(), room=sid)

        @sio.event
        def is_connected(sid):
            sio.emit('is_connected', self.is_connected(), room=sid)

        @sio.event
        def port_name(sid):
            sio.emit('port_name', self.port_name(), room=sid)

        @sio.event
        def supports(sid, cmd):
            sio.emit('supports', self.supports(obd.commands[cmd]), room=sid)

        @sio.event
        def protocol_id(sid):
            sio.emit('protocol_id', self.protocol_id(), room=sid)

        @sio.event
        def protocol_name(sid):
            sio.emit('protocol_name', self.protocol_name(), room=sid)

        @sio.event
        def supported_commands(sid):
            sio.emit('supported_commands', self.supported_commands, room=sid)

        @sio.event
        def query(sid, cmd):
            self.sio.emit('obd_query', self.query(obd.commands[cmd]), room=sid)

        @sio.event
        def start(sid):
            self.start()

        @sio.event
        def stop(sid, data):
            self.stop()

        @sio.event
        def watch(sid, commands):
            self.stop()
            commands = list(commands)
            for cmd in commands:
                self.watch(obd.commands[cmd], self.watch_callback)
            self.start()

        @sio.event
        def unwatch(sid, commands):
            self.stop()
            commands = list(commands)
            for cmd in commands:
                self.unwatch(obd.commands[cmd])
            self.start()

        @sio.event
        def unwatch_all(sid):
            self.stop()
            self.unwatch_all()

        @sio.event
        def has_name(sid, name):
            sio.emit('has_name', obd.commands.has_name(name), room=sid)
        
        @sio.event
        def close(sid):
            self.close()

        return sio

    def listen(self, port):
        """ To start the server on some port at a later time so more events can be defined on top of whats already there. """
        app = socketio.WSGIApp(self.socket)
        eventlet.wsgi.server(eventlet.listen(('127.0.0.1', port)), app)

    def watch_callback(response):
        """ Placeholder watch response callback. Should be reassigned with a custom implementation by the user of the module. """
        pass

    def create_event(self, name, handler):
        """ Create custom events by name and custom handler logic """
        sio = self.socket
        @sio.on(name)
        def custom_event(sid, data=None):
            handler(sid, data)