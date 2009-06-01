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
import shutil
import time
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

from model import EmptySuite
from model import ManualSuite
from model import DATA_MODIFIED
from mabot.settings import SETTINGS
from mabot import utils
from mabot.utils import robotapi


class IO:
    
    def __init__(self):
        self.ask_method = None
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
        self.output = xml or os.path.abspath('output.xml')
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
                suite = ManualSuite(robotapi.XmlTestSuite(xml), None, True)
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

    def save_data(self, output, ask_method):
        if output:
            self.output = output
        lock = utils.LockFile(self.output)
        lock.create_lock(ask_method)
        try:
            self._make_backup()
            changes = self._reload_data_from_xml(ask_method)
            if DATA_MODIFIED.is_modified() or output:
                self._save_data()
                return True, changes
            return False, changes
        finally:
            lock.release_lock()

    def _reload_data_from_xml(self, ask_method):
        if SETTINGS["always_load_old_data_from_xml"] and \
            SETTINGS["check_simultaneous_save"] and \
            os.path.exists(self.output) and \
            self.xml_generated != self._get_xml_generation_time():
            xml_suite = ManualSuite(robotapi.XmlTestSuite(self.output), None, True)                
            if xml_suite:
                self.suite.add_results(xml_suite, True, ask_method)
                return True
        return False

    def _save_data(self):
        self.suite.save()
        self._make_backup()
        #TODO: Change how execution errors are given
        testoutput = robotapi.RobotTestOutput(self.suite)
        testoutput.serialize_output(self.output, self.suite)            
        self.suite.saved()
        DATA_MODIFIED.saved()
        self.xml_generated = self._get_xml_generation_time()
    
    def _make_backup(self):
        if os.path.exists(self.output) and \
        SETTINGS["always_load_old_data_from_xml"]:
            # Creates backup only if the XML is valid 
            # Makes sure, that valid backup is not overridden
            backup = '%s.bak' % self.output 
            try:
                # Validates XML
                self._get_xml_generation_time()
            except:
                if os.path.exists(backup):
                    time_backup = '%s_%s.bak' % (self.output, self._get_timestamp())
                    shutil.copyfile(backup, time_backup)
                    msg = '''
%s is not a valid XML file!
Timestamped backup file was generated automatically
to file %s.

Try to save again. If the problem exists, copy latest
valid backup over the invalid XML without closing Mabot.
Note that some results will most probably be lost.
''' % (self.output, time_backup)
                    raise IOError(msg)
            else:
                shutil.copyfile(self.output, self.output+'.bak')
    
    def _get_timestamp(self):
        return '%d%02d%02d%02d%02d%02d' % time.localtime()[:6]
    
    def _get_xml_generation_time(self, path=None):
        if path is None:
            path = self.output 
        try:
            return ET.ElementTree(file=path).getroot().get("generated")
        except:
            raise IOError('%s is not a valid XML file!' % self.output)

