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
import unittest

from robot.utils.asserts import assert_raises_with_msg

from mabot.utils.lock import LockFile, LockException
from mabot.utils import lock as lock_module


class MockLockFile(LockFile):

    def __init__(self, path, time, user):
        self.time = time
        self.user = user
        LockFile.__init__(self, path)

    def _get_time(self):
        return self.time

    def _get_user(self):
        return self.user

class MockLockWriting(MockLockFile):

    def _write(self, path, content):
        raise Exception("Writing to file failed!")


lock_file_content = """File '%s' is locked for user '%s'.
Editing started at %s.
"""

class TestLockFile(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), '..', 'data', 'a.xml')
        self.lock_path = self.path + '.lock'
        self.lock_path = self.lock_path.replace('\\', '\\\\')
        self.time = "20080808"
        self.user = "user"
        self.lock = MockLockFile(self.path, self.time, self.user)
        self.expected1 = lock_file_content % (self.path, self.user, self.time)
        self._remove_lock()
        self.time2 = "2123"
        self.user2 = "someone"
        self.lock2 = MockLockFile(self.path, self.time2, self.user2)
        self.expected2 = lock_file_content % (self.path, self.user2, self.time2)

    def _remove_lock(self):
        if os.path.exists(self.lock_path):
            os.remove(self.lock_path)

    def _get_lock_file_content(self, path):
        lock = open(self.lock_path, 'r')
        content = lock.read()
        lock.close()
        return content

    def tearDown(self):
        self._remove_lock()


    def test_create_lock_no_lock_1(self):
        value = self.lock.create_lock(MockDialog(True).dialog)
        self.assertEqual(value, self.expected1)
        self.assertTrue(os.path.exists(self.lock_path))

    def test_create_lock_no_lock_2(self):
        value = self.lock.create_lock(MockDialog(False).dialog)
        self.assertEqual(value, self.expected1)
        self.assertTrue(os.path.exists(self.lock_path))

    def test_create_lock_lock_is_not_override(self):
        lock_file_content = self.lock.create_lock(MockDialog(True).dialog)
        self.assertEqual(lock_file_content, self.expected1)
        self.assertTrue(os.path.exists(self.lock_path))
        self.assertRaises(LockException, self.lock2.create_lock, MockDialog(False).dialog)
        self.assertEqual(self._get_lock_file_content(self.path), self.expected1)

    def test_create_lock_lock_is_override(self):
        lock_file_content_1 = self.lock.create_lock(MockDialog(True).dialog)
        self.assertEqual(lock_file_content_1, self.expected1)
        self.assertTrue(os.path.exists(self.lock_path))
        lock_file_content_2 = self.lock2.create_lock(MockDialog(True).dialog)
        self.assertEqual(lock_file_content_2, self.expected2)
        self.assertTrue(os.path.exists(self.lock_path))

    def test_release_log(self):
        lock_file_content_1 = self.lock.create_lock(MockDialog(True).dialog)
        self.assertEqual(lock_file_content_1, self.expected1)
        self.assertTrue(os.path.exists(self.lock_path))
        self.lock.release_lock()
        self.assertFalse(os.path.exists(self.lock_path))

    def test_create_lock_writing_to_lock_fails(self):
        lock = MockLockWriting(self.path, self.time, self.user)
        self.assertRaises(LockException, lock.create_lock, MockDialog(False).dialog)

    def test_reading_lock_fails(self):
        try:
            orig_os_path_exists = lock_module.os.path.exists
            lock_module.os.path.exists = lambda x: True
            msg = "Could not read lock: [Errno 2] No such file or directory: '%s'" % (self.lock_path)
            assert_raises_with_msg(LockException, msg, 
                                   self.lock._get_lock_file)
        finally:
            lock_module.os.path.exists = orig_os_path_exists

    def test_releasing_lock_fails(self):
        try:
            orig_os_path_exists = lock_module.os.path.exists
            lock_module.os.path.exists = lambda x: True
            msg = """Could not remove lock file. Could not read lock: [Errno 2] No such file or directory: '%s'""" % self.lock_path
            assert_raises_with_msg(LockException, msg, self.lock.release_lock)
        finally:
            lock_module.os.path.exists = orig_os_path_exists

    def test_releasing_lock_fails_when_content_have_been_changed(self):
        self.lock.create_lock(MockDialog(True))
        self.lock.content = "Another user stole the lock."
        msg = """Could not remove lock file. Data edited while you were saving it.
Use "Save As" to save results to some other file
and resolve the conflicts manually."""
        assert_raises_with_msg(LockException, msg, self.lock.release_lock)


class TestGetUser(unittest.TestCase):

    def setUp(self):
        self._lock_file = LockFile('none')
        self.orig_username = os.environ.get('USERNAME', None)

    def tearDown(self):
        if self.orig_username:
            os.environ['USERNAME'] = self.orig_username

    def test_get_user(self):
        os.environ['USERNAME'] = 'user'
        self.assertEqual(self._lock_file._get_user(), 'user')

    def test_get_user_when_it_does_not_exist(self):
        os.environ.pop('USERNAME', 'default which prevents KeyError')
        self.assertEqual(self._lock_file._get_user(), 'Unknown')


class MockDialog:

    def __init__(self, return_value):
        self.return_value = return_value

    def dialog(self, title, message):
        self.title = title
        self.message = message
        return self.return_value


if __name__ == "__main__":
    unittest.main()
