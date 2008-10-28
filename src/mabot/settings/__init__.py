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
from types import ListType
from types import StringType

USER_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'settings.py')
COMPILED_USER_SETTINGS_FILE = USER_SETTINGS_FILE + 'c'

class Settings:
    
    def __init__(self):
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
        self._remove_user_settings()
        try:
            settings_file = open(USER_SETTINGS_FILE, 'w')
            settings_file.write(str(self))
        finally:
            settings_file.close()
    
    def __str__(self):
        data = 'settings = {\n'
        for key, value in self.settings.items():
            data += '            "%s": %s,\n' % (key, self._value_to_str(value))
        return data + '           }\n'

    def _value_to_str(self, value):
        if type(value) is StringType:
            return '"""%s"""' % (value)
        elif type(value) is ListType:
            string_values = [self._value_to_str(item) for item in value ]
            return "[ %s ]" % (', '.join(string_values))
        return value
        
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
        except:
            pass
        try:
            import settings
            reload(settings)
            for key in settings.settings.keys():
                self.settings[key] = settings.settings[key]
        except:
            pass
        
    def restore_settings(self):
        self._remove_user_settings()
        self.load_settings()

    def _remove_user_settings(self):
        if os.path.exists(USER_SETTINGS_FILE):
            os.remove(USER_SETTINGS_FILE)
        if os.path.exists(COMPILED_USER_SETTINGS_FILE):
            os.remove(COMPILED_USER_SETTINGS_FILE)

SETTINGS = Settings()
