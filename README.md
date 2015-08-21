Ryu dynamic loader
===================

About this project
-------------------
This plugin(app) allow ryu install application dynamically without closing ryu process

How does it work?
------------------
I wrote a ryu application and control app manager directly, the code is very simple.
![How does it work](https://raw.githubusercontent.com/TakeshiTseng/ryu-dynamic-loader/master/howitwork.png)


Tested environment
--------------
 1. ryu v3.22 or newer version
 2. Python 2.7/3.4

How to use it?
--------------
Start ryu manager with dal_plugin
> $ ryu-manager dal_plugin

And start cli.py, and you can use it!

> $ ./ryu_cli.py

What command I can use?
--------------
For now, this plugin provide :
 1. list: list all available ryu app from ryu.app module
 2. install: install a ryu application by id
 3. uninstall: uninstall a ryu application

TODO
--------------
1. [x] Support both python 2.7 and python 3.4
2. [x] Use python cmd module to implement it!
3. [x] Change from socket to REST API
4. [x] Allow user install external ryu application
5. [x] Uninstall application by using module name
6. [x] Display applications that doesn't exist in ryu.app module
7. [x] Make command line interface pretty
8. [ ] Display more information from ryu application manager
9. [ ] Topology information
10. [ ] Dump flows from datapath
11. [x] Auto complete application module name/path

Screenshot
--------------
![screenshot](https://raw.githubusercontent.com/TakeshiTseng/ryu-dynamic-loader/master/screenshot.jpg)

Contributors
--------------
1. [TakeshiTseng][1]
2. [John-Lin][2]

[1]: https://github.com/TakeshiTseng
[2]: https://github.com/John-Lin
