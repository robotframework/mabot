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
import sys
import tkMessageBox

try:
    from robot.common import UserErrorHandler
    from robot.running.model import RunnableTestSuite, RunnableTestCase
    from robot.output.readers import Message
    from robot.running.namespace import Namespace
except ImportError, error:
    print """All needed Robot modules could not be imported. 
Check your Robot installation."""
    print "Error was: %s" % (error[0])
    sys.exit(1)

from mabot.settings import SETTINGS
from mabot import utils

class Modified:
    
    def __init__(self):
        self.status = False
    
    def modified(self):
        self.status = True
    
    def saved(self):
        self.status = False
    
    def set(self, status):
        self.status = status

    def is_modified(self):
        return self.status


DATA_MODIFIED = Modified()

ALL_TAGS_VISIBLE = "ALL MATCHING TAGS VISIBLE"

class EmptySuite:
    """Suite used when initializing the Mabot with no data"""
    
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
        if isinstance(kw, UserErrorHandler):
            msg = "Could not create keyword '%s' in testcase '%s'.\n%s"
            msg = msg % (kw.name, item.get_parent_testcase().longname, kw._error)
            raise Exception(msg)
        return kw.keywords
        

KW_LIB = UserKeywordLibrary()        

        
class AbstractManualModel:

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
        
        Works also with changes done to Robot Framework 2.0.3.
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
    
    def _set_status_and_message(self, status, message=None, override_default=True):
        if not self.visible:
            return 
        if self.status != status:
            self.status = status
            self._mark_data_modified()
        if message is not None:
            if override_default or self.message == self._get_default_message():
                self.set_message(message)
            
    def _mark_data_modified(self, update_starttime=True):
        DATA_MODIFIED.modified()
        self.is_modified = True
        if update_starttime:
            self.starttime = utils.get_timestamp()
        
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


class AbstractManualTestOrKeyword(AbstractManualModel):

    def _has_same_keywords(self, other):
        if len(self.keywords) != len(other.keywords):
            return False
        for kw1, kw2 in zip(self.keywords, other.keywords):
            if kw1.name != kw2.name or not kw1._has_same_keywords(kw2):
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
        return override_method(*self._create_message_for_duplicate_results(other))

    def _saved_after_loading(self, other):
        elapsed = utils.get_elapsed_time(self.endtime, other.endtime)
        return elapsed != '00:00:00.000'

    def _add_info_from_other(self, other):
        self.starttime = other.starttime
        self.endtime = other.endtime
        self.status = other.status
        self.message = other.message
        self.is_modified = False


class ManualSuite(RunnableTestSuite, AbstractManualModel):
    
    def __init__(self, suite, parent=None, from_xml=False):
        if not from_xml:
            KW_LIB.add_suite_keywords(suite)
        if not from_xml:
            suite = self._init_data(suite)
        AbstractManualModel.__init__(self, suite, parent)
        self.mediumname = suite.mediumname
        self.longname = suite.longname
        self.metadata = suite.metadata
        self.critical = suite.critical
        self.filtered = suite.filtered
        self.critical_stats = suite.critical_stats
        self.all_stats = suite.all_stats
        self.setup = suite.setup
        self.teardown = suite.teardown
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
        names = [ test.name for test in self.tests ]
        for test in self.tests:
            if names.count(test.name) > 1:
                msg = "Found test '%s' from suite '%s' %s times.\n"
                msg += "Mabot supports only unique test case names!"
                msg = msg % (test.name, self.longname, names.count(test.name)) 
                raise IOError(msg)

    def _update_status(self):
        self.message = ''
        RunnableTestSuite.set_status(self) # From robot.common.model.BaseTestSuite

    def _add_test_to_stats(self, test):
        #Overrides the method from robot model. Takes the visibility into account.
        if not test.visible and not self.saving:
            return
        RunnableTestSuite._add_test_to_stats(self, test)

    def _init_data(self, suite):
        varz = Namespace(suite, None, utils.LOGGER).variables
        suite._init_suite(varz)
        for test in suite.tests:
            test._init_test(varz)
        return suite
        
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
        if not other or self.name != other.name:
            return None
        self._add_from_items_to_items(other.suites, self.suites, 
                                      add_from_xml, override_method)
        self._add_from_items_to_items(other.tests, self.tests, 
                                      add_from_xml, override_method)
        if self._has_new_children(other):
            self._mark_data_modified(False)                        
        self._update_status()

    def _add_from_items_to_items(self, other_items, self_items, 
                                 add_from_xml, override_method):
        for other_item in other_items:
            if other_item.name in [ i.name for i in self_items ]:
                for self_item in self_items:
                    if self_item.name == other_item.name:
                        self_item.add_results(other_item, add_from_xml,
                                          override_method)
                        break
            elif add_from_xml:
                self_items.append(other_item) 
            else:
                # model != XML
                self._mark_data_modified(False)                           
    
    def _has_new_children(self, other):
        for suite in self.suites:
            if not suite.name in [ s.name for s in other.suites ]:
                return True
        for test in self.tests:
            if not test.name in [ s.name for s in other.tests ]:
                return True
        return False            

    def add_tag(self, tag):
        if not self.visible:
            return
        for item in self._get_items():
            item.add_tag(tag)

    def remove_tag(self, tag):
        if not self.visible:
            return
        for item in self._get_items():
            item.remove_tag(tag)
    
    def update_default_message(self, old_default, new_default):
        for item in self.suites+self.tests:
            item.update_default_message(old_default, new_default)
        
    def save(self):
        self._save(utils.get_timestamp())
        
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
        if not tags:
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
        if not self.parent: #Keeps the root always visible
            self.visible = True
        return self.visible

