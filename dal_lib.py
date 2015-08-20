# -*- codeing: utf-8 -*-
import logging
import json
from webob import Response
from ryu.app.wsgi import ControllerBase
from ryu.app.wsgi import WSGIApplication

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

LOG = logging.getLogger('DLController')
class DLController(ControllerBase):

    def __init__(self, req, link, data, **config):
        super(DLController, self).__init__(req, link, data, **config)
        self.ryu_app = data

    @rest_command
    def list_all_apps(self, req, **_kwargs):
        return self.ryu_app.list_all_apps()


    @rest_command
    def install_app(self, req, **_kwargs):
        body = json.loads(req.body)
        app_id = int(body['app_id'])

        if app_id < 0:
            e = ValueError('app id must grater than 0')
            raise e

        self.ryu_app.install_app(app_id)
        return {'result': 'ok'}

    @rest_command
    def uninstall_app(self, req, **_kwargs):
        body = json.loads(req.body)
        app_id = int(body['app_id'])

        if app_id < 0:
            e = ValueError('app id must grater than 0')
            raise e

        self.ryu_app.uninstall_app(app_id)
        return {'result': 'ok'}
