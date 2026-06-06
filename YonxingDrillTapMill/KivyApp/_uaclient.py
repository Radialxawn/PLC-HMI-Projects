from asyncua import ua
from asyncua.sync import Client, SyncNode

class UaClient(object):
    def __init__(self):
        self.client = None
        self._connected = False

    def _reset(self):
        self.client = None
        self._connected = False

    def connect(self, uri):
        self.disconnect()
        print("Connecting to %s" % (uri))
        self.client = Client(uri)
        self.client.connect()
        self._connected = True
        self.client.load_data_type_definitions()
        try:
            self.client.load_enums()
            self.client.load_type_definitions()
        except Exception:
            print("Loading custom stuff with spec <= 1.03 did not work")
        print("Connected")

    def disconnect(self):
        if self._connected:
            print("Disconnecting from server")
            self._connected = False
            try:
                self.client.disconnect()
            finally:
                self._reset()
                print("Disconnected")

    def is_connected(self):
        if not self._connected:
            print('No connection')
        return self._connected

    def id__node(self, _ids_):
        nodes = [self.client.get_node(id) for id in _ids_]
        return dict(zip(_ids_, nodes))
    
    def node__value(self, _nodes_):
        values = self.client.read_values(_nodes_)
        return dict(zip(_nodes_, values))