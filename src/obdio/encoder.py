import json
import obd
from obd.OBDResponse import Status, Monitor
from obd import Unit
from obd.protocols.protocol import Message, Frame

class OBDEncoder(json.JSONEncoder):
    """
        A JSON encoder made for python-OBD types.

        Has not been tested on vehicle yet.
    """
    def default(self, o):

        if isinstance(o, Frame):
            return {
                'rx_id': o.rx_id,
                'addr_mode': o.addr_mode,
                'data': o.data,
                'data_len': o.data_len,
                'priority': o.priority,
                'raw': o.raw,
                'seq_index': o.seq_index,
                'rx_id': o.rx_id,
                'tx_id': o.tx_id,
                'type': o.type
            }

        if isinstance(o, Message):
            return {
                'data': o.data,
                'ecu': o.ecu,
                'frames': o.frames
            }

        if isinstance(o, Status):
            return {
                'MIL': o.MIL,
                'DTC_COUNT': o.DTC_count,
                'ignition_type': o.ignition_type
            }

        if isinstance(o, Unit.Quantity):
            return o.magnitude

        if isinstance(o, obd.ECU):  # this may not be needed
            return str(o)  

        if isinstance(o, set):
            return list(o)

        if isinstance(o, obd.OBDResponse):
            if o.is_null():
                return None
            else:
                return {
                    'value': o.value,       
                    'command': o.command,
                    'time': o.time,
                    'unit': o.unit
                }

                
        if isinstance(o, obd.OBDCommand):
            return {
                'name': o.name,
                'desc': o.desc,
                # the rest of this is not human readable/may not provide much info to a client
                # 'fast': o.fast,
                # 'command': o.command,    
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
