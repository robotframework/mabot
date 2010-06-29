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

from mabot.model import io
from mabot.model.model import DATA_MODIFIED


DATA = os.path.join(os.path.dirname(__file__), 'data', 'testcases.xml')


class TestSettingStatusAndMessage(unittest.TestCase):

    def setUp(self):
        self.io = io.IO()
        self.suite = self.io.load_data(DATA)

    def tearDown(self):
        DATA_MODIFIED.saved()

    def test_pass_all_with_suite(self):
        self.suite.set_all('PASS')
        self._all_status_should_be(self.suite, 'PASS')
        expected_messages = ['Passing', '', 'Failing', 'Not Executed!']
        self._messages_should_be(self.suite.tests, expected_messages)
        expected_messages[3] = ''
        self._messages_should_be(self.suite.tests[0].keywords, expected_messages)
        self._messages_should_be(self.suite.tests[1].keywords, expected_messages)
        self._messages_should_be(self.suite.tests[2].keywords, expected_messages)
        self._messages_should_be(self.suite.tests[3].keywords, expected_messages)


    def test_fail_all_with_suite(self):
        self.suite.set_all('FAIL', 'Suite failure')
        self._all_status_should_be(self.suite, 'FAIL')
        expected_messages = ['Suite failure\nPassing', 'Suite failure',
                             'Suite failure\nFailing', 'Suite failure']
        self._messages_should_be(self.suite.tests, expected_messages)
        for i in range(0, 4):
            self._messages_should_be(self.suite.tests[i].keywords,
                                     expected_messages)

    def test_fail_all_with_test(self):
        test = self.suite.tests[0]
        test.set_all('PASS')
        self._all_status_should_be(test, 'PASS')
        expected_messages = ['Passing', '', 'Failing', '']
        self._messages_should_be(test.keywords, expected_messages)

    def test_fail_all_with_test(self):
        test = self.suite.tests[0]
        test.set_all('FAIL', 'Test failure')
        self._all_status_should_be(test, 'FAIL')
        expected_messages = ['Test failure\nPassing', 'Test failure',
                             'Test failure\nFailing', 'Test failure']
        self._messages_should_be(test.keywords, expected_messages)

    def test_suite_is_informed(self):
        self.suite.tests[2].set_all('PASS')
        self.suite.tests[3].set_all('PASS')
        self.suite.tests[4].set_all('PASS')
        self.assertEqual(self.suite.status, 'PASS')

    def test_pass_all_with_keyword(self):
        test = self.suite.tests[4]
        test.set_all('FAIL', 'Test failure')
        self._all_status_should_be(test, 'FAIL')
        self.assertEquals(test.keywords[0].keywords[0].status, 'FAIL')
        test.set_all('PASS', 'Test failure')
        self._all_status_should_be(test, 'PASS')
        self.assertEquals(test.keywords[0].status, 'PASS')
        self.assertEquals(test.keywords[0].keywords[0].status, 'PASS')

    def test_change_test_status_to_fail(self):
        test = self.suite.tests[0]
        test.update_status_and_message('FAIL', 'Failure')
        self.assertEqual(test.status, 'FAIL')
        self.assertTrue(test.is_modified)
        self.assertTrue(DATA_MODIFIED.is_modified)
        expected_messages = ['Passing', '', 'Failing', '']
        self._messages_should_be(test.keywords, expected_messages)

    def test_change_test_status_to_pass(self):
        test = self.suite.tests[2]
        test.update_status_and_message('PASS')
        self.assertEqual(test.status, 'PASS')
        self._should_be_modified(test)
        self._messages_should_be(test.keywords, ['Passing', '', 'Failing', ''])

    def test_change_tests_message(self):
        test = self.suite.tests[0]
        test.update_status_and_message('PASS', 'Hello')
        self.assertEqual(test.status, 'PASS')
        self.assertEqual(test.message, 'Hello')
        self._should_be_modified(test)

    def test_change_nothing_from_test(self):
        test = self.suite.tests[0]
        test.update_status_and_message('PASS', '   Passing   \n')
        self.assertEqual(test.status, 'PASS')
        self._should_not_be_modified(test)

    def test_suite_status_is_changed_when_test_statuses_are_changed(self):
        self.suite.tests[2].update_status_and_message('PASS', '')
        self.assertEqual(self.suite.status, 'FAIL')
        self.suite.tests[3].update_status_and_message('PASS', '')
        self.suite.tests[4].update_status_and_message('PASS', '')
        self.assertEqual(self.suite.status, 'PASS')
        self.suite.tests[1].update_status_and_message('FAIL', 'Failure')
        self.assertEqual(self.suite.status, 'FAIL')

    def test_test_status_is_changed_when_keywords_statuses_are_changed(self):
        test = self.suite.tests[2]
        test.keywords[2].update_status_and_message('PASS', '')
        self.assertEqual(test.status, 'FAIL')
        test.keywords[3].update_status_and_message('PASS', '')
        self.assertEqual(test.status, 'PASS')

    def test_setting_status_when_test_is_not_visible(self):
        test = self.suite.tests[2]
        test.visible = False
        test.update_status_and_message('PASS', '')
        self.assertEqual(test.status, 'FAIL')

    def _should_be_modified(self, item):
        self.assertTrue(item.is_modified)
        self.assertTrue(DATA_MODIFIED.is_modified())

    def _should_not_be_modified(self, item):
        self.assertFalse(item.is_modified)
        self.assertFalse(DATA_MODIFIED.is_modified())

    def _all_status_should_be(self, item, status):
        msg = "'%s' status was '%s', it should be '%s'"
        name = getattr(item, 'longname', item.name)
        msg = msg % (name, item.status, status)
        self.assertEqual(item.status, status, msg)
        for sub_item in item._get_items():
            self._all_status_should_be(sub_item, status)

    def _messages_should_be(self, items, messages):
        for item, message in zip(items, messages):
            msg = "'%s' message was '%s', it should be '%s'"
            name = getattr(item, 'longname', item.parent.longname+'.'+ item.name)
            msg = msg % (name, item.message, message)
            self.assertEqual(item.message, message, msg)

