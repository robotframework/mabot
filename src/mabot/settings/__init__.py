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
import os.path
import sys
from types import ListType
from types import StringType

import utils

USER_SETTINGS_FILE = utils.get_settings_path('mabotsettings.py')

class Settings:
    
    def __init__(self):
        self._user_settings = utils.SettingsIO(USER_SETTINGS_FILE)
        self.load_settings()

    def update(self, new_settings, suite):
        if not new_settings:
            return
        if self.settings["default_message"] != new_settings["default_message"]:
           suite.update_default_message(self.settings["default_message"],
                                        new_settings["default_message"])        
        self.settings = new_settings
        self.save_settings()
    
    def save_settings(self):
        self._user_settings.write_settings(self.settings)

    def __getitem__(self, name):
        return self.settings[name]

    def __setitem__(self, name, value):
        self.settings[name] = value

    def load_settings(self):
        from defaultsettings import default_settings
        self.settings = default_settings.copy()
        try:
            from projectsettings import project_settings
            for key in project_settings.keys():
                self.settings[key] = project_settings[key]
        except (ImportError, KeyError):
            pass
        try:
            user_settings = self._user_settings.read_settings()
        except (utils.MissingSettings, utils.InvalidSettings):
            pass
        else:
            for key in user_settings.keys():
                self.settings[key] = user_settings[key]
            
        
    def restore_settings(self):
        self._user_settings.remove_settings()
        self.load_settings()


SETTINGS = Settings()
