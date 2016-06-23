Dragon Knight
===================

About this project
-------------------
This plugin(application) allow ryu install application dynamically without closing ryu process

How does it work?
------------------
We wrote a ryu application and control app manager directly.
![How does it work][3]


Tested environment
--------------
 1. ryu v3.22 or newer version
 2. Python 2.7/3.4

How to use it?
--------------
Start dragon knight daemon
> $ dragon-knightd

And start dragon knight daemon, and you can use it!

> $ dragon-knight

What command I can use?
--------------
For now, this plugin provide :
 1. list: list all available ryu app from ryu.app module
 2. install: install a ryu application by id
 3. uninstall: uninstall a ryu application
 4. bricks: Show service bricks from app manager
 5. topology: Display topology

Features
--------------
1. [x] Support both python 2.7 and python 3.4
2. [x] Provide REST API
3. [x] Allow user install external ryu application
4. [x] Display applications that doesn't exist in ryu.app module
5. [x] Beautiful command line interface
6. [x] Ascii-style topology information
7. [x] Auto complete application module name/path
8. [x] Display bricks relationship
9. [x] Allow developer add custom command for their Ryu Application
10. [ ] [More features!][5]

TODO
--------------
1. [ ] Dump flows from datapath
2. [ ] Web UI

Screenshot
--------------
![screenshot][4]

Contributors
--------------
1. [TakeshiTseng][1]
2. [John-Lin][2]

[1]: https://github.com/TakeshiTseng
[2]: https://github.com/John-Lin
[3]: https://raw.githubusercontent.com/TakeshiTseng/ryu-dynamic-loader/master/howitwork.png
[4]: https://raw.githubusercontent.com/TakeshiTseng/ryu-dynamic-loader/master/screenshot.jpg
[5]: https://github.com/TakeshiTseng/Dragon-Knight/issues
