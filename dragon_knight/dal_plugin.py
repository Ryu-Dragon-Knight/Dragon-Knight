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
from ryu.topology import api as topo_api

from dragon_knight.lib.dal_lib import DLController


_REQUIRED_APP = ['ryu.controller.ofp_handler', 'ryu.topology.switches']
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
                        _full_name = '%s' % (_attr.__module__,)
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

        mapper.connect('list', '/installed', controller=DLController,
                       action='list_installed_app',
                       conditions=dict(method=['GET']))

        mapper.connect('list', '/uninstall', controller=DLController,
                       action='uninstall_app',
                       conditions=dict(method=['POST']))

        mapper.connect('list', '/bricks', controller=DLController,
                       action='report_brick',
                       conditions=dict(method=['GET']))

        mapper.connect('list', '/switches', controller=DLController,
                       action='list_switches',
                       conditions=dict(method=['GET']))

        mapper.connect('list', '/links', controller=DLController,
                       action='list_links',
                       conditions=dict(method=['GET']))

        mapper.connect('list', '/hosts', controller=DLController,
                       action='list_hosts',
                       conditions=dict(method=['GET']))

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
        installed_apps = self.ryu_mgr.applications

        for app_info in self.available_app:
            _cls = app_info[1]
            installed_apps_cls =\
                [obj.__class__ for obj in installed_apps.values()]

            if _cls in installed_apps_cls:
                res.append({
                    'name': app_info[0],
                    'installed': True
                })

            else:
                res.append({
                    'name': app_info[0],
                    'installed': False
                })

        return res

    def _install_app(self, app_cls):
        app_contexts = app_cls._CONTEXTS
        installed_apps = self.ryu_mgr.applications
        installed_apps_cls =\
            [obj.__class__ for obj in installed_apps.values()]

        if app_cls in installed_apps_cls:
            # app was installed
            LOG.debug('Application already installed')
            ex = ValueError('Application already installed')
            raise ex

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

    def uninstall_app(self, path):
        app_cls = self.ryu_mgr.load_app(path)
        app = None

        for _app in self.ryu_mgr.applications.values():
            if isinstance(_app, app_cls):
                app = _app
                break

        else:
            raise ValueError('Can\'t find application')

        self.ryu_mgr.uninstantiate(app.name)
        app.stop()

        # after we stoped application, chack it context
        app_contexts = app_cls._CONTEXTS
        installed_apps = self.ryu_mgr.applications
        installed_apps_cls =\
            [obj.__class__ for obj in installed_apps.values()]

        for ctx_name in app_contexts:
            for app_cls in installed_apps_cls:
                if ctx_name in app_cls._CONTEXTS:
                    break

            else:
                # remove this context
                ctx_cls = app_contexts[ctx_name]
                ctx = self.ryu_mgr.contexts[ctx_name]
                if issubclass(ctx_cls, RyuApp):
                    ctx.stop()

                if ctx.name in self.ryu_mgr.applications:
                    del self.ryu_mgr.applications[ctx.name]

                if ctx_name in self.ryu_mgr.contexts:
                    del self.ryu_mgr.contexts[ctx_name]

                if ctx.name in app_manager.SERVICE_BRICKS:
                    del app_manager.SERVICE_BRICKS[ctx.name]

                ctx.logger.info('Uninstall app %s successfully', ctx.name)

                # handler hacking, remove all stream handler to avoid it log many times!
                ctx.logger.handlers = []

    def install_app(self, path):
        context_modules = [x.__module__ for x in self.ryu_mgr.contexts_cls.values()]

        if path in context_modules:
            ex = ValueError('Application already exist in contexts')
            raise ex

        LOG.info('loading app %s', path)
        app_cls = self.ryu_mgr.load_app(path)

        if app_cls is None:
            ex = ValueError('Can\'t find application module')
            raise ex

        self._install_app(app_cls)

    def list_installed_apps(self):
        res = []
        installed_apps = self.ryu_mgr.applications.values()
        res = [installed_app.__module__ for installed_app in installed_apps]
        return res

    def report_brick(self):
        res = {}

        for name, app in app_manager.SERVICE_BRICKS.items():
            res.setdefault(name, {'provide': [], 'consume': []})
            for ev_cls, list_ in app.observers.items():
                res[name]['provide'].append((ev_cls.__name__, [capp for capp in list_]))
            for ev_cls in app.event_handlers.keys():
                res[name]['consume'].append((ev_cls.__name__))

        return res

    def list_switches(self):
        switches = topo_api.get_all_switch(self)
        return [switch.to_dict() for switch in switches]

    def list_links(self):
        links = topo_api.get_all_link(self)
        return [link.to_dict() for link in links]

    def list_hosts(self):
        hosts = topo_api.get_all_host(self)
        return [host.to_dict() for host in hosts]
