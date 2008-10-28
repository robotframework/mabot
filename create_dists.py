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


import os
import shutil
import subprocess

def _remove_build(root):
	build = os.path.join(root, 'build')
	if os.path.exists(build):
		shutil.rmtree(build)

def _remove_saved_settings(root):
	path = os.path.join(root, 'src', 'mabot', 'settings', 'settings.py')
	if os.path.exists(path):
		os.remove(path)

if __name__ == '__main__':
	root = os.path.dirname(__file__)
	_remove_build(root)
	_remove_saved_settings(root)
	subprocess.call('python setup.py bdist_wininst')
	subprocess.call('python setup.py sdist')
