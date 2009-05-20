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

import os
import sys
import unittest

from mabot.settings.utils import SettingsIO, MissingSettings, InvalidSettings


class TestSettingsIO(unittest.TestCase):
    
    def setUp(self):
        self.settings_file = os.path.join(os.path.dirname(__file__), 'data', 
                                          'testsettings.py')
        self.settings = SettingsIO(self.settings_file)

    def tearDown(self):
        sys.path.pop(0)
        self.settings.remove_settings()

    # Note: This tests needs to be first (aaa) before setting module is imported. 
    def test_aaa_no_settings_exists(self):
        self.assertRaises(MissingSettings, self.settings.read_settings)

    def test_settings_does_not_exist_anymore(self):
        self._test_settings_io({'string':'value'})
        self.settings.remove_settings()
        self.assertRaises(MissingSettings, self.settings.read_settings)

    def test_invalid_settings_exists(self):
        f = open(self.settings_file, 'w')
        f.write('foo = invalid syntax::')
        f.close()
        self.assertRaises(InvalidSettings, self.settings.read_settings)

    def test_setting_name_with_spaces(self):
        self.assertRaises(InvalidSettings, self._test_settings_io, 
                          {'setting name spaces': 'value'})

    def test_writing_string_setting(self):
        self._test_settings_io({'string':'value'})

    def test_writing_unicode_setting(self):
        self._test_settings_io({'unicode_string':u'non-ascii character \xe4'})

    def test_writing_list_setting(self):
        self._test_settings_io({'unicode_string': [1, 'string', 
                                                u'non-ascii character \xe4']})

    def test_writing_dictionary_setting(self):
        self._test_settings_io({'dictionary': {'a': 1, 'b': 2, 'c': 3}})

    def test_writing_none_setting(self):
        self._test_settings_io({'none': None})

    def test_writing_boolean_setting(self):
        self._test_settings_io({'boolean': True})

    def test_writing_multiline_string_setting(self):
        multiline = u"""Multi line string
with non-ascii chars \xe4
and quotes "foo" 'bar'
and even triple quotes \"\"\" '''
"""
        self._test_settings_io({'multiline': multiline})

    def test_multiple_settings(self):
        multiline = u"""Multi line string
with non-ascii chars \xe4
and quotes "foo" 'bar'
and even triple quotes \"\"\" '''
"""        
        self._test_settings_io({'multiline': multiline, 'string': u'some', 
                                'bool': False, 'int':1, 'float':2.4})
        
    def test_updating_setting(self):
        self._test_settings_io({'string': u'some', 'bool': False, 'int':1})
        self.settings.write_settings({'string': u'new', 'bool': True, 'int':1})
        self._test_settings_io({'string': u'new', 'bool': False, 'int':4})

    def _test_settings_io(self, expected):
        self.settings.write_settings(expected)
        actual = self.settings.read_settings()
        for key in expected.keys():
            self.assertEqual(expected[key], actual[key])

if __name__ == "__main__":
    unittest.main()