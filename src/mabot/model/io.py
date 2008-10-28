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
from model import NoOperationLogger
from model import DATA_MODIFIED
from mabot.settings import SETTINGS
from mabot.utils.LockFile import LockFile

class IO:
    
    def __init__(self, ask_method):
        self.ask_method = ask_method
        self.xml_generated = None
        self.output = None
        self.suite = EmptySuite()

    def load_data(self, source):
        if not source:
            return self.suite
        xml = self._get_xml_path_from(source)
        xml_suite, xml_error = self._load_xml_file(xml)
        testdata_suite, data_error = self._load_datasource(source)
        if xml_suite is not None and testdata_suite is None:
            self.suite = xml_suite
        elif testdata_suite is not None:
            testdata_suite.add_results_from_other_suite(xml_suite)
            self.suite = testdata_suite
        else:
            self._generate_error(xml_error, data_error)
        self.output = xml is not None and xml or 'output.xml'
        #TODO: This is not the case if there are some new data loaded
        DATA_MODIFIED.saved()
        return self.suite

    def _generate_error(self, xml_error, data_error):
        if data_error is not None and xml_error is not None:
            error = 'Errors were: "%s" and\n"%s"'
            error = error % (data_error[0], xml_error[0])
        elif data_error is not None:
            error = "Error was: %s" % (data_error[0])
        elif xml_error is not None:
            error = "Error was: %s" % (xml_error[0])
        raise Exception("Could not load data! %s" % (error))

    def _load_xml_file(self, xml):
        if xml:
            try:
                suite = ManualSuite(XmlTestSuite(xml), None, True)
                self.xml_generated = self._get_xml_generation_time(xml)
                return suite, None
            except Exception, error:
                return None, error
        return None, None

    def _load_datasource(self, source):
        try:
            settings = RobotSettings()
            settings['Include'] = SETTINGS['include']
            settings['Exclude'] = SETTINGS['exclude']
            suite = ManualSuite(TestSuite([source], settings, 
                                          NoOperationLogger()))
            return suite, None
        except Exception, error:        
            return None, error

    def _get_xml_path_from(self, path):
        if path.endswith('.xml'):
            return path 
        if not SETTINGS["always_load_old_data_from_xml"]:
            return None
        if os.path.isdir(path):
            return '%s.xml' % (path)
        if path.endswith('.html'):
            return path.replace(".html", ".xml")
        if path.endswith('.tsv'):
            return path.replace(".tsv", ".xml")
        return None

    def save_data(self):
        changes = False
        return_path = None
        lock = LockFile(self.output)
        lock.create_lock(self.ask_method)
        if SETTINGS["always_load_old_data_from_xml"] and \
            SETTINGS["check_simultaneous_save"] and \
            os.path.exists(self.output) and \
            self.xml_generated != self._get_xml_generation_time():
            xml_suite = self._read_xml()
            if xml_suite is not None:
                changes = True
                self.suite.load_new_changes_from_xml(xml_suite, self.ask_method)
        if DATA_MODIFIED.is_modified():
            self.suite.save()
            testoutput = RobotTestOutput(self.suite, NoOperationLogger())
            testoutput.serialize_output(self.output, self.suite)
            self.xml_generated = self._get_xml_generation_time()
            DATA_MODIFIED.saved()
            return_path = self.output
            self.suite.saved()
        content = lock.release_lock()
        return return_path, changes
    
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

        