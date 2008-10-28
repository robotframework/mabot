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

from mabot.model import io


class AskMethodMock:
    
    def __init__(self):
        self.response = None
        
    def ask(self):
        if self.response is None:
            raise AssertionError("No response set. Should not ask response?")
        return self.response
    
DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'data', 'suites')
HTML_DATASOURCE_ONLY = os.path.join(DATA_FOLDER, 'testcases.html')
TSV_DATASOURCE_ONLY = os.path.join(DATA_FOLDER, 'tsv_testcases.tsv')
XML_DATASOURCE_ONLY = os.path.join(DATA_FOLDER, 'output.xml')
HTML_DATASOURCE_WITH_XML = os.path.join(DATA_FOLDER, 'testcases2.html')

class TestIO(unittest.TestCase):
    
    def setUp(self):
        self.orig_settings = copy.deepcopy(io.SETTINGS)
        self.ask_method_mock = AskMethodMock()
        self.io = io.IO(self.ask_method_mock.ask)

    def tearDown(self):
        io.SETTINGS = self.orig_settings
        
    def test_load_data_without_datasources(self):
        suite = self._test_loading(None, '')

    def test_load_data_with_only_html_datasource(self):
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

    def test_load_data_with_directory_and_xml_datasources_xml_loading_on(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        suite = self._test_loading(DATA_FOLDER, 'Suites')
        self.assertEqual(suite.suites[0].tests[0].status, 'PASS')

    def test_get_xml_path_from_xml(self):
        self.assertEqual(self.io._get_xml_path_from('hello.xml'), 'hello.xml')

    def test_get_xml_path_from_html_loading_off(self):
        io.SETTINGS["always_load_old_data_from_xml"] = False
        self.assertEqual(self.io._get_xml_path_from('hello.html'), None)

    def test_get_xml_path_from_dir(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        self.assertEqual(self.io._get_xml_path_from(DATA_FOLDER), 
                         DATA_FOLDER+'.xml')

    def test_get_xml_path_from_html(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        self.assertEqual(self.io._get_xml_path_from('hello.html'), 'hello.xml')

    def test_get_xml_path_from_tsv(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        self.assertEqual(self.io._get_xml_path_from('hello.tsv'), 'hello.xml')

    def test_get_xml_path_from_txt(self):
        io.SETTINGS["always_load_old_data_from_xml"] = True
        self.assertEqual(self.io._get_xml_path_from('hello.txt'), None)
        
    def _test_loading(self, source, name):
        suite = self.io.load_data(source)
        self.assertEqual(suite.name, name)
        return suite
    
if __name__ == "__main__":
    unittest.main()