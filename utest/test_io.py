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


import copy
import os
import unittest
from os.path import abspath, dirname, join, normcase

from robot.utils.asserts import *

from mabot.model import io
from mabot.model.model import DATA_MODIFIED

class AskMethodMock:
    
    def __init__(self):
        self.response = None
        
    def ask(self):
        if self.response is None:
            raise AssertionError("No response set. Should not ask response?")
        return self.response
    
DATA_FOLDER = normcase(join(dirname(__file__), 'data',))
SUITES_FOLDER = join(DATA_FOLDER, 'suites')
SUITES_FOLDER_WITH_OS_SEP = SUITES_FOLDER + os.sep
HTML_DATASOURCE_ONLY = join(SUITES_FOLDER, 'testcases.html')
TSV_DATASOURCE_ONLY = join(SUITES_FOLDER, 'tsv_testcases.tsv')
XML_DATASOURCE_ONLY = join(SUITES_FOLDER, 'output.xml')
HTML_DATASOURCE_WITH_XML = join(SUITES_FOLDER, 'testcases2.html')
TEXT_DATASOURCE = join(SUITES_FOLDER, 'text.txt')
NON_EXISTING_DATASOURCE = join(DATA_FOLDER, 'foo.html')
DUPLICATE_USERKEYWORDS = join(DATA_FOLDER, 'duplicate_keywords.html')
INVALID_HTML = join(DATA_FOLDER, 'invalid.html')
INVALID_XML = join(DATA_FOLDER, 'invalid.xml')
VALID_HTML_INVALID_XML_DATASOURCE = join(DATA_FOLDER, 'valid_html_invalid_xml.html')
VALID_HTML_INVALID_XML_XML = join(DATA_FOLDER, 'valid_html_invalid_xml.xml')
HTML_DATASOURCE_WITH_UPDATES = join(DATA_FOLDER, 'html_with_updates.html')
SAME_TEST_NAME = join(DATA_FOLDER, 'same_test_name.html')

class _TestIO(unittest.TestCase):

    def setUp(self):
        self.orig_settings = copy.deepcopy(io.SETTINGS)
        self.ask_method_mock = AskMethodMock()
        self.io = io.IO(self.ask_method_mock.ask)

    def tearDown(self):
        DATA_MODIFIED.saved()
        io.SETTINGS = self.orig_settings
        
    def _test_loading(self, source, name):
        suite = self.io.load_data(source)
        self.assertEqual(suite.name, name)
        return suite

    def _test_error(self, path, message, method=None):
        if not method:
            method = self.io.load_data
        message = "Could not load data!\n%s" % (message)
        assert_raises_with_msg(IOError, message, method, path)


