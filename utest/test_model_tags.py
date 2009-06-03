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


from copy import deepcopy
from os.path import dirname, join, normcase
import unittest

from mabot.model import model
from mabot.model.io import IO


class _TestAddAndRemoveTags(unittest.TestCase):

    def setUp(self):
        data = normcase(join(dirname(__file__), 'data', 'root_suite'))
        self.suite = IO().load_data(data)
        self.test = self.suite.suites[0].tests[0]
        self.orig_settings = deepcopy(model.SETTINGS)
        
    def tearDown(self):
        model.SETTINGS = self.orig_settings
        
    def _test_tags(self, initial_tags, method, input, expected, 
                   tags_allowed_only_once=[]):
        self.test.tags = initial_tags[:]
        model.SETTINGS["tags_allowed_only_once"] = tags_allowed_only_once
        method(input)
        self.assertEquals(self.test.tags, expected)

class TestAddingTags(_TestAddAndRemoveTags):
    
    def _test_add_tags(self, initial_tags, input, expected, 
                       tags_allowed_only_once=[]):
        self._test_tags(initial_tags, self.test.add_tags, input, expected, 
                        tags_allowed_only_once)
    
    def test_adding_tags_when_no_only_once_tags_defined(self):
        self._test_add_tags([], ['foo'], ['foo'])

    def test_adding_tag_not_in_only_once_tags(self):
        self._test_add_tags([], ['foo'], ['foo'])

    def test_adding_tag_in_only_once_tags_but_no_tags_to_remove(self):
        self._test_add_tags(['bar'], ['not-foo'], 
                        ['bar', 'not-foo'], ['not-'])

    def test_adding_tag_in_only_once_tags_and_one_tag_to_remove(self):
        self._test_add_tags(['not-bar'], ['not-foo'], 
                            ['not-foo'], ['not-'])

    def test_adding_tag_in_only_once_tags_and_three_tags_to_remove(self):
        self._test_add_tags(['tag-1', 'tag-2', 'tag-3'], ['tag-foo'], 
                            ['tag-foo'], ['tag-'])
    
    def test_adding_multiple_tags_some_matching_only_once_tags_and_not_tags_to_remove(self):
        self._test_add_tags(['tag-1', 'tag-2'], ['some', 'build-x', 'reg-2'], 
                            ['build-x', 'reg-2', 'some', 'tag-1', 'tag-2'], 
                            ['req-', 'build'])

    def test_adding_multiple_tags_some_matching_only_once_tags_and_one_tag_to_remove(self):
        self._test_add_tags(['tag-1', 'tag-2', 'build-y'],
                            ['some', 'build-x', 'reg-2'], 
                            ['build-x', 'reg-2', 'some', 'tag-1', 'tag-2'], 
                            ['req-', 'build'])

    def test_adding_multiple_tags_some_matching_only_once_tags_and_multiple_tags_to_remove(self):
        initial_tags = ['build-x', 'executed-by-james', 'other',
                        'req-1', 'tag-1', 'tag-2', 'tag-3']
        add_tags = ['build-y', 'executed-by-bond', 'req-2', 'some', 'tag-4']
        expected = ['build-y', 'executed-by-bond', 'other',
                    'req-1', 'req-2', 'some', 'tag-4']
        self._test_add_tags(initial_tags, add_tags, expected, 
                            ['tag-', 'build-', 'executed-by-'])
    
    def test_adding_tags_to_suite(self):
        self._test_tags(['some', 'other'], self.suite.add_tags, ['foo', 'bar'], 
                        ['bar', 'foo', 'other', 'some'])
        self.assertTrue(self.test.is_modified)

    def test_adding_tags_to_suite_when_it_is_not_visible(self):
        self.suite.visible = False
        self._test_tags(['some', 'other'], self.suite.add_tags, ['foo', 'bar'], 
                        ['some', 'other'])
        self.assertFalse(self.test.is_modified)

    def test_adding_tags_to_test_when_it_is_not_visible(self):
        self.test.visible = False
        self._test_add_tags(['some', 'other'], ['foo', 'bar'], ['some', 'other'])
        self.assertFalse(self.test.is_modified)
        
    def test_test_is_marked_as_modified_when_tags_are_added(self):
        self._test_add_tags(['some'], ['bar'], ['bar', 'some'])
        self.assertTrue(self.test.is_modified)


class TestRemovingTags(_TestAddAndRemoveTags):
    
    def _test_remove_tags(self, initial_tags, input, expected):
        self._test_tags(initial_tags, self.test.remove_tags, input, expected)
        
    def test_removing_tags_no_tags_matching_found(self):
        self._test_remove_tags(['some'], ['bar'], ['some'])
        self.assertFalse(self.test.is_modified)

    def test_removing_tags_one_removed(self):
        self._test_remove_tags(['some'], ['some'], [])
        self.assertTrue(self.test.is_modified)

    def test_removing_tags_three_removed(self):
        self._test_remove_tags(['some', 'more', 'tags'], ['some', 'tags'], 
                               ['more'])
        self.assertTrue(self.test.is_modified)

    def test_removing_tags_from_test_when_it_is_not_visible(self):
        self.test.visible = False
        self._test_remove_tags(['some'], ['some'], ['some'])
        self.assertFalse(self.test.is_modified)
        
    def test_adding_tags_to_suite(self):
        self._test_tags(['some', 'tag'], self.suite.remove_tags, ['foo', 'some'], 
                        ['tag'])
        self.assertTrue(self.test.is_modified)

    def test_adding_tags_to_suite_when_it_is_not_visible(self):
        self.suite.visible = False
        self._test_tags(['some', 'tag'], self.suite.remove_tags, ['foo', 'some'], 
                        ['some', 'tag'])
        self.assertFalse(self.test.is_modified)


class TestMarkDataModified(_TestAddAndRemoveTags):

    def setUp(self):
        _TestAddAndRemoveTags.setUp(self)
        model.SETTINGS["additional_tags"] = ['foo', 'tag-1']
        self.test.tags = ['bar']

    def test_if_test_is_executed_additional_tags_are_added(self):        
        self.test._mark_data_modified(executed=True)
        self.assertEquals(self.test.tags, ['bar', 'foo', 'tag-1'])

    def test_if_test_is_not_executed_additional_tags_are_not_added(self):
        self.test._mark_data_modified(executed=False)
        self.assertEquals(self.test.tags, ['bar'])


if __name__ == "__main__":
    unittest.main()