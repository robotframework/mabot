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
from robot.utils.asserts import *

from mabot.ui import tree


class _Mock:

    def __init__(self, name, mediumname, longname, visible):
        self.parent = None
        self.name = name
        if mediumname:
            self.mediumname = mediumname
        else:
            self.mediumname = name
        if longname:
            self.longname = longname
        else:
            self.longname = name
        self.visible = visible

class MockSuite(_Mock):

    def __init__(self, name, mediumname=None, longname=None, visible=True,
                 suites=[], tests=[]):
        _Mock.__init__(self, name, mediumname, longname, visible)
        for suite in suites:
            suite.parent = self
        self.suites = suites
        for test in tests:
            test.parent = self
        self.tests = tests

class MockTest(_Mock):

    def __init__(self, name, mediumname=None, longname=None,
                 visible=True, keywords=[]):
        _Mock.__init__(self, name, mediumname, longname, visible)
        for kw in keywords:
            kw.parent = self
        self.keywords = keywords

class TestTreeSuite(unittest.TestCase):


    def test_simple_suite_name(self):
        suite = MockSuite('Suite')
        tree_suite = tree.SuiteTreeItem(suite)
        self.assertEquals(tree_suite.label, 'Suite')

    def test_name_when_test_cases(self):
        test1 = MockTest('Test1')
        test2 = MockTest('Test2')
        suite = MockSuite('Suite1', tests = [test1, test2])
        tree_suite = tree.SuiteTreeItem(suite)
        self.assertEquals(tree_suite.label, 'Suite1')

    def test_name_when_test_suites(self):
        sub1 = MockSuite('SubSuite1')
        sub2 = MockSuite('SubSuite2')
        suite = MockSuite('Suite1', suites = [sub1, sub2])
        tree_suite = tree.SuiteTreeItem(suite)
        self.assertEquals(tree_suite.label, 'Suite1')
        self.assertEquals(tree_suite.children[0].label, 'SubSuite1')
        self.assertEquals(tree_suite.children[1].label, 'SubSuite2')

    def test_collapse_all_suites_with_one_sub_suite_with_one_test_leaf(self):
        test1 = MockTest('Test1')
        subsub1 = MockSuite('SubSubSuite1', tests=[test1])
        sub1 = MockSuite('SubSuite1', suites=[subsub1])
        suite = MockSuite('Suite1', suites = [sub1])
        tree_suite = tree.SuiteTreeItem(suite)
        self.assertEquals(tree_suite.label, 'Suite1/SubSuite1')
        self.assertEquals(tree_suite.children[0].label, 'SubSubSuite1')
        self.assertEquals(tree_suite.children[0].children[0].label, 'Test1')

    def test_collapse_all_suites_with_one_sub_suite_with_two_suites_with_test(self):
        test1 = MockTest('Test1')
        test2 = MockTest('Test2')
        subsub1 = MockSuite('SubSubSuite1', tests=[test1])
        subsub2 = MockSuite('SubSubSuite2', tests=[test2])
        sub1 = MockSuite('SubSuite1', suites=[subsub1, subsub2])
        suite = MockSuite('Suite1', suites = [sub1])
        tree_suite = tree.SuiteTreeItem(suite)
        self.assertEquals(tree_suite.label, 'Suite1/SubSuite1')
        self.assertEquals(tree_suite.children[0].label, 'SubSubSuite1')

    def test_collapse_all_suites_with_one_sub_suite_with_one_test_leaf_and_one_non_visible_test_leaf(self):
        test1 = MockTest('Test1')
        subsub1 = MockSuite('SubSubSuite1', tests=[test1])
        sub1 = MockSuite('SubSuite1', suites=[subsub1])
        test2 = MockTest('Test2', visible=False)
        subsub2 = MockSuite('SubSubSuite2', visible=False, tests=[test2])
        sub2 = MockSuite('SubSuite2', visible=False, suites=[subsub2])
        suite = MockSuite('Suite1', suites = [sub1, sub2])
        tree_suite = tree.SuiteTreeItem(suite)
        self.assertEquals(tree_suite.label, 'Suite1/SubSuite1')
        self.assertEquals(tree_suite.children[0].label, 'SubSubSuite1')
        self.assertEquals(len(tree_suite.children), 1)
        self.assertEquals(len(tree_suite.children[0].children), 1)

    def test_get_icon_names_with_file_suite(self):
        test = MockTest('Test')
        suite = MockSuite('Suite', tests=[test])
        tree_suite = tree.SuiteTreeItem(suite)
        self.assertEquals(tree_suite.GetIconName(), 'file_suite')

    def test_get_icon_names_with_dir_suite(self):
        subsuite = MockSuite('SubSuite')
        suite = MockSuite('Suite', suites=[subsuite])
        tree_suite = tree.SuiteTreeItem(suite)
        self.assertEquals(tree_suite.GetIconName(), 'dir_suite')


if __name__ == "__main__":
    unittest.main()
