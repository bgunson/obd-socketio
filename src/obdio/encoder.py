import json
import obd

class OBDEncoder(json.JSONEncoder):
    """
        A JSON encoder made for python-OBD types.

        Has not been tested on vehicle yet.
    """
    def default(self, o):

        if isinstance(o, obd.OBDStatus):
            return "OBDStatus Not implemented"

        if isinstance(o, obd.ECU):  # this may not be needed
            return str(o)   

        if isinstance(o, set):
            return list(o)

        if isinstance(o, obd.OBDResponse):
            if o.is_null():
                return None
            else:
                return {
                    'value': o.value,       # pint values may break this
                    'command': o.command,
                    'message': o.messages,
                    'time': o.time,
                    'unit': o.unit
                }
                
        if isinstance(o, obd.OBDCommand):
            return {
                'name': o.name,
                'desc': o.desc,
                # 'fast': o.fast,
                # the rest of this is not human readable/may not provide much info to a client
                # 'command': str(o.command),    
                # 'bytes': str(o.bytes),
                # 'ecu': o.ecu,
            }

        try:
            # obd.OBDCommand sets caught here
            iterable = iter(o)
            return list(iterable)
        except TypeError:
            pass
       
        return f'Object of type {o.__class__.__name__} is not JSON serializable'

        # Opt not to raise TypeError for now
        # return json.JSONEncoder.default(self, o)
