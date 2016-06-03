#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import ryu.contrib
ryu.contrib.update_module_path()

from ryu import cfg
import logging
import sys

from ryu import log
log.early_init_log(logging.DEBUG)

from ryu import flags
from ryu import version
from ryu.app import wsgi
from ryu.base.app_manager import AppManager
from ryu.controller import controller
from ryu.topology import switches

LOG = logging.getLogger('dragon_knight')
CONF = cfg.CONF
CONF.register_cli_opts([
    cfg.ListOpt('app-lists', default=[],
                help='application module name to run'),
    cfg.MultiStrOpt('app', positional=True, default=[],
                    help='application module name to run'),
    cfg.StrOpt('pid-file', default=None, help='pid file name'),
    cfg.BoolOpt('enable-debugger', default=False,
                help='don\'t overwrite Python standard threading library'
                '(use only for debugging)'),
    # ryu.topology.switches hack
    cfg.BoolOpt('observe-links', default=True,
                help='observe link discovery events.'),
])


def main(args=None, prog=None):
    try:
        CONF(args=args, prog=prog,
             project='ryu', version='ryu-manager {}'.format(version),
             default_config_files=['/usr/local/etc/ryu/ryu.conf'])
    except cfg.ConfigFilesNotFoundError:
        CONF(args=args, prog=prog,
             project='ryu', version='ryu-manager {}'.format(version))

    log.init_log()
    hub.patch(thread=True)

    if CONF.pid_file:
        LOG.info('Pid file : %s', CONF.pid_file)
        import os
        with open(CONF.pid_file, 'w') as pid_file:
            pid_file.write(str(os.getpid()))

    app_lists = CONF.app_lists + CONF.app

    if not app_lists:
        app_lists = ['ryu.controller.ofp_handler', 'dragon_knight.dk_plugin']

    if 'ryu.controller.ofp_handler' not in app_list:
        app_list.append('ryu.controller.ofp_handler')

    if 'dragon_knight.dk_plugin' not in app_list:
        app_list.append('dragon_knight.dk_plugin')

    app_mgr = AppManager.get_instance()
    app_mgr.load_apps(app_lists)
    contexts = app_mgr.create_contexts()
    services = []
    services.extend(app_mgr.instantiate_apps(**contexts))

    webapp = wsgi.start_service(app_mgr)

    if webapp:
        thr = hub.spawn(webapp)
        services.append(thr)

    try:
        hub.joinall(services)

    finally:
        app_mgr.close()

if __name__ == "__main__":
    main()
