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


import tkMessageBox

from mabot.settings import SETTINGS
from mabot import utils
from mabot.utils import robotapi


class Modified:

    def __init__(self):
        self.status = False

    def modified(self):
        self.status = True

    def saved(self):
        self.status = False

    def is_modified(self):
        return self.status


DATA_MODIFIED = Modified()

ALL_TAGS_VISIBLE = "ALL MATCHING TAGS VISIBLE"

class EmptySuite:
    """Suite used when initializing the Mabot without data"""

    def __init__(self):
        self.parent = None
        self.doc = self.name = self.starttime = self.endtime = ''
        self.status = self.message = ''
        self.metadata = {}
        self.tests = self.suites = []

    def __nonzero__(self):
        return 1

    def is_suite(self):
        return True

    def __getattr__(self, name):
        return self.do_nothing

    def get_execution_status(self):
        return 'PASS'

    def do_nothing(self, *args, **kw_args):
        return ""

    def get_all_visible_tags(self):
        return []


class UserKeywordLibrary:

    def __init__(self):
        self.keywords = {}

    def add_suite_keywords(self, suite):
        self.keywords = suite.user_keywords.handlers

    def get_keywords(self, name, item):
        if not self.keywords.has_key(name):
            return []
        kw = self.keywords[name]
        if isinstance(kw, robotapi.UserErrorHandler):
            msg = "Could not create keyword '%s' in testcase '%s'.\n%s"
            msg = msg % (kw.name, item.get_parent_testcase().longname, kw._error)
            raise Exception(msg)
        return kw.keywords


KW_LIB = UserKeywordLibrary()


class AbstractManualModel(object):

    def __init__(self, item, parent=None):
        self.is_modified = False
        self.parent = parent
        self.doc = item.doc
        self.name = item.name
        self.starttime = self.endtime = '00000000 00:00:00.000'
        self.status = self._get_status(item)
        self.visible = True

    def _get_status(self, item):
        """Gets the status correctly from robot.running and robot.output items.
        """
        status = getattr(item, 'status', 'FAIL')
        return status == 'PASS' and 'PASS' or 'FAIL'

    def set_all(self, status, message=None):
        for item in self._get_items():
            item.set_all(status, message)
        self._set_status_and_message(status, message, False)
        self._update_parent()

    def update_status_and_message(self, status=None, message=None):
        self._set_status_and_message(status, message)
        self._update_parent()

    def set_message(self, message):
        message = message.strip()
        if self.message != message:
            self.message = message
            self._mark_data_modified()
            self._update_parent()

    def _set_status_and_message(self, status, message=None, override_default=True):
        if not self.visible:
            return
        if self.status != status:
            self.status = status
            self._mark_data_modified()
        if message is not None:
            if override_default or self.message == self._get_default_message():
                self.set_message(message)
            else:
                self.set_message('%s\n%s' % (message, self.message))

    def _mark_data_modified(self, update_starttime=True):
        DATA_MODIFIED.modified()
        self.is_modified = True
        if update_starttime:
            self.starttime = robotapi.get_timestamp()

    def _update_parent(self):
        if self.parent is not None:
            self.parent._child_status_updated()

    def _child_status_updated(self):
        self._update_status()
        if self.parent is not None:
            self.parent._child_status_updated()

    def _update_status(self):
        child_statuses = [ item.status for item in self._get_items() ]
        updated_status = 'FAIL' in child_statuses and 'FAIL' or 'PASS'
        self._set_status_and_message(updated_status)

    def _save(self, time):
        if self.is_modified:
            self.endtime = time
            self.is_modified = False
        for item in self._get_items():
            item._save(time)

    def has_visible_children(self):
        for item in self._get_items():
            if item.visible:
                return True
        return False

    def get_execution_status(self):
        if self.status == "FAIL" and \
           self.message == self._get_default_message() and \
           'FAIL' not in [ item.get_execution_status() for item in self._get_items() ]:
            return "NOT_EXECUTED"
        return self.status

    def is_suite(self):
        return isinstance(self, ManualSuite)

    def is_test(self):
        return isinstance(self, ManualTest)

    def is_keyword(self):
        return isinstance(self, ManualKeyword)

    def _get_fixture_keyword(self, kw, from_xml):
        if not from_xml:
            kw = kw._keyword
        if kw:
            return ManualKeyword(kw, self, from_xml)
        return None

    def has_same_name(self, other):
        return robotapi.eq(self.name, other.name, ignore=['_'])


