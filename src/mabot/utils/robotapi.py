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

import sys

try:
    from robot.output import TestSuite as XmlTestSuite
    from robot.serializing.testoutput import RobotTestOutput as _RobotTestOutput
    from robot.common import UserErrorHandler
    from robot.running.model import RunnableTestSuite, RunnableTestCase
    from robot.output.readers import Message
    from robot.running import TestSuite
    from robot.conf import RobotSettings
    from robot.running.namespace import Namespace
    from robot.running.context import ExecutionContext
    from robot.utils import ArgumentParser, get_timestamp, normalize,\
                            elapsed_time_to_string, eq, normalize_tags
    from robot.utils import get_elapsed_time as _get_elapsed_time
    from robot import version
    ROBOT_VERSION = version.get_version()
    from robot.errors import DataError
    from robot.errors import Information
    from robot.output.logger import LOGGER
    LOGGER.disable_automatic_console_logger()
except ImportError, error:
    print """All needed Robot modules could not be imported.
Check your Robot installation."""
    print "Error was: %s" % (error)
    sys.exit(1)


def RobotTestOutput(suite):
    return _RobotTestOutput(suite, NoOperation())


def get_elapsed_time(start_time, end_time=None, seps=('', ' ', ':', '.')):
    elapsed = _get_elapsed_time(start_time, end_time, seps)
    return elapsed_time_to_string(elapsed)


class NoOperation:

    def __getattr__(self, name):
        return self.noop

    def noop(self, *args, **kwargs):
        pass
