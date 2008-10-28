#!/usr/local/bin python

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


"""Setup script for Robot Framework's Mabot tool distributions"""

from distutils.core import setup
import os
from os.path import dirname, join
import sys

def main():
    setup(name         = 'Mabot',
          version      =  _get_version(),
          description  = 'Manual test result reporting tool for Robot Framework',
          author       = 'Robot Framework Developers',
          author_email = 'robotframework-devel@googlegroups.com',
          url          = 'http://code.google.com/p/robotframework-mabot/',
          license      = 'Apache License 2.0',
          platforms    = 'any',
          package_dir  = { '' : 'src'},
          packages     = ['mabot', 'mabot.model', 'mabot.settings', 
                          'mabot.ui', 'mabot.utils'],
          package_data = { 'mabot': ['ui/icons/*.gif']},
          scripts      = [ 'src/bin/mabot.py' ]
          )

def _get_version():        
    sys.path.insert(0, join(dirname(__file__), 'src', 'mabot'))
    from version import version
    return version

if __name__ == "__main__":
    main()
    