class AbstractManualTestOrKeyword(AbstractManualModel):

    def _has_same_keywords(self, other):
        if len(self.keywords) != len(other.keywords):
            return False
        for kw1, kw2 in zip(self.keywords, other.keywords):
            if not (kw1.has_same_name(kw2) and kw1._has_same_keywords(kw2)):
                return False
        return True

    def _add_keywords_results(self, other, add_from_xml, override_method):
        for self_kw, other_kw in zip(self.keywords, other.keywords):
            self_kw.add_results(other_kw, add_from_xml, override_method)

    def _load_other(self, other, override_method):
        if not override_method:
            return True
        if not self._saved_after_loading(other):
            return False
        elif not self.is_modified:
            return True
        elif self == other:
            return False
        return override_method(*self._create_message_for_duplicate_results(other))

    def _get_message_for_different_attrs(self, other):
        s_diffs = ''
        o_diffs = ''
        for attr in self.compare_attrs:
            s_value = getattr(self, attr)
            o_value = getattr(other, attr)
            if type(s_value) is list and type(o_value) is list:
                s_value = ', '.join(s_value)
                o_value = ', '.join(o_value)
            if s_value !=  o_value:
                s_diffs += '%s: %s\n' % (attr.capitalize(), s_value)
                o_diffs += '%s: %s\n' % (attr.capitalize(), o_value)
        return s_diffs, o_diffs

    def _saved_after_loading(self, other):
        elapsed = robotapi.get_elapsed_time(self.endtime, other.endtime)
        return elapsed != '00:00:00.000'

    def _add_info_from_other(self, other):
        self.starttime = other.starttime
        self.endtime = other.endtime
        self.status = other.status
        self.message = other.message
        self.is_modified = False

    def __cmp__(self, other):
        for attr in self.compare_attrs:
            diffs = cmp(getattr(self, attr), getattr(other, attr))
            if diffs != 0:
                return diffs
        return 0

