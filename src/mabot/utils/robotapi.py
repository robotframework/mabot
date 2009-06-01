import sys

try:
    from robot.output import TestSuite as XmlTestSuite
    from robot.serializing.testoutput import RobotTestOutput as _RobotTestOutput
    from robot.common import UserErrorHandler
    from robot.running.model import RunnableTestSuite, RunnableTestCase
    from robot.output.readers import Message
    from robot.running import TestSuite as _TestSuite
    from robot.conf import RobotSettings
    from robot.utils import get_timestamp, normalize
    from robot.utils import get_elapsed_time as _get_elapsed_time 
    from robot.running.namespace import Namespace as _NameSpace
    from robot.utils import ArgumentParser as _ArgumentParser
    from robot import version
    ROBOT_VERSION = version.get_version()
    from robot.errors import DataError
    if ROBOT_VERSION >= '2.0.3':
        from robot.errors import Information
    else:
        class Information(Exception):
            """Used by argument parser with --help or --version"""
    if ROBOT_VERSION >= '2.1':
        from robot.output.logger import LOGGER
        LOGGER.disable_automatic_console_logger()
except ImportError, error:
    print """All needed Robot modules could not be imported. 
Check your Robot installation."""
    print "Error was: %s" % (error.message)
    sys.exit(1)



def Namespace(suite, parent):
    if ROBOT_VERSION >= '2.1':
        return _NameSpace(suite, parent)
    else:
        return _NameSpace(suite, parent, NoOperation())


def TestSuite(datasources, settings):
    if ROBOT_VERSION >= '2.1':
        return _TestSuite(datasources, settings)
    else:
        return _TestSuite(datasources, settings, NoOperation())


def RobotTestOutput(suite):
    return _RobotTestOutput(suite, NoOperation())

    
def get_elapsed_time(start_time, end_time=None, seps=('', ' ', ':', '.')):
    elapsed = _get_elapsed_time(start_time, end_time, seps)
    if ROBOT_VERSION >= '2.1':
        from robot.utils import elapsed_time_to_string
        elapsed = elapsed_time_to_string(elapsed) 
    return elapsed
        

class _ArgumentParserFor2_0_2AndOlderRobot(_ArgumentParser):

    def __init__(self, doc, version):
        self.doc = doc.replace("<VERSION>", version)
        self.version = version
        _ArgumentParser.__init__(self, doc)

    def parse_args(self, args, **kwargs):
        try:
            opts, args = RobotArgParser.parse_args(self, args)
        except Exception, err:
            raise DataError('[ERROR] %s' % str(err))
        if opts['help']:
            raise Information(self.doc)
        if opts['version']:
            raise Information('Mabot %s' % (self.version))
        if len(args) > 1:
            DataError("[ERROR] Only one datasource is allowed.")
        return opts, args


def ArgumentParser(doc, version, arg_limits):
    if ROBOT_VERSION >= '2.0.3':
        return _ArgumentParser(doc, version, arg_limits)
    else:
        return _ArgumentParserFor2_0_2AndOlderRobot(doc, version)


class NoOperation:
    
    def __getattr__(self, name):
        return self.noop
    
    def noop(self, *args, **kwargs):
        pass    