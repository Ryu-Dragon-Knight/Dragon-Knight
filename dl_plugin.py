# -*- codeing: utf-8 -*-
import logging
import pkgutil
import inspect

from ryu import app as ryu_app
from ryu.lib import hub
from ryu.app.wsgi import WSGIApplication
from ryu.base import app_manager
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.base.app_manager import RyuApp, AppManager

from dl_lib import DLController


LOG = logging.getLogger('DynamicLoader')

def deep_import(mod_name):
    mod = __import__(mod_name)
    components = mod_name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

class DynamicLoader(RyuApp):

    def __init__(self, *args, **kwargs):
        super(DynamicLoader, self).__init__(*args, **kwargs)
        self.ryu_mgr = AppManager.get_instance()
        self.available_app = []
        self.init_apps()
        wsgi = self.create_wsgi_app('0.0.0.0', 5566)
        mapper = wsgi.mapper
        wsgi.registory['DLController'] = self

        self.init_mapper(mapper)

    def create_wsgi_app(self, host, port):
        wsgi = WSGIApplication()
        webapp = hub.WSGIServer((host, port), wsgi)
        hub.spawn(webapp.serve_forever)
        return wsgi


    def init_apps(self):
        # init all available apps
        for _, name, is_pkg in pkgutil.walk_packages(ryu_app.__path__):
            LOG.debug(
                'Find %s : %s',
                'package' if is_pkg else 'module',
                name)

            if is_pkg:
                continue

            try:
                _app_module = deep_import('ryu.app.' + name)

                for _attr_name in dir(_app_module):
                    _attr = getattr(_app_module, _attr_name)

                    if inspect.isclass(_attr) and _attr.__bases__[0] == RyuApp:
                        LOG.debug('\tFind ryu app : %s.%s',
                            _attr.__module__,
                            _attr.__name__)
                        _full_name = '%s.%s' % (_attr.__module__, _attr.__name__)
                        self.available_app.append((_full_name, _attr))

            except ImportError:
                LOG.debug('Import Error')

    def init_mapper(self, mapper):
        mapper.connect('list', '/list', controller=DLController,
                       action='list_all_apps',
                       conditions=dict(method=['GET']))

        mapper.connect('list', '/install', controller=DLController,
                       action='install_app',
                       conditions=dict(method=['POST']))

        mapper.connect('list', '/uninstall', controller=DLController,
                       action='uninstall_app',
                       conditions=dict(method=['POST']))

    def create_context(self, key, cls):
        context = None

        if issubclass(cls, RyuApp):
            context = self.ryu_mgr._instantiate(None, cls)
        else:
            context = cls()

        LOG.info('creating context %s', key)

        if key in self.ryu_mgr.contexts:
            return None

        self.ryu_mgr.contexts.setdefault(key, context)
        return context


    def list_all_apps(self):
        res = []
        _installed_apps = self.ryu_mgr.applications

        for app_info in self.available_app:
            _cls = app_info[1]
            _installed_apps_cls =\
                [obj.__class__ for obj in _installed_apps.values()]

            if _cls in _installed_apps_cls:
                res.append({'name': app_info[0], 'installed': True})

            else:
                res.append({'name': app_info[0], 'installed': False})

        return res


    def install_app(self, app_id):
        try:
            app_cls = self.available_app[app_id][1]
            app_contexts = app_cls._CONTEXTS
            _installed_apps = self.ryu_mgr.applications
            _installed_apps_cls =\
                [obj.__class__ for obj in _installed_apps.values()]

            if app_cls in _installed_apps_cls:
                # app was installed
                LOG.debug('Application already installed')
                return
            new_contexts = []

            for k in app_contexts:
                context_cls = app_contexts[k]
                ctx = self.create_context(k, context_cls)

                if ctx and issubclass(context_cls, RyuApp):
                    new_contexts.append(ctx)

            app = self.ryu_mgr.instantiate(app_cls, **self.ryu_mgr.contexts)
            new_contexts.append(app)

            for ctx in new_contexts:
                t = ctx.start()
                # t should be join to some where?

        except IndexError:
            LOG.debug('Can\'t find application with id %d', app_id)
            ex = IndexError('Can\'t find application with id %d' % (app_id, ))
            raise ex

        except ValueError:
            LOG.debug('ryu-app-id must be number')

        except Exception, ex:
            LOG.debug('Import error for id: %d', ev.app_id)
            raise ex


    def uninstall_app(self, app_id):
        app_info = self.available_app[app_id]
        # TODO: such dirty, fix it!
        app_name = app_info[0].split('.')[-1]

        if app_name in self.ryu_mgr.applications:
            app = self.ryu_mgr.applications[app_name]
            self.ryu_mgr.uninstantiate(app_name)
            app.stop()
