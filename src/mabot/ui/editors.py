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


import re
from Tkinter import *
import webbrowser

from ui import *

START = 1.0

def Editor(master, tree_item):
    editor_type = tree_item.item.model_item.class_type
    if editor_type == 'SUITE':
        return SuiteEditor(master, tree_item)
    elif editor_type == 'TEST':
        return TestEditor(master, tree_item)
    elif editor_type == 'KEYWORD':
        return KeywordEditor(master, tree_item)

class AbstractEditor:
        
    def __init__(self, master, tree_item):
        self._tree_item = tree_item
        self._model_item = self._tree_item.item.model_item
        self._current_row = 0
        self._editor = CommonFrame(master)
        self._init_data(self._editor)
        self._editor.pack(fill=BOTH)

    def _create_name(self, master):
        self._create_title_and_data(master, self._class_type, 
                                    self._model_item.name)

    def _create_documentation(self, master):
        if self._model_item.doc:
            self._create_title_and_data(master, "Documentation", 
                                        self._model_item.doc)

    def _create_status(self, master):
        row = CommonFrame(master)        
        TitleLabel(row, "Status")
        self._create_status_radio_buttons(row).pack(side=LEFT, expand=1, anchor=W)
        row.pack(fill=BOTH, expand=1, anchor=W)
        
    def _create_status_radio_buttons(self, master):
        frame = CommonFrame(master)
        self._status = StringVar()
        self._status.set(self._model_item.status)
        Radiobutton(frame, foreground='green', text="PASS", 
                    variable=self._status, value="PASS",
                    command=lambda: self._set_status('PASS'),
                    background='white').pack(side=LEFT, expand=1)
        Radiobutton(frame, foreground='red', text="FAIL", 
                    variable=self._status, value="FAIL",
                    command=lambda: self._set_status('FAIL'),
                    background='white').pack(side=LEFT, expand=1)
        return frame

    def _create_title_and_data(self, master, title, data, **datacnf):
        row = CommonFrame(master)
        TitleLabel(row, title)
        DataLabel(row, data, **datacnf)
        row.pack(fill=BOTH, expand=1, anchor=N+W)
        
    def _create_message(self, master):
        row = CommonFrame(master)
        TitleLabel(row, "Message")
        scrollbar_y = Scrollbar(row, orient=VERTICAL)
        scrollbar_y.pack(side=RIGHT, fill=Y, expand=1)
        scrollbar_x = Scrollbar(row, orient=HORIZONTAL)
        scrollbar_x.pack(side= BOTTOM, fill=X, expand=1)
        self._message_field = DataLabel(row, 
                                        self._model_item.message, editable=True, 
                                        yscrollcommand=scrollbar_y.set,
                                        xscrollcommand=scrollbar_x.set)
        self._message_field.bind('<Key>', self._save_message)
        #This should make sure that all the data is saved.
        self._message_field.bind('<Leave>', self._save_message)
        scrollbar_y.config(command=self._message_field.yview)
        scrollbar_x.config(command=self._message_field.xview)
        row.pack(fill='both')
        
    def _create_times(self, master):
        times = self._model_item.starttime[:-4] + ' / ' + self._model_item.endtime[:-4]
        self._create_title_and_data(master, "Modified / Saved:", times)

    def _save_message(self, event):
        self._model_item.set_message(self._get_message())
        self._tree_item.update()
            
    def update(self):
        self._message_field.delete(START, END)
        self._message_field.insert(START, self._model_item.message)
        self._status.set(self._model_item.status)
    
    def _set_status(self, status):
        self._model_item.update_status_and_message(status, self._get_message())
        self._tree_item.update()
        self.update()
                    
    def _get_message(self):
        return self._message_field.get(START, END)
        
    def close(self):
        self._editor.destroy()

class TitleLabel(Label):
    
    def __init__(self, master, text, **cnf):
        text = text + ' '*(14-len(text))
        Label.__init__(self, master, text=text, font=('Courier', 8, 'bold'), 
                       background='white', **cnf)
        Label.pack(self, expand=1, anchor=W)


class DataLabel(Text):

    def __init__(self, master, text, editable=False, **cnf):
        self.editable = editable
        text_parts = get_text_parts(text)
        border = self.editable and 1 or 0
        width = 80
        height = self.editable and 30 or get_height(text, width)
        wrap = not self.editable and WORD or NONE 
        Text.__init__(self, master, border=border, width=width,
                      font=('Courier', 8), height=height,  wrap=wrap, **cnf)
        self.tag_config("normal", font=('Courier', 8))
        self.tag_config("bold", font=('Courier', 8, 'bold'))
        self.tag_config("italic", font=('Courier', 8, 'italic'))
        self._insert_to_field(text_parts)
        if not self.editable:
            self.config(state=DISABLED, cursor="arrow")
        Text.pack(self)

    def insert_to_field(self, text): 
        """Update only content, no size."""
        self._insert_to_field(get_text_parts(text))

    def _insert_to_field(self, text_parts):
        link_number = 0
        for text, type in text_parts:
            modified_type = type
            if type == 'link':
                modified_type = "link_%d" % (link_number)
                self.tag_config(modified_type, foreground="blue", underline=1)
                self.tag_bind(modified_type,"<Button-1>", 
                              OpenLink(text, type).launch)
                link_number +=1
            self.insert(INSERT, text, modified_type)

    def update_field(self, text):
        if not self.editable:
            self.config(state=NORMAL)
        self.delete(START, END)
        self.insert_to_field(text)
        if not self.editable:
            self.config(state=DISABLED)
    
