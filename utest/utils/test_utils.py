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

from mabot.utils import get_tags_from_string, get_status_color

class TestGetTagsFromString(unittest.TestCase):

    def test_string_without_tags(self):
        self.assertEquals(get_tags_from_string(''), [])

    def test_string_with_one_tag(self):
        self.assertEquals(get_tags_from_string('tag-1'), ['tag-1'])

    def test_string_with_multiple_tags(self):
        self.assertEquals(get_tags_from_string('tag-1, tag, another'), 
                          ['tag-1', 'tag', 'another'])

    def test_string_with_comma_tags(self):
        self.assertEquals(get_tags_from_string('tag-1, another,tag'), 
                          ['tag-1', 'another,tag'])

class TestGetStatusColor(unittest.TestCase):

    def test_get_status_color_pass(self):
        self.assertEquals(get_status_color(MockItem('PASS')), 'green')

    def test_get_status_color_fail(self):
        self.assertEquals(get_status_color(MockItem('FAIL')), 'red')

    def test_get_status_color_not_run(self):
        self.assertEquals(get_status_color(MockItem('NOT_EXECUTED')), 'black')

    def test_get_status_color_invalid(self):
        self.assertEquals(get_status_color(MockItem('INVALID')), 'black')


class MockItem(object):

    def __init__(self, status):
        self.status = status

    def get_execution_status(self):
        return self.status


if __name__ == "__main__":
    unittest.main()
