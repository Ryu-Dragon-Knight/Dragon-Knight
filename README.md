Ryu dynamic loader
===================

What is this?
-------------
This plugin(app) allow ryu install application dynamically without closing ryu process

How does it work?
---------
I wrote a ryu application and control app manager directly, the code is very simple.
![enter image description here](https://raw.githubusercontent.com/TakeshiTseng/ryu-dynamic-loader/master/howitwork.png)

Tested environment
--------------
 1. ryu v3.22
 2. Python 2.7

How to use it?
--------------
Start ryu application with dl_plugin
> $ ryu-manager dl_plugin

And start cli.py, and you can use it!

> $ ryu-manager dl_plugin

What command I can use?
--------------
For now, this plugin only provide "list" and install command, and I will add "uninstall" later

TODO List
--------------
1. Add "uninstall command"
2. Change from python 2.7 to python 3.4
