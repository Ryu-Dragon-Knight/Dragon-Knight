#!/usr/bin/env python
# -*- codeing: utf-8 -*-
import socket
import logging
import json

LOG = logging.getLogger('DynamicLoadCmd')


def main():
    
    sc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sc.connect(('127.0.0.1', 10807))

    while True:
        line = raw_input('(ryu) ')

        if line == 'exit':
            break

        elif line == 'list':
            msg = json.dumps({'cmd': 'list'})
            sc.sendall(msg)
            buf = sc.recv(2048)
            print buf
            app_list = json.loads(buf)
            app_id = 0

            for app_info in app_list:
                print '[%02d]%s' % (app_id, app_info['name']),

                if app_info['installed']:
                    print '[\033[92minstalled\033[0m]'
                else:
                    print ''

                app_id += 1

        elif 'uninstall' in line:
            argv = line.split(' ')

            if len(argv) < 2:
                print 'install [app_id]'
                continue

            app_id = int(argv[1])
            msg = json.dumps({'cmd':'uninstall', 'app_id': app_id})
            sc.sendall(msg)

        elif 'install' in line:
            argv = line.split(' ')

            if len(argv) < 2:
                print 'install [app_id]'
                continue

            app_id = int(argv[1])
            msg = json.dumps({'cmd':'install', 'app_id': app_id})
            sc.sendall(msg)


if __name__ == '__main__':
    main()
