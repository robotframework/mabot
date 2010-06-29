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

from mabot.settings.utils import SettingsIO, RFSettings, InvalidSettings


class TestSettingsIO(unittest.TestCase):
    
    def setUp(self):
        self.settings_file = os.path.join(os.path.dirname(__file__), 'data', 
                                          'testsettings.py')
        self.settings = SettingsIO(path=self.settings_file)

    def tearDown(self):
        self.settings.remove()

    def test_get_paths_without_file_name(self):
        actual = self.settings._get_paths('toolx', None)[1]
        expected_end = '%s%s%s' % ('toolx', os.sep, 'toolxsettings.py')
        self.assertTrue(actual.endswith(expected_end))

    def test_get_paths_with_file_name(self):
        actual = self.settings._get_paths('toolx', 'name')[1]
        self.assertTrue(actual.endswith('%s%s%s' % ('toolx', os.sep, 'name')))

    def test_no_settings_exists(self):
        self.assertEquals(self.settings.read(), {})
        
    def test_invalid_setting_name(self):
        self.assertRaises(InvalidSettings, self.settings.write, 
                          {'name with space':0})

    def test_settings_does_not_exist_anymore(self):
        self._test_settings_io({'string':'value'})
        self.settings.remove()
        self.assertEquals(self.settings.read(), {})

    def test_invalid_settings_exists(self):
        f = open(self.settings_file, 'w')
        f.write('foo = invalid syntax::')
        f.close()
        self.assertRaises(InvalidSettings, self.settings.read)

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
        self.settings.write({'string': u'new', 'bool': True, 'int':1})
        self._test_settings_io({'string': u'new', 'bool': False, 'int':4})

    def _test_settings_io(self, expected):
        self.settings.write(expected)
        actual = self.settings.read()
        self.assertEqual(expected, actual)


class Logger:
    
    def __init__(self):
        self.logs = []
    
    def log(self, message):
        self.logs.append(message)

class TestRFSettings(unittest.TestCase):
    
    def setUp(self):
        self.logger = Logger()
        self.settings_file = os.path.join(os.path.dirname(__file__), 'data', 
                                          'testsettings.py')

    def tearDown(self):
        self.settings.remove()

        
    def test_default_values_are_read_correctly_when_no_user_settings(self):
        defaults = {'foo':'bar'}
        self.settings = RFSettings(path=self.settings_file, 
                                   defaults=defaults)
        self.assertEquals(self.settings._settings, defaults)


    def test_default_values_are_read_correctly_when_invalid_settings(self):
        defaults = {'foo':'bar'}
        self._add_invalid_data_to_user_settings_file('invalid syntax =')
        self.settings = RFSettings(path=self.settings_file, 
                                   defaults=defaults, logger=self.logger.log)
        self.assertEquals(self.settings._settings, defaults)
        log_end = "testsettings.py' is not a valid Python file.\ninvalid syntax (testsettings.py, line 1)"
        self.assertTrue(self.logger.logs[0].startswith('Settings file'))
        self.assertTrue(self.logger.logs[0].endswith(log_end))

    def test_empty_logger_when_invalid_settings(self):
        defaults = {'foo':'bar'}
        self._add_invalid_data_to_user_settings_file('invalid syntax')
        self.settings = RFSettings(path=self.settings_file)
        self.assertEquals(self.settings._settings, {})

    def test_default_values_are_read_correctly_when_user_settings(self):
        defaults = {'foo':'bar', 'hello':'world'}
        self._write_settings({'foo':'new value'})
        expected = {'foo':'new value', 'hello':'world'}
        self.settings = RFSettings(path=self.settings_file, 
                                   defaults=defaults)
        self.assertEquals(self.settings._settings, expected)

    def test_changing_settings_with_setitem(self):
        defaults = {'foo':'bar', 'hello':'world'}
        self.settings = RFSettings(path=self.settings_file, 
                                   defaults=defaults)
        self.settings['foo'] = 'new value'
        expected = {'foo':'new value', 'hello':'world'}
        self.assertEquals(expected, self.settings._settings)

    def test_getting_settings_with_getitem(self):
        defaults = {'foo':'bar', 'hello':'world'}
        self.settings = RFSettings(path=self.settings_file, 
                                   defaults=defaults)
        self.assertEquals('bar', self.settings['foo'])

    def test_updating_settings_with_dict(self):
        defaults = {'foo':'bar', 'hello':'world'}
        self.settings = RFSettings(path=self.settings_file, 
                                   defaults=defaults)
        self.assertEquals(self.settings._settings, defaults)
        self.settings.update({'foo':'new value'})
        expected = {'foo':'new value', 'hello':'world'}
        self.assertEquals(self.settings._settings, expected)
        self.assertEquals(self._read_settings(), expected)
    
    def test_updating_settings_with_module(self):
        defaults = {'foo':'bar', 'hello':'world'}
        self.settings = RFSettings(path=self.settings_file, 
                                   defaults=defaults)
        self._write_settings({'foo':'new value'})
        expected = {'foo':'new value', 'hello':'world'}
        self.assertEquals(self.settings._settings, defaults)
        self.settings.update(self.settings_file)
        self.assertEquals(self.settings._settings, expected)
        self.assertEquals(self._read_settings(), expected)

    def test_updating_settings_with_module_and_not_saving(self):
        defaults = {'foo':'bar', 'hello':'world'}
        self.settings = RFSettings(path=self.settings_file, 
                                   defaults=defaults)
        
        self._write_settings({'foo':'new value'})
        expected = {'foo':'new value', 'hello':'world'}
        self.assertEquals(self.settings._settings, defaults)
        self.settings.update(self.settings_file, save=False)
        self.assertEquals(self.settings._settings, expected)
        self.assertEquals(self._read_settings(), {'foo':'new value'})

    def test_updating_settings_with_none(self):
        defaults = {'foo':'bar', 'hello':'world'}
        self.settings = RFSettings(path=self.settings_file, 
                                   defaults=defaults)
        self.settings.update(None)
        self.assertEquals(self.settings._settings, defaults)
        
    def test_saving(self):
        self.settings = RFSettings(path=self.settings_file)
        values = {'foo':'bar', 'hello':'world'}
        self.settings._settings = values
        self.settings.save()
        self.assertEquals(values, self._read_settings())
    
    def test_loading(self):
        self.settings = RFSettings(path=self.settings_file)
        values = {'foo':'bar', 'hello':'world'}
        self._write_settings(values)
        self.settings.load()
        self.assertEquals(values, self.settings._settings)
    
    def test_restoring(self):
        self.settings = RFSettings(path=self.settings_file, defaults={'a':1})
        values = {'foo':'bar', 'hello':'world'}
        self.settings.update(values)
        values['a'] = 1
        self.assertEquals(values, self.settings._settings)
        self.settings.restore()
        self.assertEquals({'a':1}, self.settings._settings)
        self.assertEquals({'a':1}, self._read_settings())
    
    def _write_settings(self, dict):
        io = SettingsIO(path=self.settings_file)
        io.write(dict)

    def _read_settings(self):
        io = SettingsIO(path=self.settings_file)
        return io.read()

    def _add_invalid_data_to_user_settings_file(self, data):
        f = open(self.settings_file, 'w')
        f.write(data)
        f.close()


if __name__ == "__main__":
    unittest.main()