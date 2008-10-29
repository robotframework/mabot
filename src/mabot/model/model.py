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

try:
    from robot.running.model import RunnableTestSuite, RunnableTestCase
    from robot.output.readers import Message
    from robot.running.namespace import Namespace
    from robot import utils as robot_utils
except ImportError, error:
    print """All needed Robot modules could not be imported. 
Check your Robot installation."""
    print "Error was: %s" % (error[0])
    sys.exit(1)

from mabot.settings import SETTINGS

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
    """Suite used when initializing the Mabot with no data"""
    
    def __init__(self):
        self.parent = None
        self.doc = self.name = self.starttime = self.endtime = ''
        self.status = self.message = ''
        self.class_type = 'SUITE'
        self.metadata = {}
        self.tests = self.suites = []
    
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

    def get_keywords(self, name):
        if self.keywords.has_key(name):
            return self.keywords[name].keywords
        return []

KW_LIB = UserKeywordLibrary()        

        
class AbstractManualModel:

    def __init__(self, item, parent=None):
        self.is_modified = False
        self.parent = parent
        self.doc = item.doc
        self.name = item.name
        self.starttime = self.endtime = '00000000 00:00:00.000'
        self.status = hasattr(item, 'status') and item.status or 'FAIL'
        #self.status = from_xml and item.status or 'FAIL'
        self.visible = True

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
            
    def _mark_data_modified(self):
        DATA_MODIFIED.modified()
        self.is_modified = True
        self.starttime = robot_utils.get_timestamp()
        
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
        self.class_type = 'SUITE'
        self._update_status()
        if from_xml:
            self.starttime = suite.starttime
            self.endtime = suite.endtime
        self.saving = False
    
    def _update_status(self):
        self.message = ''
        RunnableTestSuite.set_status(self) # From robot.common.model.BaseTestSuite

    def _add_test_to_stats(self, test):
        #Overrides the method from robot model. Takes the visibility into account.
        if not test.visible and not self.saving:
            return
        RunnableTestSuite._add_test_to_stats(self, test)

    def _init_data(self, suite):
        varz = Namespace(suite, None, NoOperationLogger()).variables
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

    def add_results_from_other_suite(self, other_suite):
        if other_suite is None or self.name != other_suite.name:
            return None
        for sub_suite in other_suite.suites:
            for suite in self.suites:
                if suite.name == sub_suite.name:
                    suite.add_results_from_other_suite(sub_suite)
                    break        
        for result_test in other_suite.tests:
            for test in self.tests:
                if test.name == result_test.name:
                    if self._has_same_keywords(test, result_test):
                        self._copy_results_from(test, result_test, self.tests)
                        break
        self._update_status()
                
    def _copy_results_from(self, test1, test2, tests):
        new_test =  ManualTest(test2, self, True)
        print new_test.message
        print new_test.status
        new_test.is_modified = False
        tests[tests.index(test1)] = new_test
    
    def _has_same_keywords(self, item1, item2):
        if len(item1.keywords) != len(item2.keywords):
            return False
        for kw1, kw2 in zip(item1.keywords, item2.keywords):
            if kw1.name.split('.')[-1] != kw2.name.split('.')[-1]:
                return False
            else:
                return self._has_same_keywords(kw1, kw2)
        return True

    def load_new_changes_from_xml(self, other_suite, override_method):
        for sub_suite in other_suite.suites:
            for suite in self.suites:
                if suite.name == sub_suite.name:
                    suite.load_new_changes_from_xml(sub_suite, override_method)
                    break
        for reloaded_test in other_suite.tests:
            for test in self.tests:
                if test.name == reloaded_test.name:
                    if test._update_test(reloaded_test, override_method):
                        print 'Updating The Test'
                        self._copy_results_from(test, reloaded_test, self.tests)
                        break
        print ', '.join([ i.status for i in self.tests ])
        self._update_status()
    
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

    def update_tag(self, old_tag, new_tag):
        if not self.visible:
            return
        for item in self.suites + self.tests:
            item.update_tag(old_tag, new_tag)
    
    def update_default_message(self, old_default, new_default):
        for item in self.suites+self.tests:
            item.update_default_message(old_default, new_default)
        
    def save(self):
        self._save(robot_utils.get_timestamp())
        
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

