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

from mabot.settings import Settings
from mabot.settings.defaultsettings import default_settings
from mabot.settings import USER_SETTINGS_FILE


class TestSettings(unittest.TestCase):

    def setUp(self):
        self._remove_settings()
        self.settings = Settings()

    def _remove_settings(self):
        for path in [USER_SETTINGS_FILE, '%sc' % USER_SETTINGS_FILE ]:
            if os.path.exists(path):
                os.remove(path)
            
    def tearDown(self):
        self._remove_settings()

    def test_loading_default_settings(self):
        expected = self.settings.settings.copy()
        expected["exclude"] = default_settings["exclude"]
        expected["ask_additional_tags_at_startup"] = default_settings["ask_additional_tags_at_startup"]
        self.assertEquals(self.settings.settings, expected)
        self.assertEquals(self.settings.settings["include"], [])
        self.assertEquals(self.settings.settings["exclude"], [])
        
    def test_saving_with_default_settings(self):
        self.settings.save_settings()
        self.assertEquals(self.settings.settings, 
                          self._read_settings_from_file())

    def test_saving_with_modified_settings(self):
        self.settings.save_settings()
        settings = self._read_settings_from_file()
        self.assertEquals(self.settings.settings, settings)
        self.settings.settings["default_message"] = "My message"
        self.settings.settings["exclude"] = ["a", "b", "c"]
        self.settings.save_settings()
        settings = self._read_settings_from_file()
        self.assertEquals(self.settings.settings, settings)
        self.assertEquals(self.settings.settings["exclude"], ["a", "b", "c"])
        self.settings.load_settings()
        self.assertEquals(self.settings.settings, settings)
          
    def test_reverting_default_settings(self):
        defaults = self.settings.settings.copy()
        self.settings.settings["default_message"] = "My message"
        self.settings.settings["exclude"] = ["a", "b", "c"]
        self.settings.save_settings()
        self.assertEquals(self.settings.settings["exclude"],["a", "b", "c"])
        self.assertTrue(os.path.exists(USER_SETTINGS_FILE))
        self.settings.restore_settings()
        self.assertEquals(self.settings.settings, defaults)
        self.assertFalse(os.path.exists(USER_SETTINGS_FILE))

    def _read_settings_from_file(self):
        import mabotsettings
        reload(mabotsettings)
        settings = {}
        for item in dir(mabotsettings):
            if not item.startswith('_'):
                settings[item] = getattr(mabotsettings, item)
        return settings
        
if __name__ == "__main__":
    unittest.main()