class ManualSuite(robotapi.RunnableTestSuite, AbstractManualModel):

    def __init__(self, suite, parent=None, from_xml=False):
        if not from_xml:
            KW_LIB.add_suite_keywords(suite)
        AbstractManualModel.__init__(self, suite, parent)
        self.longname = suite.longname
        self.metadata = suite.metadata
        self.critical = suite.critical
        self.critical_stats = suite.critical_stats
        self.all_stats = suite.all_stats
        self.setup = self._get_fixture_keyword(suite.setup, from_xml)
        self.teardown = self._get_fixture_keyword(suite.teardown, from_xml)
        self.suites = [ManualSuite(sub_suite, self, from_xml) for sub_suite in suite.suites]
        self.tests = [ManualTest(test, self, from_xml) for test in suite.tests]
        self._update_status()
        self.source = suite.source
        if from_xml:
            self.starttime = suite.starttime
            self.endtime = suite.endtime
        self.saving = False
        self._check_no_duplicate_tests()

    def _check_no_duplicate_tests(self):
        names = [ robotapi.normalize(test.name, ignore=['_']) for test in self.tests ]
        for test in self.tests:
            count = names.count(robotapi.normalize(test.name, ignore=['_']))
            if count > 1:
                msg = "Found test '%s' from suite '%s' %s times.\n"
                msg += "Mabot supports only unique test case names!"
                msg = msg % (test.name, self.longname, count)
                raise IOError(msg)

    def _update_status(self):
        self.message = ''
        robotapi.RunnableTestSuite.set_status(self) # From robot.common.model.BaseTestSuite

    def _add_test_to_stats(self, test):
        #Overrides the method from robot model. Takes the visibility into account.
        if not test.visible and not self.saving:
            return
        robotapi.RunnableTestSuite._add_test_to_stats(self, test)

    def _get_items(self):
        return self.suites + self.tests

    def _set_status_and_message(self, status, message=None, override_default=True):
        self._update_status()

    def get_execution_status(self):
        updated_status = "PASS"
        for item in self._get_items():
            if item.visible:
                status = item.get_execution_status()
                if status == "NOT_EXECUTED":
                    return "NOT_EXECUTED"
                if status == "FAIL":
                    updated_status = "FAIL"
        return updated_status

    def add_results(self, other, add_from_xml=False, override_method=None):
        if not other or not self.has_same_name(other):
            return None
        self._add_from_items_to_items(other.suites, self.suites,
                                      add_from_xml, override_method)
        self._add_from_items_to_items(other.tests, self.tests,
                                      add_from_xml, override_method)
        if self._has_new_children(other):
            self._mark_data_modified(update_starttime=False)
        self._update_status()

    def _add_from_items_to_items(self, other_items, self_items,
                                 add_from_xml, override_method):
        for other_item in other_items:
            item_added = self._add_item_to_items(other_item, self_items,
                                                 add_from_xml, override_method)
            if item_added:
                continue
            elif add_from_xml:
                self_items.append(other_item)
            else:
                # model != XML
                self._mark_data_modified(update_starttime=False)

    def _add_item_to_items(self, other_item, self_items, add_from_xml,
                                  override_method):
        for self_item in self_items:
            if self_item.has_same_name(other_item):
                self_item.add_results(other_item, add_from_xml,
                                  override_method)
                return True
        return False

    def _has_new_children(self, other):
        for suite in self.suites:
            if not self._is_item_in_others(suite, other.suites):
                return True
        for test in self.tests:
            if not self._is_item_in_others(test, other.tests):
                return True
        return False

    def _is_item_in_others(self, item, other_items):
        for other_item in other_items:
            if item.has_same_name(other_item):
                return True
        return False

    def add_tags(self, tags):
        if not self.visible:
            return
        for item in self._get_items():
            item.add_tags(tags)

    def remove_tags(self, tags):
        if not self.visible:
            return
        for item in self._get_items():
            item.remove_tags(tags)

    def update_default_message(self, old_default, new_default):
        if old_default.strip() == new_default.strip():
            return
        for item in self._get_items():
            item.update_default_message(old_default, new_default)

    def save(self):
        self._save(robotapi.get_timestamp())

    def _save(self, time):
        self.saving = True
        for item in self._get_items():
            item._save(time)

    def saved(self):
        self.saving = False
        self._update_status()
        for suite in self.suites:
            suite.saved()

    def get_all_visible_tags(self, tags=None):
        if tags is None:
            tags = []
        if self.visible:
            for item in self._get_items():
                item.get_all_visible_tags(tags)
        return tags

    def change_visibility(self, includes, excludes, tag_name):
        self.visible = False
        for item in self._get_items():
            if item.change_visibility(includes, excludes, tag_name):
                self.visible = True
        self._keep_root_always_visible()
        return self.visible

    def _keep_root_always_visible(self):
        if not self.parent:
            self.visible = True