class TestGetExecutionStatus(unittest.TestCase):

    def setUp(self):
        self.io = io.IO()
        self.suite = self.io.load_data(DATA)

    def tearDown(self):
        DATA_MODIFIED.saved()

    def test_get_execution_status_not_executed_with_suite(self):
        self.suite.tests[3].keywords[2].message = ''
        self.assertEqual(self.suite.get_execution_status(), 'NOT_EXECUTED')

    def test_get_execution_status_failed_with_suite(self):
        self.assertEqual(self.suite.get_execution_status(), 'FAIL')

    def test_get_execution_status_passed_with_suite(self):
        self.suite.tests[2].set_all('PASS')
        self.suite.tests[3].set_all('PASS')
        self.suite.tests[4].set_all('PASS')
        self.assertEqual(self.suite.get_execution_status(), 'PASS')

    def test_get_execution_status_with_suite_when_some_tests_not_visible(self):
        self.suite.tests[2].visible = False
        self.suite.tests[3].visible = False
        self.suite.tests[4].visible = False
        self.assertEqual(self.suite.get_execution_status(), 'PASS')


    def test_get_execution_status_not_executed_with_test(self):
        test = self.suite.tests[3]
        test.keywords[2].message = ''
        self.assertEqual(test.get_execution_status(), 'NOT_EXECUTED')

    def test_get_execution_status_failed_with_test(self):
        self.assertEqual(self.suite.tests[3].get_execution_status(), 'FAIL')

    def test_get_execution_status_passed_with_test(self):
        test = self.suite.tests[0]
        test.set_all('PASS')
        self.assertEqual(test.get_execution_status(), 'PASS')

    def test_get_execution_status_not_executed_with_kw(self):
        self.assertEqual(self.suite.tests[0].keywords[3].get_execution_status(),
                         'NOT_EXECUTED')


    def test_get_execution_status_failed_with_kw(self):
        self.assertEqual(self.suite.tests[0].keywords[2].get_execution_status(),
                         'FAIL')

    def test_get_execution_status_passed_with_kw(self):
        self.assertEqual(self.suite.tests[0].keywords[1].get_execution_status(),
                         'PASS')

if __name__ == "__main__":
    unittest.main()
