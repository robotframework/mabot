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


import unittest
import os.path

from mabot.settings import Settings, defaultsettings
from mabot.settings.utils import SettingsIO

        
class TestSettings(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), 'data', 
                                 'testsettings.py')
        self._remove_settings()
        self.settings = Settings(self.path)
        self.suite = Suite()

    def tearDown(self):
        self._remove_settings()

    def test_loading_default_settings(self):
        expected = self.settings._settings.copy()
        expected = self._read_settings_from_file(defaultsettings.__file__[:-1])
        self.assertEquals(self.settings._settings, expected)
        self.assertEquals(self.settings._settings["include"], [])
        self.assertEquals(self.settings._settings["exclude"], [])
        self.assertEquals(self.settings._settings["default_message"], 
                          "Not Executed!")
        
    def test_saving_with_default_settings(self):
        self.settings.save()
        self.assertEquals(self.settings._settings, 
                          self._read_settings_from_file())

    def test_saving_with_modified_settings(self):
        self.settings.save()
        settings = self._read_settings_from_file()
        self.assertEquals(self.settings._settings, settings)
        self.settings._settings["default_message"] = "My message"
        self.settings._settings["exclude"] = ["a", "b", "c"]
        self.settings.save()
        settings = self._read_settings_from_file()
        self.assertEquals(self.settings._settings, settings)
        self.assertEquals(self.settings._settings["exclude"], ["a", "b", "c"])
        self.settings.load()
        self.assertEquals(self.settings._settings, settings)
          
    def test_reverting_default_settings(self):
        defaults = self.settings._settings.copy()
        self.settings._settings["default_message"] = "My message"
        self.settings._settings["exclude"] = ["a", "b", "c"]
        self.settings.save()
        self.assertEquals(self.settings._settings["exclude"],["a", "b", "c"])
        self.assertTrue(os.path.exists(self.path))
        self.settings.restore()
        self.assertEquals(self.settings._settings, defaults)
        self.assertEquals(self._read_settings_from_file(), defaults)

    def test_update_settings_affects_suite_when_default_message_is_not_changed(self):
        defaults = {'default_message':"Not Executed!"}
        self.settings.update_settings(defaults, self.suite)
        self.assertEquals(self.suite.called, [])
        
    def test_update_settings_affects_suite_when_default_message_is_changed(self):
        not_defaults = {'default_message':"New"}
        self.settings.update_settings(not_defaults, self.suite)
        self.assertEquals(self.suite.called, [('Not Executed!', 'New')])

    def _read_settings_from_file(self, path=None):
        if path:
            return SettingsIO(path=path).read()
        return SettingsIO(path=self.path).read()

    def _remove_settings(self):
        if os.path.exists(self.path):
            os.remove(self.path)

class Suite:
    
    def __init__(self):
        self.called = []
        
    def update_default_message(self, orig, changed):
        self.called.append((orig, changed))


if __name__ == "__main__":
    unittest.main()