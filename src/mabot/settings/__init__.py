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

from utils import RFSettings

class Settings(RFSettings):
    
    def __init__(self, path=None):
        self.defaults_settings = os.path.join(os.path.dirname(__file__), 
                                              'defaultsettings.py')
        self.project_settings = os.path.join(os.path.dirname(__file__), 
                                              'projectsettings.py')
        defaults = RFSettings(path=self.project_settings, 
                              defaults=self.defaults_settings)._settings
        if path:
            RFSettings.__init__(self, path=path, defaults=defaults)
        else:
            RFSettings.__init__(self, 'mabot', defaults=defaults)
        self.load()

    def update_settings(self, new_settings, suite):
        if not new_settings:
            return
        suite.update_default_message(self._settings["default_message"],
                                     new_settings["default_message"])        
        RFSettings.update(self, new_settings)
   

SETTINGS = Settings()
