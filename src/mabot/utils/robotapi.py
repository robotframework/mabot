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
    from robot.common import UserErrorHandler
    from robot.running.model import RunnableTestSuite, RunnableTestCase            
    from robot.running import TestSuite
    from robot.conf import RobotSettings
    from robot.running.namespace import Namespace
    from robot.utils import ArgumentParser, get_timestamp, normalize,\
                            elapsed_time_to_string, eq, normalize_tags
    from robot.utils import get_elapsed_time
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


def XmlTestSuite(suite):
    if ROBOT_VERSION < '2.7':
        from robot.output import TestSuite
        return TestSuite(suite)
    from robot.result import ExecutionResult
    return ExecutionResult(suite).suite

def RobotTestOutput(suite):
    if ROBOT_VERSION < '2.6':
        from robot.serializing.testoutput import RobotTestOutput as _RobotTestOutput
        return _RobotTestOutput(suite, NoOperation())
    elif ROBOT_VERSION < '2.7':
        from robot.result.resultwriter import ResultFromXML
        return ResultFromXML(suite, NoOperation())
    return _ResultFromXML(suite)

class _ResultFromXML(object):
    
    def __init__(self, suite):
        self.suite = suite
    
    def serialize_output(self, path, _non_needed):        
        from robot.reporting.outputwriter import OutputWriter
        serializer = OutputWriter(path)
        self.suite.serialize(serializer)
        from robot.common import Statistics 
        statistics = Statistics(self.suite, ())
        statistics.serialize(serializer)
        serializer.close()


def get_elapsed_time_as_string(start_time, end_time):
    elapsed = get_elapsed_time(start_time, end_time)
    return elapsed_time_to_string(elapsed)


class NoOperation:

    def __getattr__(self, name):
        return self.noop

    def noop(self, *args, **kwargs):
        pass
