#! /usr/bin/env python
# -*- codeing: utf-8 -*-
from __future__ import print_function

import cmd
import six
import json

if six.PY2:
    import urllib2 as urllib

else:
    import urllib3 as urllib

CLI_BASE_URL = 'http://127.0.0.1:5566'
CLI_LIST_PATH = '/list'
CLI_INSTALL_PATH = '/install'
CLI_UNINSTALL_PATH = '/uninstall'


def http_get(url):
    '''
    do http GET method
    return python dictionary data

    param:
        url: url for http GET, string type
    '''
    result = None

    if six.PY2:
        try:
            response = urllib.urlopen(url)
        except urllib.URLError as e:
            return e.reason
        result = json.load(response)

    else:
        http = urllib.PoolManager()
        response = http.request('GET', url)
        result = json.loads(response.data.decode('utf8'))

    return result


def http_post(url, req_body):
    '''
    do http POST method
    return python dictionary data

    param:
        url: url for http GET, string type
        req_body: data to send, string type
    '''
    result = None

    if six.PY2:
        try:
            response = urllib.urlopen(url, data=req_body)
        except urllib.URLError as e:
            return e.reason
        result = json.load(response)

    else:
        http = urllib.PoolManager()
        response = http.urlopen('POST', url, body=req_body)
        result = json.load(response)

    return result


class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class DlCli(cmd.Cmd):
    """
    Ryu dynamic loader command line
    """

    _msg = 'Welcome to the Ryu CLI. Type help or ? to list commands.\n'

    _anscii_art = """
        ____
       / __ \__  ____  __
      / /_/ / / / / / / /
     / _, _/ /_/ / /_/ /
    /_/ |_|\__, /\__,_/
          /____/
    """

    _hint_msg = """
    \n\nHit '{0}<Tab>{1}' key to auto-complete the commands \
    \nand '{0}<ctrl-d>{1}' or type '{0}exit{1}' to exit Ryu CLI.\n
    """.format(Bcolors.BOLD, Bcolors.ENDC)

    intro = (_msg + Bcolors.OKGREEN + _anscii_art + Bcolors.ENDC +
             _hint_msg + Bcolors.ENDC)

    prompt = Bcolors.WARNING + 'ryu-cli> ' + Bcolors.ENDC

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.app_list = None

    def do_list(self, line):
        '''
        List all available applications.
        '''

        self.app_list = http_get(CLI_BASE_URL + CLI_LIST_PATH)

        if not type(self.app_list) == list:
            print(self.app_list)
            return False

        app_id = 0

        for app_info in self.app_list:
            print('[%02d] %s' % (app_id, app_info['name']), end='')

            if app_info['installed']:
                print(' [' + Bcolors.OKGREEN + 'installed' +
                      Bcolors.ENDC + ']')
            else:
                print('')

            app_id += 1

    def do_install(self, line):
        '''
        Install ryu application by using module path
        Usage:
            install [app path]
        Example:
            install ryu.app.simple_switch
        '''
        req_body = json.dumps({'path': line})
        result = http_post(CLI_BASE_URL + CLI_INSTALL_PATH, req_body)

        if not type(result) == dict:
            print(result)
            return

        if result['result'] == 'ok':
            print('Successfully installed!')

        else:
            print(result['details'])

    def complete_install(self, text, line, begidx, endidx):

        self.app_list = http_get(CLI_BASE_URL + CLI_LIST_PATH)

        if not text:
            completions = [app_info['name'] for app_info in self.app_list]

        else:
            completions = [app_info['name']
                           for app_info in self.app_list
                           if app_info['name'].startswith(text)
                           ]

        return completions

    def do_uninstall(self, line):
        '''
        Uninstall ryu application
        Usage:
            uninstall [application module path]
        Example:
            uninstall ryu.app.simple_switch
        '''
        req_body = json.dumps({'path': line})
        result = http_post(CLI_BASE_URL + CLI_UNINSTALL_PATH, req_body)

        if not type(result) == dict:
            print(result)
            return

        if result['result'] == 'ok':
            print('Successfully uninstalled!')

        else:
            print(result['details'])

    def complete_uninstall(self, text, line, begidx, endidx):

        self.app_list = http_get(CLI_BASE_URL + CLI_LIST_PATH)

        if not text:
            completions = [app_info['name']
                           for app_info in self.app_list
                           if app_info['installed']
                           ]

        else:
            completions = [app_info['name']
                           for app_info in self.app_list
                           if app_info['name'].startswith(text) and
                           app_info['installed']
                           ]

        return completions

    def default(self, line):
        fail_msg = Bcolors.FAIL + 'Command not found: ' + line + Bcolors.ENDC
        print (fail_msg)

    def do_exit(self, line):
        '''
        Exit from command line
        '''
        return True

    def do_EOF(self, line):
        '''
        Use ctrl + D to exit
        '''
        return True


def main(args=None):
    '''
    Usage:
        ./cli [Base url]

        Base url: RESTful API server base url, default is http://127.0.0.1:5566
    '''
    import sys
    if len(sys.argv) >= 2:
        CLI_BASE_URL = sys.argv[1]

    try:
        DlCli().cmdloop()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