class ManualTest(RunnableTestCase, AbstractManualTestOrKeyword):

    def __init__(self, test, parent, from_xml=False):
        AbstractManualModel.__init__(self, test, parent)
        if from_xml:
            self.starttime = test.starttime
            self.endtime = test.endtime
            self.message = test.message or ""
        else:
            self.message = self._get_default_message()
        self.mediumname = test.mediumname
        self.longname = test.longname
        self.setup = test.setup
        self.teardown = test.teardown
        self.tags = test.tags
        self.keywords = [ ManualKeyword(kw, self, from_xml) for kw in test.keywords ]
        self.critical = test.critical
        self.timeout = test.timeout

    def _mark_data_modified(self, executed=True):
        AbstractManualModel._mark_data_modified(self)
        if executed:
            for tag in SETTINGS["additional_tags"]:
                self.add_tag(tag, mark_modified=False)
            
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
            self._mark_data_modified(False)

    def _add_info_from_other(self, other):
        AbstractManualTestOrKeyword._add_info_from_other(self, other)
        self._add_loaded_tags(other)

    def _resolve_keywords_results(self, other):
        try:
            test = self._load_test_from_datasource()
        except IOError, message:
            msg = 'Could not check correct model from data source!\n%s'
            tkMessageBox('Loading Data Source Failed', msg % (error))
            return
        if test._has_same_keywords(self):
            return
        if test._has_same_keywords(other):
            test = other
        else:
            msg = "Keywords of test '%s' were updated from the data source.\n"
            msg += "Therefore changes made to those keywords could not be saved.\n"
            tkMessageBox('Keywords Reloaded', msg % (self.longname))
        self._add_info_from_other(test)
        self._copy_keywords(test)
        self._mark_data_modified(False)

    def _load_test_from_datasource(self):
        suite = ManualSuite(utils.load_data(self.parent.source, SETTINGS))
        for test in suite.tests:
            if test.name == self.name:
                return test            

    def _copy_keywords(self, other):
        self.keywords = other.keywords
        for kw in self.keywords:
            kw.parent = self

    def _create_message_for_duplicate_results(self, other):
        message = """Test '%s' updated by someone else!
Your test information:
Status: %s
Message: %s
Tags: %s

Other test information:
Status: %s
Message: %s
Tags: %s

Do you want your changes to be overridden?"""
        message = message % (self.longname, self.status, self.message, 
                             ', '.join(self.tags), other.status, 
                             other.message, ', '.join(other.tags))
        return "Conflicting Test Results!", message
    

    def _add_loaded_tags(self, other):
        tags = other.tags[:]
        for tag in self.tags:
            if tag not in tags:
                tags.append(tag)
                self._mark_data_modified(False)
        self.tags = sorted(tags)

    def add_tag(self, tag, mark_modified=True):
        if not self.visible:
            return
        tag = utils.normalize(tag)
        if not tag in self.tags:
            self.tags.append(tag)
            self.tags.sort()
            if mark_modified:
                self._mark_data_modified(False)
             
    def remove_tag(self, tag):
        if not self.visible:
            return
        tag = utils.normalize(tag)
        if tag in self.tags:
            self.tags.remove(tag)
            self._mark_data_modified(False)
            
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
            self.keywords = [ ManualKeyword(kw, self, False) for kw in KW_LIB.get_keywords(self.name, self) ]
        self.args = kw.args
        self.type = kw.type
        self.timeout = kw.timeout

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
        message = """Keyword '%s' updated by someone else in test case '%s'!
Your keyword information:
Status: %s
Message: %s

Other keyword information:
Status: %s
Message: %s

Do you want your changes to be overridden?"""
        message = message % (self.name, self.get_parent_testcase().longname, 
                             self.status, self.message, other.status, other.message)
        return "Conflicting Keyword Results!", message


class ManualMessage(Message):
    
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
        parts = [ utils.normalize(tag) for tag in pattern.split('NOT') ]
        if '' not in parts:
            ands = [parts[0]]
            nots = parts[1:]
        else:
            nots = ['*']
    else:
        ands = [ utils.normalize(pattern) ]
    return ands, nots
