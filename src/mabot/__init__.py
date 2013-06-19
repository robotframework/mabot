#!/usr/local/bin python

#  Copyright 2008 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


"""Mabot -- Robot Framework's Manual Test Execution Tool

Version: <VERSION>

Usage:  mabot.py [options] datasource/output

Inputs to Mabot are Robot's test suite (HTML, TSV or directory) or output (XML)
of Mabot or Robot. Mabot can be used to mark test cases' and keywords' status
and messages and to generate Robot Framework's XML output file which can be
further processed with Rebot or other tools allowing one combined result from
multiple test executions.

Options:

 -i --include tag *       Select test cases by tag. Tag is case and space
                          insensitive and it can also be a simple pattern. To
                          include only tests which have more than one tag use
                          '&' or 'AND' between tag names.
                          For example '--include tag1&tag2' includes only those
                          tests that have both 'tag1' and 'tag2'.
                          When this option is given, it overrides the include
                          setting. New value is also automatically saved.
 -e --exclude tag *       Unselect test cases by tag. These tests are not
                          selected even if they are included with --include.
                          Tag names are handled similarly as in --include and
                          excluding only tests containing multiple tags works
                          works the same way using '&' or 'AND'.
                          When this option is given, it overrides the exclude
                          setting. New value is also automatically saved.
 -h -? --help             Print usage instructions.
 --version                Print version information.

Examples:

# Start mabot from datasource
$ mabot.py tests.html

# Or load results from already modified xml
$ mabot.py output.xml
"""

import sys
import os

# Insert bundled robot to path before anything else
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from mabot import settings
from mabot.utils.robotapi import Information, DataError, ArgumentParser, ROBOT_VERSION
from mabot import model
from mabot import ui
from mabot.ui.main import Mabot
from mabot.version import version



def run(args):
    aparser = ArgumentParser(__doc__, version=version, arg_limits=(0,1))
    try:
        opts, args = _get_opts_and_args(aparser, args)
    except Information, msg:
        _exit(str(msg))
    except DataError, err:
        _exit(str(err), 1)
    Mabot(args and args[0] or None, opts)

def _get_opts_and_args(aparser, args):
    if ROBOT_VERSION < '2.7':
        return aparser.parse_args(args, help='help', version='version',
                                  check_args=True)
    return aparser.parse_args(args)

def _exit(message, rc=0):
    print message
    if rc != 0:
        print '\nTry --help for usage information.'
    sys.exit(rc)

if __name__ == '__main__':
    run(sys.argv[1:])
