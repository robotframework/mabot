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

from abstracttkdialog import AbstractTkDialog

from mabot.settings import SETTINGS
from mabot import utils

START = 1.0

class SettingsDialog(AbstractTkDialog):

    def __init__(self, parent, title):
        self.new_settings = None      
        AbstractTkDialog.__init__(self, parent, title)
    
    def body(self, master):
        methods = [ self._default_message,
                    self._ask_tags_added_to_modified_tests_at_startup,
                    self._tag_info_label,
                    self._addition_tags_for_executed_test,
                    self._tags_allowed_only_once,
                    self._info_label,
                    self._always_load_old_data_from_xml,
                    self._check_simultaneous_save,
                    self._include,
                    self._exclude ]
        for index, method in enumerate(methods):
            method(master, index)

    def _info_label(self, master, row):
        text = "\nSettings below will affect after loading new data\n"
        self._label(master, row, text)

    def _tag_info_label(self, master, row):
        text = "Note: In all tag related settings separator is comma and space ', '."
        self._label(master, row, text)

    def _label(self, master, row, text):
        Label(master, text=text).grid(row=row, column=0, sticky='NW')
        
    def _default_message(self, master, row):
        Label(master, text="Default Message:").grid(row=row, column=0, sticky=NW)
        self.default_message = Text(master, height=10, width=50)
        self.default_message.insert(START, SETTINGS["default_message"])
        self.default_message.grid(row=row, column=1)

    def _ask_tags_added_to_modified_tests_at_startup(self, master, row):
        self.ask_tags_added_to_modified_tests_at_startup = self._create_radio_buttons(master, 
            "Ask Tags Added to Modified Tests at Start Up:", SETTINGS["ask_tags_added_to_modified_tests_at_startup"], row)

    def _addition_tags_for_executed_test(self, master, row):
        self.addition_tags = self._create_entry(master, "Tags Added to Modified Tests (i.e. executed-by-x, build-y):", 
                                                ', '.join(SETTINGS["tags_added_to_modified_tests"]), row)

    def _tags_allowed_only_once(self, master, row):
        self.tags_allowed_only_once = self._create_entry(master, "Tags allowed only once (i.e. executed-by-, build-):", 
                                                ', '.join(SETTINGS["tags_allowed_only_once"]), row)

    def _always_load_old_data_from_xml(self, master, row):
        self.always_load_old_data_from_xml = self._create_radio_buttons(master, 
            "Always Load Old Data from XML:", SETTINGS["always_load_old_data_from_xml"], row)
    
    def _check_simultaneous_save(self, master, row):
        self.check_simultaneous_save = self._create_radio_buttons(master, 
            "Check Simultaneous Save:", SETTINGS["check_simultaneous_save"], row)

    def _include(self, master, row):
        title="Include Tags (i.e. smoke, manual);"
        self.include = self._create_entry(master, title, 
                                          ', '.join(SETTINGS["include"]), row)

    def _exclude(self, master, row):
        title = "Exclude Tags (i.e. not-ready, some-other):"
        self.exclude = self._create_entry(master, title, 
                                          ', '.join(SETTINGS["exclude"]), row)

    def _create_radio_buttons(self, master, title, value, row):
        self._label(master, row, title)
        variable = StringVar()
        variable.set(value)
        radio_buttons_container = CommonFrame(master)
        radio_buttons_container.grid(row=row, column=1, sticky=W)
        Radiobutton(radio_buttons_container, text="ON", value=True,
                    variable=variable).grid(row=0, column=0)
        Radiobutton(radio_buttons_container, text="OFF", value=False, 
                    variable=variable).grid(row=0, column=1)
        return variable

    def _create_entry(self, master, header, value, row):
        self._label(master, row, header)
        entry = Entry(master, width=50)
        entry.insert(0, value)
        entry.grid(row=row, column=1)
        return entry
    
    def apply(self):
        ask_tags_added_to_modified_tests = self._get_boolean(self.ask_tags_added_to_modified_tests_at_startup)
        tags_added_to_modified_tests = self._get_tags(self.addition_tags)
        tags_allowed_only_once = self._get_tags(self.tags_allowed_only_once)
        load_always = self._get_boolean(self.always_load_old_data_from_xml)
        check_simultaneous = self._get_boolean(self.check_simultaneous_save)
        include = self._get_tags(self.include)
        exclude = self._get_tags(self.exclude)
        self.new_settings = {"default_message":self.default_message.get(START, END).strip(),
                            "ask_tags_added_to_modified_tests_at_startup":ask_tags_added_to_modified_tests, 
                            "tags_allowed_only_once":tags_allowed_only_once,
                            "tags_added_to_modified_tests":tags_added_to_modified_tests,
                            "always_load_old_data_from_xml":load_always,
                            "check_simultaneous_save":check_simultaneous,
                            "include":include,
                            "exclude":exclude,
                            }

    def _get_boolean(self, item):
        value = item.get()
        if value == "True" or value == "1":
            return True
        return False

    def _get_tags(self, field):
        return utils.get_tags_from_string(field.get())
    
    def validate(self):
        return True
    
        
class ChangeStatusDialog(AbstractTkDialog):

    def __init__(self, parent):
        AbstractTkDialog.__init__(self, parent, "Set Failed")

    def body(self, master):
        Label(master, text="Give reason for failure:").pack(fill=BOTH)
        scrollbar = Scrollbar(master, orient=VERTICAL)
        self.message_field = Text(master, yscrollcommand=scrollbar.set)
        self.message_field.insert(START, SETTINGS["default_message"])
        scrollbar.config(command=self.message_field.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.message_field.pack(fill=BOTH, expand=1)
        return self.message_field # initial focus

    def apply(self):
        self.message = self.message_field.get(START, END).strip()
    
    def validate(self):
        return self.message_field.get(START, END).strip() != ''


class RemoveTagsDialog(AbstractTkDialog):

    def __init__(self, parent, tags):
        self._all_tags = tags
        self.tags = []
        AbstractTkDialog.__init__(self, parent, 'Remove Tags')
        
    def body(self, master):
        scrollbar = Scrollbar(master, orient=VERTICAL)
        self.listbox = Listbox(master, selectmode=EXTENDED, 
                               yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.listbox.pack(fill=BOTH, expand=1)
        for tag in self._all_tags:
            self.listbox.insert(END, tag)

    def validate(self):
        return self.listbox.curselection()

    def apply(self):
        self.tags = [ self._all_tags[int(i)] for i in self.listbox.curselection() ]


class CommonFrame(Frame):

    def __init__(self, master, **cnf):
        Frame.__init__(self, master, background='white', **cnf)

