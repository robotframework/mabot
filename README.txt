Mabot
=====

Introduction
------------

Manual test result reporting tool for Robot Framework. It uses same file 
formats as Robot Framework. It has following features:

 - Manual test cases can be saved to same format as automated tests.
 - Easy and simple way for marking test execution results.
 - Tagging functionality makes it easy to collect statistics 
 - Same output format with Robot Framework allows combining manual and 
   automated tests' results to one report.

For more information, see http://code.google.com/p/robotframework-mabot/.


Installation
------------

Run `python setup.py install` or visit 
http://code.google.com/p/robotframework-mabot/ for distribution and 
installation instructions.

Usage
-----

Mabot is started with command `mabot.py` Additionally a path to test data or 
saved xml can be given with possible command line options before the path. 
Robot Frameworks `rebot` tool is used for post-processing outputs.

Examples::

  mabot.py
  mabot.py --include manual my_tests.html
  mabot.py results.xml

For more information, run `mabot.py --help` or see 
http://code.google.com/p/robotframework-mabot/


Directory Layout
----------------

atest/
    Acceptance tests. Naturally using Mabot.

src/
    Mabot source code.

utest/
    Unit tests.

