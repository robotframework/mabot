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


import os.path
try:
    import xml.etree.cElementTree as ET
except ImportError:
    try: 
        import cElementTree as ET
    except ImportError:
        try:
            import elementtree.ElementTree as ET
        except ImportError:
            raise ImportError('Could not import ElementTree module. '
                              'Upgrade to Python 2.5+ or install ElementTree '
                              'from http://effbot.org/zone/element-index.htm')

try:
    from robot.running import TestSuite
    from robot.output import TestSuite as XmlTestSuite
    from robot.conf import RobotSettings
    from robot.serializing.testoutput import RobotTestOutput
except ImportError, error:
    print """All needed Robot modules could not be imported. 
Check your Robot installation."""
    print "Error was: %s" % (error[0])

from model import EmptySuite
from model import ManualSuite
from model import DATA_MODIFIED
from mabot.settings import SETTINGS
from mabot import utils

class IO:
    
    def __init__(self, ask_method):
        self.ask_method = ask_method
        self.xml_generated = None
        self.output = None
        self.suite = EmptySuite()

    def load_data(self, path):
        if not path:
            # In case empty suite is loaded
            return self.suite
        datasource, xml = self._get_datasource_and_xml_from(path)
        xml_suite, xml_error = self._load_xml_file(xml)
        testdata_suite, data_error = self._load_datasource(datasource)
        self._set_suite(testdata_suite, data_error, xml_suite, xml_error)
        self.output = xml or 'output.xml'
        return self.suite
        
    def _set_suite(self, testdata_suite, data_error, xml_suite, xml_error):
        if testdata_suite and xml_suite:
            testdata_suite.add_results(xml_suite)
            self.suite = testdata_suite
        elif xml_suite and not data_error:
            self.suite = xml_suite
        elif testdata_suite and not xml_error:
            self.suite = testdata_suite
        else:
            self._generate_error(xml_error, data_error)

    def _generate_error(self, xml_error, data_error):
        if data_error is not None and xml_error is not None:
            error = "%s and\n%s" % (data_error[0], xml_error[0])
        elif data_error is not None:
            error = data_error[0]
        elif xml_error is not None:
            error = xml_error[0]      
        raise IOError("Could not load data!\n%s\n" % (error))

    def _load_xml_file(self, xml):
        if xml and os.path.exists(xml):
            try:
                suite = ManualSuite(XmlTestSuite(xml), None, True)
                self.xml_generated = self._get_xml_generation_time(xml)
                return suite, None
            except Exception, error:
                return None, error
        return None, None

    def _load_datasource(self, source):
        if source:
            try:
                suite = ManualSuite(utils.load_data(source, SETTINGS))
                return suite, None
            except Exception, error:        
                return None, error
        return None, None

    def _get_datasource_and_xml_from(self, path):
        path = os.path.normcase(os.path.abspath(path))
        root, extension = os.path.splitext(path)
        msg = "Could not load data!\n"
        if not os.path.exists(path):
            msg += "Path '%s' does not exist!" % (path)
            raise IOError(msg)
        if not self._is_supported_format(path, extension):
            msg += "Path '%s' is not in supported format!\n" % (path)
            msg += "Supported formats are HTML, " 
            msg += "TSV, XML and Robot Framework's test suite directory." 
            raise IOError(msg)
        if extension.lower() == '.xml':
            return None, path

        if not SETTINGS["always_load_old_data_from_xml"]:
            return path, None
        else:
            return path, '%s.xml' % (root)

    def _is_supported_format(self, path, extension):
        if os.path.isdir(path):
            return True
        return extension.lower() in [ '.html', '.xml', '.tsv' ]

    def save_data(self, output=None, changes=False):
        if output:
            self.output = output
        lock = utils.LockFile(self.output)
        lock.create_lock(self.ask_method)
        self._reload_data_from_xml()
        if DATA_MODIFIED.is_modified() or changes:
            changes = True
            self._save_data()
        lock.release_lock()
        return changes

    def _reload_data_from_xml(self):
        if SETTINGS["always_load_old_data_from_xml"] and \
            SETTINGS["check_simultaneous_save"] and \
            os.path.exists(self.output) and \
            self.xml_generated != self._get_xml_generation_time():
            xml_suite = self._read_xml()
            if xml_suite:
                self.suite.add_results(xml_suite, True, self.ask_method)

    def _save_data(self):
        self.suite.save()
        testoutput = RobotTestOutput(self.suite, utils.LOGGER)
        testoutput.serialize_output(self.output, self.suite)
        self.suite.saved()
        DATA_MODIFIED.saved()
        self.xml_generated = self._get_xml_generation_time()
    
    def _get_xml_generation_time(self, path=None):
        if path is None:
            path = self.output 
        return ET.ElementTree(file=path).getroot().get("generated")
    
    def _read_xml(self):
        while True:
            try:
                return ManualSuite(XmlTestSuite(self.output), None, True)                
            except Exception, error:
                message = """Loading file '%s' failed!
Error was: %s

Do you want to try to load the file again?
""" % (self.path, error[0])
                if not self.ask_method("Loading Failed!", message):
                    return None

        