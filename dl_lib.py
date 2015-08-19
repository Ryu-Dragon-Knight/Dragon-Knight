# -*- codeing: utf-8 -*-
import logging
import json
import contextlib
import dl_event
from ryu.lib import hub
from ryu.base import app_manager


LOG = logging.getLogger('DynamicLoaderLib')
class DynamicLoaderLib(app_manager.RyuApp):

    _EVENTS = [dl_event.EventAppListRequst,
               dl_event.EventAppListReply,
               dl_event.EventAppInstall,
               dl_event.EventAppUninstall,
               ]

    def __init__(self, *args, **kwargs):
        super(DynamicLoaderLib, self).__init__(*args, **kwargs)
        self.server = hub.StreamServer(('0.0.0.0', 10807), self._connection_factory)

    def start(self):
        hub.spawn(self.server.serve_forever)

    def _connection_factory(self, socket, address):
        with contextlib.closing(CliAgent(socket, address, self)) as agent:
            agent.serv()
        

class CliAgent(object):

    def __init__(self, socket, address, dynamic_load_app):
        self.socket = socket
        self.address = address
        self.dynamic_load_app = dynamic_load_app
    def close(self):
        self.socket.close()

    def serv(self):

        while True:
            buf = self.socket.recv(128)
            try:
                msg = json.loads(buf.decode('ascii'))

                if msg['cmd'] == 'list':
                    req = dl_event.EventAppListRequst()
                    rep = self.dynamic_load_app.send_request(req)
                    reply_msg = json.dumps(rep.app_list)
                    self.socket.sendall(reply_msg)

                if msg['cmd'] == 'install':
                    ev = dl_event.EventAppInstall(msg['app_id'])
                    self.dynamic_load_app.send_event_to_observers(ev)

                if msg['cmd'] == 'uninstall':
                    ev = dl_event.EventAppUninstall(msg['app_id'])
                    self.dynamic_load_app.send_event_to_observers(ev)


            except ValueError:
                LOG.debug('Incorrect json format %s', buf)

            hub.sleep(0.1)



