# -*- codeing: utf-8 -*-
import logging
import json
import six
from webob import Response
from ryu.app.wsgi import ControllerBase
from ryu.app.wsgi import WSGIApplication

LOG = logging.getLogger('DLController')


# REST command template
def rest_command(func):
    def _rest_command(*args, **kwargs):
        try:
            msg = func(*args, **kwargs)
            return Response(content_type='application/json',
                            body=json.dumps(msg))

        except SyntaxError as e:
            details = e.msg
        except (ValueError, NameError) as e:
            details = e.message
        except IndexError as e:
            details = e.args[0]

        msg = {'result': 'failure',
               'details': details}
        return Response(body=json.dumps(msg))

    return _rest_command


class DLController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(DLController, self).__init__(req, link, data, **config)
        self.ryu_app = data

    @rest_command
    def list_all_apps(self, req, **_kwargs):
        return self.ryu_app.list_all_apps()

    @rest_command
    def list_installed_app(self, req, **_kwargs):
        return self.ryu_app.list_installed_apps()

    @rest_command
    def report_brick(self, req, **_kwargs):
        return self.ryu_app.report_brick()

    @rest_command
    def install_app(self, req, **_kwargs):
        if six.PY2:
            body = json.loads(req.body)

        else:
            body = json.loads(req.body.decode('utf8'))

        path = body['path']

        self.ryu_app.install_app(path)
        return {'result': 'ok'}

    @rest_command
    def uninstall_app(self, req, **_kwargs):
        if six.PY2:
            body = json.loads(req.body)

        else:
            body = json.loads(req.body.decode('utf8'))
        path = body['path']

        self.ryu_app.uninstall_app(path)
        return {'result': 'ok'}

    @rest_command
    def list_switches(self, req, **_kwargs):
        return self.ryu_app.list_switches()

    @rest_command
    def list_links(self, req, **_kwargs):
        return self.ryu_app.list_links()

    @rest_command
    def list_hosts(self, req, **_kwargs):
        return self.ryu_app.list_hosts()

    @rest_command
    def custom_cmd(self, req, **_kwargs):
        if six.PY2:
            body = json.loads(req.body)

        else:
            body = json.loads(req.body.decode('utf8'))

        cmd_name = body['cmd_name']
        cmd_args = body['cmd_args']
        return self.ryu_app.custom_cmd(cmd_name, cmd_args)
