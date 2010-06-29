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


from Tkinter import *
from idlelib import TreeWidget
import os

from mabot.utils import get_status_color

TreeWidget.ICONDIR = os.path.join(os.path.dirname(__file__), 'icons')


class Node(TreeWidget.TreeNode):

    def __init__(self, canvas, parent, item, root=None):
        self.root = root
        TreeWidget.TreeNode.__init__(self, canvas, parent, item)
        self.label = ForeGroundLabel(self.canvas,
                                     get_status_color(self.item.model_item),
                                     text=self.item.GetText(), bd=0, padx=2,
                                     pady=2)

    def select(self, event=None):
        TreeWidget.TreeNode.select(self, event)
        if self.root is not None:
            self.root.notify_select(self)
        else:
            parent = self.parent
            while parent is not None:
                if parent.root is not None:
                    parent.root.notify_select(self)
                    break
                parent = parent.parent

    def drawtext(self):
        self.label.update_foreground(get_status_color(self.item.model_item))
        TreeWidget.TreeNode.drawtext(self)


class ForeGroundLabel(Label):

    def __init__(self, master, foreground, **cnf):
        self.foreground = foreground
        Label.__init__(self, master, cnf)

    def update_foreground(self, foreground):
        self.foreground = foreground
        Label.configure(self, {'foreground':self.foreground})

    def configure(self, cnf):
        Label.configure(self, cnf)
        Label.configure(self, {'foreground':self.foreground})

class _RobotTreeItem(TreeWidget.TreeItem):

    def __init__(self, item):
        self.model_item = item
        self.children = self._get_children()
        self.label = self._get_label()

    def GetText(self):
        return self.label

    def GetSubList(self):
        return self.children

    def IsExpandable(self):
        return self.model_item.has_visible_children()


class SuiteTreeItem(_RobotTreeItem):

    def _get_children(self):
        if self._only_one_visible_folder_suite_child(self.model_item):
            visible_suite = [s for s in self.model_item.suites if s.visible ][0]
            return SuiteTreeItem(visible_suite)._get_children()
        children = []
        for suite in self.model_item.suites:
            if suite.visible:
                children.append(SuiteTreeItem(suite))
        for test in self.model_item.tests:
            if test.visible:
                children.append(TestTreeItem(test))
        return children

    def GetIconName(self):
        if self.model_item.tests:
            return 'file_suite'
        return 'dir_suite'

    def _only_one_visible_folder_suite_child(self, item):
        return len([s for s in item.suites if s.visible ]) == 1 \
               and not item.suites[0].tests

    def _get_label(self):
        names = []
        self._get_suite_names_with_one_suite_child(self.model_item, names)
        return '/'.join(names)

    def _get_suite_names_with_one_suite_child(self, item, names):
        names.append(item.name)
        if self._only_one_visible_folder_suite_child(item):
            return self._get_suite_names_with_one_suite_child(item.suites[0], names)
        return names


class _AbstractTestAndKWItem(_RobotTreeItem):

    def _get_label(self):
        return self.model_item.name

    def _get_children(self):
        return [ KeywordTreeItem(kw) for kw in self.model_item.keywords ]


class TestTreeItem(_AbstractTestAndKWItem):

    def GetIconName(self):
        return 'test'


class KeywordTreeItem(_AbstractTestAndKWItem):

    def GetIconName(self):
        return 'keyword'
