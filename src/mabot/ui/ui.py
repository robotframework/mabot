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

class TextMessageDialog(AbstractTkDialog):

    def __init__(self, parent, title, comment, height=5, width=40, message=""):
        self.message = message
        self.comment = comment
        self.width=width
        self.height=height
        AbstractTkDialog.__init__(self, parent, title)

    def body(self, master):
        Label(master, text=self.comment).grid(row=0)
        self.message_field = Text(master, height=self.height, width=self.width)
        self.message_field.insert(START, self.message)
        self.message_field.grid(row=1)
        return self.message_field # initial focus

    def apply(self):
        self.message = self.message_field.get(START, END)
    
    def validate(self):
        return self.message_field.get(START, END) != ''

class EntryDialog(AbstractTkDialog):

    def __init__(self, parent, title, label, default_message=""):
        self._label = label
        self._default_message = default_message
        AbstractTkDialog.__init__(self, parent, title)

    def body(self, master):
        Label(master, text=self._label).grid(row=0, sticky=W+E)
        self._entry = Entry(master)
        self._entry.insert(0, self._default_message)
        self._entry.grid(row=1, sticky=W+E)
        return self._entry # initial focus

    def apply(self):
        self.message = self._entry.get()
    
    def validate(self):
        return self._entry.get() != ''


class SettingsDialog(AbstractTkDialog):

    def __init__(self, parent, title):
        self.new_settings = None      
        AbstractTkDialog.__init__(self, parent, title)
    
    def body(self, master):
        self._default_message(master, 0)
        self._ask_additional_tags_at_startup(master, 1)
        self._addition_tags_for_executed_test(master, 2)
        self._info_label(master, 3)
        self._always_load_old_data_from_xml(master, 4)
        self._check_simultaneous_save(master, 5)
        self._include(master, 6)
        self._exclude(master, 7)

    def _info_label(self, master, row):
        text = "\nSettings below will affect after loading new data\n"
        Label(master, text=text).grid(row=row, column=0)
        
    def _default_message(self, master, row):
        Label(master, text="Default Message:").grid(row=row, column=0, sticky=NW)
        self.default_message = Text(master, height=10, width=50)
        self.default_message.insert(START, SETTINGS["default_message"])
        self.default_message.grid(row=row, column=1)

    def _ask_additional_tags_at_startup(self, master, row):
        self.ask_additional_tags_at_startup = self._create_radio_buttons(master, 
            "Ask Additional Tags at Start Up:", SETTINGS["ask_additional_tags_at_startup"], row)

    def _addition_tags_for_executed_test(self, master, row):
        self.addition_tags = self._create_entry(master, "Additional Tags (i.e. executed-by-x, build-y):", 
                                                ', '.join(SETTINGS["additional_tags"]), row)

    def _always_load_old_data_from_xml(self, master, row):
        self.always_load_old_data_from_xml = self._create_radio_buttons(master, 
            "Always Load Old Data from Xml:", SETTINGS["always_load_old_data_from_xml"], row)
    
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
        Label(master, text=title).grid(row=row, column=0, sticky=NW)
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
        Label(master, text=header).grid(row=row, column=0, sticky=NW)
        entry = Entry(master, width=50)
        entry.insert(0, value)
        entry.grid(row=row, column=1)
        return entry
    
    def apply(self):
        ask_additional_tags = self._get_boolean(self.ask_additional_tags_at_startup)
        additional_tags = self._get_tags(self.addition_tags)
        load_always = self._get_boolean(self.always_load_old_data_from_xml)
        check_simultaneous = self._get_boolean(self.check_simultaneous_save)
        include = self._get_tags(self.include)
        exclude = self._get_tags(self.exclude)
        self.new_settings = {"default_message":self.default_message.get(START, END).strip(),
                            "ask_additional_tags_at_startup":ask_additional_tags, 
                            "additional_tags":additional_tags,
                            "always_load_old_data_from_xml":load_always,
                            "check_simultaneous_save":check_simultaneous,
                            "include":include,
                            "exclude":exclude,
                            }

    def _get_boolean(self, item):
        return item.get() == "True" and True or False

    def _get_tags(self, field):
        return utils.get_tags_from_string(field.get())
    
    def validate(self):
        return self.default_message.get(START, END) != ''
    
        
class ChangeStatusDialog(TextMessageDialog):

    def __init__(self, parent):
        TextMessageDialog.__init__(self, parent, "Set Failed",
                                   "Give reason for failure:" , 5, 50, 
                                   SETTINGS["default_message"])

class AddTagsDialog(EntryDialog):

    def __init__(self, parent):
        EntryDialog.__init__(self, parent, "Add Tags",
                                   "Give tags (i.e. tag1, tag2)")
    
    def apply(self):
        EntryDialog.apply(self)
        self.tags = utils.get_tags_from_string(self.message)

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


class AskAdditionalTagsDialog(TextMessageDialog):

    def __init__(self, parent, data):
        label = """Give tag(s) that you want to add to all the test cases
you are going to report (i.e. env-x, build-y):"""
        TextMessageDialog.__init__(self, parent, "Additional Tags", label,
                                   1, 50, data)


class CommonFrame(Frame):

    def __init__(self, master, **cnf):
        Frame.__init__(self, master, background='white', **cnf)