class TestLoadData(_TestIO):
    
    def test_load_data_without_datasources(self):
        suite = self._test_loading(None, '')

    def test_load_data_with_only_html_datasource(self):
        suite = self._test_loading(HTML_DATASOURCE_ONLY, 'Testcases')

    def test_load_data_with_only_html_datasource_and_xml_loading_on(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        suite = self._test_loading(HTML_DATASOURCE_ONLY, 'Testcases')
        
    def test_load_data_with_only_tsv_datasource(self):
        suite = self._test_loading(TSV_DATASOURCE_ONLY, 'Tsv Testcases')

    def test_load_data_with_only_xml_datasource(self):
        suite = self._test_loading(XML_DATASOURCE_ONLY, 'Xml Testcases')

    def test_load_data_with_html_and_xml_datasources_xml_loading_off(self):
        suite = self._test_loading(HTML_DATASOURCE_WITH_XML, 'Testcases 2')
        self.assertEqual(suite.tests[0].status, 'FAIL')

    def test_load_data_with_html_and_xml_datasources_xml_loading_on(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        suite = self._test_loading(HTML_DATASOURCE_WITH_XML, 'Testcases 2')
        self.assertEqual(suite.tests[0].status, 'PASS')

    def test_load_data_with_directory_and_xml_datasources_with_xml_loading_on(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        suite = self._test_loading(SUITES_FOLDER, 'Suites')
        self.assertEqual(suite.suites[0].tests[0].status, 'PASS')


    def test_load_datasource_and_xml_with_updates_in_html(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        suite = self._test_loading(HTML_DATASOURCE_WITH_UPDATES, 
                                   'Html With Updates')        
        self.assertEquals(len(suite.tests), 2)
        self.assertEquals(suite.tests[0].message, 'Failure!')
        self.assertTrue(DATA_MODIFIED.is_modified(),
                        "Status should be True as there is modifications.")

    def test_load_datasource_and_xml_with_no_updates_in_html(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        suite = self._test_loading(HTML_DATASOURCE_WITH_XML, 'Testcases 2')
        self.assertFalse(DATA_MODIFIED.is_modified(),
                        "Status should be False as there is no modifications.")

    def test_load_datasource_and_xml_with_same_test_case_names(self):
        msg = "Found test 'TC' from suite 'Same Test Name' 2 times.\n"
        msg += "Mabot supports only unique test case names!\n"
        self._test_error(SAME_TEST_NAME, msg)
    

    def test_load_data_with_html_suite_with_dublicate_keywords(self):
        msg = "Could not create keyword 'UK' in testcase 'Duplicate Keywords.TC1'."
        msg += "\nKeyword 'UK' defined multiple times\n"
        self._test_error(DUPLICATE_USERKEYWORDS, msg)

    def test_load_data_with_non_existing_datasource(self):
        msg = "Path '%s' does not exist!" % (NON_EXISTING_DATASOURCE)
        self._test_error(NON_EXISTING_DATASOURCE, msg)

    def test_load_data_with_non_existing_datasource_with_xml_loading_on(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True        
        msg = "Path '%s' does not exist!" % (NON_EXISTING_DATASOURCE)
        self._test_error(NON_EXISTING_DATASOURCE, msg)

    def test_load_data_with_invalid_datasource_and_valid_xml(self):
        io.SETTINGS["include"] = ['no-tag']
        io.SETTINGS["always_load_old_data_from_xml"] = True        
        msg = "Suite 'Testcases 2' with includes 'no-tag' contains no test cases.\n"
        self._test_error(HTML_DATASOURCE_WITH_XML, msg)

    def test_load_data_with_valid_datasource_and_invalid_xml(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True      
        msg = "File '%s' is not a valid XML file.\n" % (VALID_HTML_INVALID_XML_XML)
        self._test_error(VALID_HTML_INVALID_XML_DATASOURCE, msg)

    def test_load_data_with_xml_error_and_datasource_error(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True      
        msg = "Test case file '%s' contains no test cases. and\n" % (INVALID_HTML)
        msg += "File '%s' is not a valid XML file.\n" % (INVALID_XML)
        self._test_error(INVALID_HTML, msg)


class TestGetDatasourceAndXml(_TestIO):

    def test_get_datasource_and_xml_from_xml(self):
        self.assertEqual(self.io._get_datasource_and_xml_from(XML_DATASOURCE_ONLY), 
                         (None, XML_DATASOURCE_ONLY))

    def test_get_datasource_and_xml_from_html_loading_off(self):
        io.SETTINGS["always_load_old_data_from_xml"] = False
        self.assertEqual(self.io._get_datasource_and_xml_from(HTML_DATASOURCE_WITH_XML), 
                         (HTML_DATASOURCE_WITH_XML, None))

    def test_get_datasource_and_xml_from_html(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        self.assertEqual(self.io._get_datasource_and_xml_from(HTML_DATASOURCE_WITH_XML), 
                         (HTML_DATASOURCE_WITH_XML, 
                          HTML_DATASOURCE_WITH_XML.replace('.html', '.xml')))

    def test_get_datasource_and_xml_from_dir_without_os_sep(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        self.assertEqual(self.io._get_datasource_and_xml_from(SUITES_FOLDER), 
                         (SUITES_FOLDER, SUITES_FOLDER+'.xml'))

    def test_get_datasource_and_xml_from_dir_ending_with_os_sep(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        folder = SUITES_FOLDER.endswith(os.sep) and SUITES_FOLDER
        self.assertEqual(self.io._get_datasource_and_xml_from(SUITES_FOLDER_WITH_OS_SEP), 
                         (SUITES_FOLDER, SUITES_FOLDER+'.xml'))

    def test_get_datasource_and_xml_from_tsv(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        self.assertEqual(self.io._get_datasource_and_xml_from(TSV_DATASOURCE_ONLY), 
                         (TSV_DATASOURCE_ONLY, TSV_DATASOURCE_ONLY.replace('.tsv', '.xml')))

    def test_get_datasource_and_xml_from_txt(self):
        msg = "Path '%s' is not in supported format!\nSupported formats" % (TEXT_DATASOURCE)
        msg += " are HTML, TSV, XML and Robot Framework's test suite directory."
        self._test_error(TEXT_DATASOURCE, msg, 
                         self.io._get_datasource_and_xml_from)

    def test_get_datasource_and_xml_from_non_existing_file(self):
        msg = "Path '%s' does not exist!" % (NON_EXISTING_DATASOURCE)
        self._test_error(NON_EXISTING_DATASOURCE, msg, 
                         self.io._get_datasource_and_xml_from)
            
    
if __name__ == "__main__":
    unittest.main()