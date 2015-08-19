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


def http_get(url):
    '''
    do http GET method
    return python dictionary data

    param:
        url: url for http GET, string type
    '''
    result = None

    if six.PY2:
        response = urllib.urlopen(url)
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
        response = urllib.urlopen(url, data=req_body)
        result = json.load(response)

    else:
        http = urllib.PoolManager()
        response = http.urlopen('POST', url, body=req_body)
        result = json.load(response)

    return result

class DlCli(cmd.Cmd):
    """
    Ryu dynamic loader command line
    """

    def do_list(self, line):
        '''
        List all available applications.
        '''

        app_list = http_get('http://127.0.0.1:8080/list')
        app_id = 0

        for app_info in app_list:
            print('[%02d]%s' % (app_id, app_info['name']), end='')

            if app_info['installed']:
                print('[\033[92minstalled\033[0m]')
            else:
                print('')

            app_id += 1


    def do_install(self, line):
        '''
        Install ryu application
        Usage:
            install [app_id]
        '''
        try:
            app_id = int(line)
            req_body = json.dumps({'app_id':app_id})
            result = http_post('http://127.0.0.1:8080/install', req_body)
            print(result)

        except ValueError:
            print('Application id must be integer')

    def do_uninstall(self, line):
        '''
        Uninstall ryu application
        Usage:
            uninstall [app_id]
        '''
        try:
            app_id = int(line)
            req_body = json.dumps({'app_id':app_id})
            result = http_post('http://127.0.0.1:8080/uninstall', req_body)
            print(result)

        except ValueError:
            print('Application id must be integer')

    def do_exit(self, line):
        '''
        Exit from command line
        '''
        return True

if __name__ == '__main__':
    DlCli().cmdloop()
