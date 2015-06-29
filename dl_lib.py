import contextlib
import pdb
from ryu.lib.hub import StreamServer
from ryu.lib import hub
import json
from ryu.base import app_manager
from ryu.controller import event

class EventAppListRequst(event.EventRequestBase):

    def __init__(self):
        super(EventAppListRequst, self).__init__()
        self.dst = 'DynamicLoader'

class EventAppListReply(event.EventReplyBase):
    '''
    reply application application list
    ex:
    [
        {app name(string): (app class, installed(boolean))},
        ...
    ]
    '''
    def __init__(self, dst, app_list):
        super(EventAppListReply, self).__init__(dst)
        self.app_list = app_list

class EventAppInstall(event.EventBase):

    def __init__(self, app_id):
        super(EventAppInstall, self).__init__()
        self.app_id = app_id

class EventAppUninstall(event.EventBase):

    def __init__(self, app_id):
        super(EventAppUninstall, self).__init__()
        self.app_id = app_id


class DynamicLoaderLib(app_manager.RyuApp):

    def __init__(self, *args, **kwargs):
        super(DynamicLoaderLib, self).__init__(*args, **kwargs)
        self.name = 'dl_lib'
        self.server = StreamServer(('0.0.0.0', 10807), self._connection_factory)

    def start(self):
        hub.spawn(self.server.serve_forever)

    def _connection_factory(self, socket, address):


        try:
            while True:
                buf = socket.recv(128)
                try:
                    msg = json.loads(buf.decode('ascii'))

                    if msg['cmd'] == 'list':
                        req = EventAppListRequst()
                        rep = self.send_request(req)
                        reply_msg = json.dumps(rep.app_list)
                        socket.sendall(reply_msg)

                    if msg['cmd'] == 'install':
                        ev = EventAppInstall(msg['app_id'])
                        self.send_event_to_observers(ev)

                    if msg['cmd'] == 'uninstall':
                        ev = EventAppUninstall(msg['app_id'])
                        self.send_event_to_observers(ev)


                except Exception:
                    pass
                hub.sleep(0.1)
        finally:
            socket.close()