class SuiteEditor(AbstractEditor):
    
    def __init__(self, master, tree_item):
        self._class_type = 'Test Suite'
        AbstractEditor.__init__(self, master, tree_item)

    def _init_data(self, editor):
        self._create_name(editor)
        self._create_documentation(editor)
        self._create_metadata(editor)
        self._create_status(editor)
        self._create_message(editor)

    def _create_status(self, master):
        row = CommonFrame(master)
        TitleLabel(row, "Status")
        self._status_field = DataLabel(row, self._model_item.status, 
                                       foreground=get_status_color(self._model_item))
        row.pack(fill='both')

    def _create_metadata(self, master):
        for key, value in self._model_item.metadata.items():
            self._create_title_and_data(master, key, value)

    def _create_message(self, master):
        row = CommonFrame(master)
        TitleLabel(row, "Message")
        self._message_field = DataLabel(row, self._model_item.get_full_message())
        row.pack(fill='both')

    def update(self):
        self._message_field.update_field(self._model_item.message)
        self._status_field.configure(foreground=get_status_color(self._model_item))
        self._status_field.update_field(self._model_item.status)

        
class TestEditor(AbstractEditor):

    def __init__(self, master, tree_item):
        self._class_type = 'Test Case'
        AbstractEditor.__init__(self, master, tree_item)

    def _init_data(self, editor):
        self._create_name(editor)
        self._create_documentation(editor)
        self._create_tags(editor)
        self._create_status(editor)
        self._create_message(editor)
        self._create_times(editor)

    def _create_tags(self, master):
        self._create_title_and_data(master, "Tags", 
                                    ', '.join(self._model_item.tags))


class KeywordEditor(AbstractEditor):

    def __init__(self, master, tree_item):
        self._class_type = 'Keyword'
        AbstractEditor.__init__(self, master, tree_item)

    def _init_data(self, editor):
        self._create_name(editor)
        self._create_documentation(editor)
        self._create_status(editor)
        self._create_message(editor)
        self._create_times(editor)

    def _create_name(self, master):
        step = self._model_item.name
        s = ''
        if self._model_item.args:
            s = 's'
            step += '\n\n' + '\n\n'.join(self._model_item.args)
        self._create_title_and_data(master, 'Step'+s, step)

        
link = '(file|https?)://[^ ]*'
bold = '(\s|^)\*.*?\*(\s|$)'
italic = '(\s|^)_.*?_(\s|$)'
item = re.compile(".*?(%s|%s|%s).*" %(link, bold, italic), re.IGNORECASE)

searches = [(link, 'link'), (italic, 'italic'), (bold, 'bold')]


def get_text_parts(text):
    match = re.search(item, text)
    if match is None:
        return ((text, 'normal'),)
    else:
        return _create_tuple(text, match, _get_type(match))

    
def _get_type(match):
    content = match.groups()[0]
    for regexp, type in searches:
        if re.match(regexp, content, re.DOTALL+re.IGNORECASE) is not None:
            return type


def _create_tuple(text, match, type):    
    content = match.groups()[0]
    items = []
    found =False
    for item in text.partition(content):
        if item == '':
            continue
        if item is content:
            if type == 'bold' or type == 'italic':
                result = ''
                if not item[0] in ['*', '_']: 
                    result += item[0] + item[2:-2]
                else:
                    result += item[1:-2]
                if not item[-1] in ['*', '_']:
                    result += item[-1]
                else:
                    result += item[-2]
                item = result
            items.append((item, type))
            found = 'True'
        else:
            if found:
                items.extend(get_text_parts(item))
            else:
                items.append((item, 'normal'))
    return tuple(items)


def get_height(text, width):
    lines = text.splitlines()
    line_count = len(lines)
    for line in lines:
        if len(line) > width:
            row_lenght = 0
            for word in line.split():
                if (row_lenght + len(word)) > width:
                    line_count += 1
                    row_lenght = 0
                if len(word) > width:
                    line_count += len(word) / width
                    row_lenght = len(word) % width + 1
                else:
                    row_lenght += len(word) + 1
    return line_count + 2


class OpenLink:
    
    def __init__(self, content, type):
        self.content = content
        self.type = type
                
    def launch(self, event):
        webbrowser.open(self.content)


def get_status_color(item):
    colours = {"PASS":"green", "FAIL":"red", "NOT_EXECUTED":"black"}
    return colours[item.get_execution_status()]