class ManualTest(robotapi.RunnableTestCase, AbstractManualTestOrKeyword):

    def __init__(self, test, parent, from_xml=False):
        AbstractManualModel.__init__(self, test, parent)
        if from_xml:
            self.starttime = test.starttime
            self.endtime = test.endtime
            self.message = test.message or ""
        else:
            self.message = self._get_default_message()
        self.longname = test.longname
        self.setup = self._get_fixture_keyword(test.setup, from_xml)
        self.teardown = self._get_fixture_keyword(test.teardown, from_xml)
        self.tags = robotapi.normalize_tags(test.tags)
        self.keywords = [ ManualKeyword(kw, self, from_xml) for kw in test.keywords ]
        self.critical = test.critical
        self.timeout = test.timeout
        self.compare_attrs = ['status', 'message', 'tags']

    def _mark_data_modified(self, executed=True):
        AbstractManualModel._mark_data_modified(self)
        if executed:
            self._add_tags_added_to_modified_tests(mark_modified=False)

    def _add_tags_added_to_modified_tests(self, mark_modified):
        self.add_tags(SETTINGS["tags_added_to_modified_tests"],
                      mark_modified=mark_modified)

    def _get_items(self):
        return self.keywords

    def _get_default_message(self):
        return SETTINGS["default_message"]

    def add_results(self, other, add_from_xml, override_method):
        same_keywords = self._has_same_keywords(other)
        if self._load_other(other, override_method) and same_keywords:
            self._add_info_from_other(other)
        if same_keywords:
            self._add_keywords_results(other, add_from_xml, override_method)
        elif add_from_xml:
            self._resolve_keywords_results(other)
        else:
            self._mark_data_modified(executed=False)

    def _add_info_from_other(self, other):
        AbstractManualTestOrKeyword._add_info_from_other(self, other)
        self._add_loaded_tags(other)

    def _resolve_keywords_results(self, other):
        try:
            test = self._load_test_from_datasource()
        except IOError, error:
            msg = 'Could not check correct model from data source!\n%s'
            tkMessageBox('Loading Data Source Failed', msg % (error))
            return
        if not test or test._has_same_keywords(self):
            return
        if test._has_same_keywords(other):
            test = other
        else:
            msg = "Keywords of test '%s' were updated from the data source.\n"
            msg += "Therefore changes made to those keywords could not be saved.\n"
            tkMessageBox('Keywords Reloaded', msg % (self.longname))
        self._add_info_from_other(test)
        self._copy_keywords(test)
        self._mark_data_modified(executed=False)

    def _load_test_from_datasource(self):
        suite = ManualSuite(utils.load_data(self.parent.source, SETTINGS))
        for test in suite.tests:
            if self.has_same_name(test):
                return test

    def _copy_keywords(self, other):
        self.keywords = other.keywords
        for kw in self.keywords:
            kw.parent = self

    def _create_message_for_duplicate_results(self, other):
        s_diffs, o_diffs = self._get_message_for_different_attrs(other)
        message = """Test '%s' updated by someone else!
Your test information:
%s
Other test information:
%s
Do you want your changes to be overridden?"""
        message = message % (self.longname, s_diffs, o_diffs)
        return "Conflicting Test Results!", message

    def _add_loaded_tags(self, other):
        tags = other.tags[:]
        for tag in self.tags:
            if tag not in tags:
                tags.append(tag)
                self._mark_data_modified(executed=False)
        self.tags = sorted(tags)

    def add_tags(self, tags, mark_modified=True):
        if not self.visible:
            return
        for tag in robotapi.normalize_tags(tags):
            self._add_tag(tag, mark_modified)
        self.tags.sort()

    def _add_tag(self, tag, mark_modified):
        if not tag in self.tags:
            self._remove_related_tags_if_allowed_only_once(tag)
            self.tags.append(tag)
            if mark_modified:
                self._mark_data_modified(executed=False)

    def _remove_related_tags_if_allowed_only_once(self, tag):
        for prefix in SETTINGS["tags_allowed_only_once"]:
            if tag.startswith(prefix):
                self._remove_tags_matching_prefix(prefix)

    def _remove_tags_matching_prefix(self, prefix):
        self.remove_tags([tag for tag in self.tags if tag.startswith(prefix)])

    def remove_tags(self, tags):
        if not self.visible:
            return
        for tag in tags:
            self._remove_tag(tag)

    def _remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            self._mark_data_modified(executed=False)

    def update_default_message(self, old_default, new_default):
        if self.message == old_default:
            self.set_message(new_default)

    def get_all_visible_tags(self, tags):
        if self.visible:
            for tag in self.tags:
                if not tag in tags:
                    tags.append(tag)
        return tags

    def change_visibility(self, includes, excludes, tag_name):
        if self.is_included(includes, excludes) and \
           (tag_name == ALL_TAGS_VISIBLE or tag_name in self.tags):
            self.visible = True
        else:
            self.visible = False
        return self.visible

    def _child_status_updated(self):
        self._add_tags_added_to_modified_tests(mark_modified=True)
        AbstractManualTestOrKeyword._child_status_updated(self)


