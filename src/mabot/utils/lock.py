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
import time

class LockFile:
    
    def __init__(self, path):
        self.path = path
        self.lock_path = path + '.lock'
        self.lock_file_content = None
        
    def create_lock(self, ask_method):
        """Checks whether the lock file exists. Calls ask_method if it exists.

        Returns the the content of the created lock. Raises exception in case 
        creating the lock file fails.
        """
        lock_file_content = self._get_lock_file()
        message = "%s\nDo you want to remove the lock?" % (lock_file_content)
        if lock_file_content is not None and \
            not ask_method("File locked for editing!", message):
            raise LockException("Lock '%s' not overridden." % self.lock_path)
        return self._create_lock()

    def _get_lock_file(self):
        if not os.path.exists(self.lock_path):
            return None
        try :
            lock = open(self.lock_path, 'r')
            content = lock.read()
            lock.close()
        except Exception, error:
            try:
                lock.close()
            except:
                pass
            message = "Could not read lock '%s'.\n%s" % (self.lock_path, 
                                                         error[0])
            raise LockException(message)
        return content

    def _create_lock(self):
        """Creates the lock and returns the lock file content."""
        content = """File '%s' is locked for user '%s'.
Editing started at %s.
"""
        content = content % (self.path, self._get_user(), self._get_time())
        try:
            lock = open(self.lock_path, 'w')
            self._write(lock, content)
            lock.close()
        except Exception, error:
            lock.close()
            raise LockException("Could not create the lock. %s" % (error[0]))
        self.content = content
        return self.content

    def _get_user(self):
        try:
            user = os.environ["USERNAME"]
        except:
            user = "Unknown"
        return user
    
    def _write(self, file, content):
        file.write(content)

    def _get_time(self):
        return time.asctime()
    
    def release_lock(self):
        """Releases the created lock file."""
        try:
            content = self._get_lock_file()
            if content != self.content:
                msg = """Data edited while you were saving it.
Use "Save As" to save results to some other file 
and resolve the conflicts manually."""
                raise LockException(msg)
            if os.path.exists(self.lock_path):
                os.remove(self.lock_path)
        except Exception, error:
            raise LockException("Could not remove lock file. %s" % (error[0]))


class LockException(Exception):
    
    pass