class ManualTest(RunnableTestCase, AbstractManualModel):

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
        self.class_type = 'TEST'
        self.critical = test.critical
        self.timeout = test.timeout

    def _mark_data_modified(self, executed=True):
        AbstractManualModel._mark_data_modified(self)
        for tag in SETTINGS["additional_tags"]:
            self.add_tag(tag, mark_modified=False)
            
    def _get_items(self):
        return self.keywords

    def _get_default_message(self):
        return SETTINGS["default_message"]

    def add_tag(self, tag, mark_modified=True):
        if not self.visible:
            return
        tag = robot_utils.normalize(tag)
        if not tag in self.tags:
            if mark_modified:
                self._mark_data_modified(False)
            self.tags.append(tag)
 
    def update_tag(self, old_tag, new_tag):
        old_tag = robot_utils.normalize(old_tag)
        new_tag = robot_utils.normalize(new_tag)
        if old_tag in self.tags:
            self._mark_data_modified(False)
            self.tags[self.tags.index(old_tag)] = new_tag
            
    def remove_tag(self, tag):
        if not self.visible:
            return
        tag = robot_utils.normalize(tag)
        if tag in self.tags:
            self._mark_data_modified(False)
            self.tags.remove(tag)
            
    def update_default_message(self, old_default, new_default):
        if self.message == old_default:
            self.set_message(new_default)

    def _update_test(self, reloaded_test, dialog):
        elapsed = robot_utils.get_elapsed_time(self.endtime, reloaded_test.endtime)
        if not self._is_positive_elapsed_time(elapsed):
            return False
        if not self.is_modified and self._is_positive_elapsed_time(elapsed):
            return True
        message = """Test '%s' updated by someone else!
Your test information: 
Status:%s
Message:%s
Tags:%s

Other test information:
Status:%s
Message:%s
Tags:%s

Do you want your changes to be overridden?""" 
        message = message % (self.longname, self.status, self.message, 
                             ', '.join(self.tags), reloaded_test.status, 
                             reloaded_test.message, ', '.join(reloaded_test.tags))
        return_value = dialog("Conflicting Test Results!", message)
        print return_value
        return return_value

    def _is_positive_elapsed_time(self, elapsed):
        return elapsed != '00:00:00.000' and not elapsed.startswith('-')

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


class ManualKeyword (AbstractManualModel):

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
            self.keywords = [ ManualKeyword(kw, self, False) for kw in KW_LIB.get_keywords(self.name) ]
        self.args = kw.args
        self.type = kw.type
        self.class_type = 'KEYWORD'
        self.timeout = kw.timeout

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
        if self.message != '': 
            ManualMessage(self.message, self.status, self.msg_timestamp, 
                          self.msg_level).serialize(serializer)
        for kw in self.keywords:
            kw.serialize(serializer)
        serializer.end_keyword(self)


class ManualMessage(Message):
    
    def __init__(self, message, status, timestamp=None, level=None):
        self.timestamp = timestamp or '00000000 00:00:00.000'
        status_level = status == 'PASS' and 'INFO' or 'FAIL'
        self.level = level or status_level
        #TODO: Convert message to html and set self.html to True
        self.message = message
        self.html = False


class NoOperationLogger:
    
    def __getattr__(self, name):
        return self.noop
    
    def noop(self, *args, **kwargs):
        pass


def get_includes_and_excludes_from_pattern(pattern):
    if pattern == '':
        return [], []
    pattern = pattern.replace('AND', '&')
    ands = []
    nots = []
    if 'NOT' in pattern:
        parts = [ robot_utils.normalize(tag) for tag in pattern.split('NOT') ]
        if '' not in parts:
            ands = [parts[0]]
            nots = parts[1:]
        else:
            nots = ['*']
    else:
        ands = [ robot_utils.normalize(pattern) ]
    return ands, nots
