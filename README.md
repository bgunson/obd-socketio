# obd-socketio

Quickly create a [python-socketio](https://pypi.org/project/python-socketio/) server with events corresponding to the [python-OBD](https://pypi.org/project/obd/) API. Ideal for controlling an Async connection to a vehicle from a JavaScript socketio client. The module provides default events which correspond to python-OBD methods as well as JSON encoding for its types.

An example use case would be to use the server on a wireless hotspot enabled Raspberry Pi running and be able to interact with the connection from another device in a browser. You can use the default events which will behave as python-OBD does or build your own custom websocket/OBD2 API.

## Installation
```
pip install obd-socketio
```

## Basic Usage
```
import obdio

io = obdio.OBDio()  # creates an obd connection, class extends obd.Async

io.create_server()   # exposes events named by the python-OBD API

io.listen(48484)  # listen on port 48484
```

## API

### OBDio class
Initiaties the OBD connection to the vehicle. This class extends obd.Async (and therefore obd.OBD) so all aguments are the same, see [OBD connections](https://python-obd.readthedocs.io/en/latest/Connections/) for more args.

### create_server(**kwargs)
- Returns the server socket

Creates the socketio server instance and gives you access to the socket after being called. `create_server()` passes its arguments to python-socketio's [Server class](https://python-socketio.readthedocs.io/en/latest/api.html#server-class) giving you control over its behaviour as well as engineIO configuration. For example
```
import obdio

io = obdio.OBDio()

sio = io.create_server(cors_allowed_origins='*', json=obdio)   # use obdio as the json module for obd support

sio.emit('event') # now you can use the socket
```
The json parameter can be substituted for your own or the built-in (`import json`) module though it cannot serialize some of the obd types.

### listen(port)
- `port` (number) - the port your server will listen on

Must be called after `create_server]`.
```
...
io.create_server()
io.listen(3000)     # on port 3000
```

### watch_callback(response)
- `response` (obd.OBDResponse) - the obd value that triggered the callback

Out of the box, when commands are watched they are all given the same callback `watch_callback` which does not implement anything. It is left for you to define so that data can be handled in your program uniquely. For example, for each response the value could be cached into a dictionary then that entire object streamed over the socket at a lesser rate than `watch_callback` may be fired.

```
data = {}
def cache_values(response):
    data[resopnse.command] = response.value

io.watch_callback = cache_values
```

### create_event(name, handler)
- `name` (string) - the name of a custom or overriden event
- `handler(sid, data)` (function) - the custom event handler

You are able to create custom events, or override the defaults with custom behaivour.
```
...
sio = io.create_server()   # call create server first to access the socket

def custom_handler(sid, data):
    sio.emit('custom', data)

io.create_event('custom_event', handler)

# define more events here then finally call
io.listen(port)
```
To override default events you can use the above method or use the [@sio.event](https://python-socketio.readthedocs.io/en/latest/server.html#defining-event-handlers) decorator
```
...

@sio.event
def watch(sid, cmd):
    pass     #override default watch behaviour

...

io.listen(48484)
```


### Default Server Events
On creation of an OBDio server most of the python-OBD API is exposed through events of the same name as its functions. The server will handle the event then respond with data (if any) using the same event name.

| **Event Name**     | **Argument Type**          | **Response Type** |
|--------------------|----------------------------|-------------------|
| status             | None                       | string            |
| is_connected       | None                       | boolean           |
| protocol_name      | None                       | string            |
| protocol_id        | None                       | string            |
| port_name          | None                       | string            |
| supports           | string<sup>1               | boolean           |
| supported_commands | None                       | object            |
| query<sup>2        | string<sup>1               | null              |
| start              | None                       | null              |
| watch              | (string or string[])<sup>1 | null              |
| unwatch            | (string or string[])<sup>1 | null              |
| unwatch_all        | None                       | null              |
| has_name           | string<sup>1               | boolean           |
| close              | None                       | null              |

1. Arg is a string (or list of) OBD command by name i.e. 'RPM', 'SPEED'. See the OBD [Command Tables](https://python-obd.readthedocs.io/en/latest/Command%20Tables/).

2. To query a command, it must be 'watched' first

See the python-OBD [documentation](https://python-obd.readthedocs.io/en/latest/) for expected behaviour of the default events.


