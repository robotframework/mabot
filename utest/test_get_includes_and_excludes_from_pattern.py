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

from mabot.model.model import get_includes_and_excludes_from_pattern


class TestGetIncludesAndExcludesFromPattern(unittest.TestCase):

    def test_empty(self):
        self._test_pattern('', [], [])

    def test_star_only(self):
        self._test_pattern('*', ['*'], [])

    def test_multiple_excludes(self):
        self._test_pattern('NOThelloNOTsomeNOTagain', [], ['*'])
        self._test_pattern('againNOThelloNOTsomeNOT', [], ['*'])
        self._test_pattern('againNOThelloNOTNOTsome', [], ['*'])

    def test_multiple_includes(self):
        self._test_pattern('helloANDsome&again',
                           ['hello&some&again'], [])

    def test_include_and_exclude(self):
        self._test_pattern('*NOThello', ['*'], ['hello'])

    def test_include_and_multiple_excludes(self):
        self._test_pattern('*NOThelloNOTsomeNOTagain', ['*'],
                           ['hello', 'some', 'again'])

    def test_multiple_includes_and_exclude(self):
        self._test_pattern('helloANDsomeNOTagain', ['hello&some'], ['again'])

    def test_multiple_includes_and_multiple_excludes(self):
        self._test_pattern('helloANDsomeNOTagainNOTmore',
                           ['hello&some'], ['again', 'more'])

    def _test_pattern(self, pattern, includes, excludes):
        expected = (includes, excludes)
        actual = get_includes_and_excludes_from_pattern(pattern)
        self.assertEquals(expected, actual, '\n%s !=\n%s' % (expected, actual))


if __name__ == "__main__":
    unittest.main()