class ManualKeyword (AbstractManualTestOrKeyword):

    def __init__(self, kw, parent, from_xml):
        AbstractManualModel.__init__(self, kw, parent)
        if from_xml:
            self.starttime = kw.starttime
            self.endtime = kw.endtime
            if len(kw.messages) > 0:
                self.messages = kw.messages[:-1]
                self.message = kw.messages[-1].message
                self.msg_timestamp = kw.messages[-1].timestamp
                self.msg_level = kw.messages[-1].level
            else:
                self.messages = []
                self.message = self._get_default_message()
                self.msg_timestamp = self.msg_level = None
            self.keywords = [ ManualKeyword(sub_kw, self, True) for sub_kw in kw.keywords ]
        else:
            self.messages = []
            self.message = ""
            self.msg_timestamp = self.msg_level = None
            self.keywords = [ ManualKeyword(sub_kw, self, False) for sub_kw in KW_LIB.get_keywords(self.name, self) ]
        self.args = kw.args
        self.type = kw.type
        self.timeout = kw.timeout
        self.compare_attrs = ['status', 'message']

    def add_results(self, other, add_from_xml, override_method):
        if self._load_other(other, override_method):
            self._add_info_from_other(other)
        self._add_keywords_results(other, add_from_xml, override_method)

    def get_parent_testcase(self):
        if self.parent.is_test():
            return self.parent
        return self.parent.get_parent_testcase()

    def _get_default_message(self):
        return ''

    def _get_items(self):
        return self.keywords

    def serialize(self, serializer):
        serializer.start_keyword(self)
        for message in self.messages:
            message.serialize(serializer)
        #TODO: In case there are keywords and messages, the order is not kept in here
        #This can happen when reading XML from (p/j)ybot test execution
        if self.message:
            ManualMessage(self.message, self.status, self.msg_timestamp,
                          self.msg_level).serialize(serializer)
        for kw in self.keywords:
            kw.serialize(serializer)
        serializer.end_keyword(self)

    def _create_message_for_duplicate_results(self, other):
        self_diffs, other_diffs = self._get_message_for_different_attrs(other)
        message = """Keyword '%s' updated by someone else in test case '%s'!
Your keyword information:
%s

Other keyword information:
%s

Do you want your changes to be overridden?"""
        message = message % (self.name, self.get_parent_testcase().longname,
                             self_diffs, other_diffs)
        return "Conflicting Keyword Results!", message


class ManualMessage(robotapi.Message):

    def __init__(self, message, status, timestamp=None, level=None):
        self.timestamp = timestamp or '00000000 00:00:00.000'
        status_level = status == 'PASS' and 'INFO' or 'FAIL'
        self.level = level or status_level
        self.message = message
        self.html = False


def get_includes_and_excludes_from_pattern(pattern):
    if pattern == '':
        return [], []
    pattern = pattern.replace('AND', '&')
    ands = []
    nots = []
    if 'NOT' in pattern:
        parts = pattern.split('NOT')
        if '' not in parts:
            ands = [parts[0]]
            nots = parts[1:]
        else:
            nots = ['*']
    else:
        ands = [ pattern ]
    return ands, nots
