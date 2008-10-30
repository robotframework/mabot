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
from Tkinter import _setit
import tkMessageBox
import tkFileDialog
from idlelib import TreeWidget

from tree import SuiteTreeItem
from tree import Node

from mabot.settings import SETTINGS
from mabot.model.io import IO
from mabot.model.model import DATA_MODIFIED
from mabot.model.model import ALL_TAGS_VISIBLE
from mabot.model.model import get_includes_and_excludes_from_pattern
from mabot.version import version

from editors import Editor
from editors import SuiteEditor
from ui import *


class Mabot:
    
    def __init__(self, datasource, options):
        self.root = Tk()
        self.suite = None
        self._save_options(options)
        self.io = IO(tkMessageBox.askyesno) 
        self._load_data_and_create_ui(datasource)
        self._ask_additional_tags()
        self.root.mainloop()

    def _save_options(self, options):
        if options['include']:
            SETTINGS['include'] = options['include']
        if options['exclude']:
            SETTINGS['exclude'] = options['exclude']
        if options['include'] or options['exclude']:
            SETTINGS.save_settings()

    def _load_data_and_create_ui(self, datasource):
        try:
            self.suite = self.io.load_data(datasource)
        except Exception, error:
            tkMessageBox.showerror('Loading Failed!', error[0])
            if self.suite:
                return
            self.suite = self.io.load_data(None)
        self._create_root()
        self._create_menu()
        self._create_middle_window()
        self._create_statusbar(self.root)

    def _ask_additional_tags(self):
        if not SETTINGS['ask_additional_tags_at_startup']:
            return
        dialog = AskAdditionalTagsDialog(self.root, 
                                         ', '.join(SETTINGS['additional_tags']))
        if dialog.pressed == 'OK':
            new_tags = utils.get_tags_from_string(dialog.message.strip())
            if new_tags != SETTINGS['additional_tags']:
                SETTINGS['additional_tags'] = new_tags
                SETTINGS.save_settings()
        dialog.destroy()

    def _create_root(self):
        self.root.destroy()
        self.root = Tk()
        self.root.title('%s - Mabot' % (self.suite.name))
        self.root.protocol("WM_DELETE_WINDOW", self._quit)
        self.root.configure(background='white')
        width, height = self.root.maxsize()
        self.root.geometry('%dx%d+100+50' % (width-200, height-100))

    def _create_middle_window(self):
        middle_window = CommonFrame(self.root)
        self._create_visibility_selection(middle_window)
        self.canvas = self._create_tree(middle_window)
        self._init_tree_view()
        self.editor_frame = CommonFrame(middle_window)
        self.current_editor = SuiteEditor(self.editor_frame, self._active_node)
        self.editor_frame.pack(anchor=N+W, expand=1)
        middle_window.pack(fill=BOTH, expand=1)

    def _create_tree(self, master):
        tree_area = CommonFrame(master)
        canvas = TreeWidget.ScrolledCanvas(tree_area, bg="white", 
                                           highlightthickness=0, takefocus=1)
        canvas.frame.pack(fill=BOTH, expand=1)
        tree_area.pack(side=LEFT, fill=BOTH)
        return canvas
    
    def _create_visibility_selection(self, master):
        tag_selection_frame = CommonFrame(master)
        self._create_pattern_field(tag_selection_frame)
        self._create_tag_selection(tag_selection_frame)
        self._update_visibility()

    def _create_pattern_field(self, master):
        self.tag_pattern = Entry(master, width=25)
        self.last_tag_pattern = ''
        self.tag_pattern.pack(side=LEFT)
        update = lambda x: self._tag_pattern_updated()
        self.tag_pattern.bind('<Leave>', update)
        self.tag_pattern.bind('<Return>', update)

    def _create_tag_selection(self, master):
        self.tag_selection = StringVar(master)
        self.tag_selection.set(ALL_TAGS_VISIBLE) # default value
        self.previous_tag_selection = self.tag_selection.get()
        self.tag_options = OptionMenu(master, self.tag_selection, ALL_TAGS_VISIBLE, 
                                      command=lambda x: self._tag_selection_updated(True)) 
        self.tag_options.configure(bg="white")
        self.tag_options.pack(side=LEFT)
        master.pack(anchor=NW)

    def _tag_pattern_updated(self):
        if self.last_tag_pattern == self.tag_pattern.get():
            return
        self.last_tag_pattern = self.tag_pattern.get()
        self._update_visibility()
        self._tag_selection_updated()
    
    def _update_visibility(self):
        self._change_visibility()
        self.tag_selection.set(ALL_TAGS_VISIBLE) # default value
        self._recreate_tag_selection()

    def _change_visibility(self):    
        inc, exc = get_includes_and_excludes_from_pattern(self.tag_pattern.get())
        self.suite.change_visibility(inc, exc, self.tag_selection.get())
    
    def _recreate_tag_selection(self):
        selection = self.tag_options['menu']
        while selection.index(END) != 0:
            selection.delete(END)
        for tag in sorted(self.suite.get_all_visible_tags()):
            selection.insert(END, 'command', label=tag, 
                             command=_setit(self.tag_selection, tag, 
                                            lambda x: self._tag_selection_updated(True)))
        
    def _tag_selection_updated(self, only_selection_updated=False):
        if only_selection_updated and \
            self.tag_selection.get() == self.previous_tag_selection:
            return
        self.previous_tag_selection = self.tag_selection.get()
        self._change_visibility()
        self.suite.update_status_and_message()
        self._init_tree_view()
        self._create_new_editor()

    def _init_tree_view(self):
        item = SuiteTreeItem(self.suite)
        self.node = Node(self.canvas.canvas, None, item, self)
        self.node.update()
        self.node.expand()
        self._active_node = self.node

    def _set_status_passed(self, all=False):
        self._set_status('PASS', all=all)
        self.current_editor.update()
        
    def _set_status_failed(self, all=False):
        dialog = ChangeStatusDialog(self.root)
        if dialog.pressed == 'OK':
            self._set_status('FAIL', dialog.message, all)
        dialog.destroy()

    def _set_status(self, status, message=None, all=False):
        if all:
            self._active_node.item.model_item.set_all(status, message)
        else:
            self._active_node.item.model_item.update_status_and_message(status, message)
        self.node.update()
        self._create_new_editor()
            
    def _add_tag(self, event=None):
        if self._active_node is not None \
            and self._active_node.item.model_item.class_type != "KEYWORD":
            dialog = EditTagDialog(self.root, "Add")
            if dialog.pressed == 'OK':
                self._add_new_tag(dialog.message)
            dialog.destroy()
        else:
            self._no_node_selected("No test suite or test case selected!")

    def _remove_tag(self, event=None):
        if self._active_node is not None \
            and self._active_node.item.model_item.class_type != "KEYWORD":
            dialog = EditTagDialog(self.root, "Remove")
            if dialog.pressed == 'OK':
                self._remove_old_tag(dialog.message)
            dialog.destroy()
        else:
            self._no_node_selected("No test suite or test case selected!")
    
    def _add_new_tag(self, tag):
        self._active_node.item.model_item.add_tag(tag)
        self._create_new_editor()
        self._update_visibility()

    def _remove_old_tag(self, tag):
        self._active_node.item.model_item.remove_tag(tag)
        self._create_new_editor()
        self._update_visibility()
            
    def _no_node_selected(self, message=None):
        if message is None:
            message = "No test suite, test case or keyword selected!"
        self._statusbar_right.configure(text=message)

    def notify_select(self, tree_node):
        if self._active_node is None or tree_node != self._active_node:
            self._active_node = tree_node
            self._create_new_editor()
            self._statusbar_right.configure(text='')
                
    def _create_new_editor(self):
        self.current_editor.close()
        self.current_editor = Editor(self.editor_frame, self._active_node)

    def _open_file(self, event=None):
        if self._continue_without_saving():
            path = tkFileDialog.Open().show()
            if path:
                self._load_data_and_create_ui(path)
        
    def _open_dir(self, event=None):
        if self._continue_without_saving():
            directory = tkFileDialog.Directory().show()
            if directory:
                self._load_data_and_create_ui(directory)
                
    def _save(self, event=None):
        try:
            path, changes = self.io.save_data()
            if changes:
                self._init_tree_view()
                self.notify_select(self.node)
                self._update_visibility()
                self._create_new_editor()
            if path is not None:
                self._statusbar_right.configure(text='Wrote output to: ' + path)
            else:
                self._statusbar_right.configure(text='No changes to be saved.')        
        except Exception, error:
            tkMessageBox.showerror('Saving Failed!', error[0])
                    
    def _save_as(self):
        path = tkFileDialog.SaveAs().show()
        if path != "":
            self.io.output = path
            self._save()
    
    def _quit(self, event=None):
        if self._continue_without_saving():
            self.root.destroy()

    def _continue_without_saving(self):
        return not DATA_MODIFIED.is_modified() or \
            tkMessageBox.askyesno("Unsaved data", 
                    "Data is not Saved!\n Continue?")

    def _edit_settings(self):
        settings_dialog = SettingsDialog(self.root, "Settings")
        SETTINGS.update(settings_dialog.new_settings, self.suite)
                        
    def _about(self, event=None):
        msg = '''Mabot, version %s

More information: http://code.google.com/p/robotframework-mabot/''' % (version)
        tkMessageBox.showinfo("About Mabot", msg)
     
    def _create_menu(self):
        menubar = Menu(self.root)
        self._create_file_menu(menubar)
        self._create_settings_menu(menubar)
        self._create_tools_menu(menubar)
        self._create_help_menu(menubar)        
        self.root.config(menu=menubar) # display the menu

    def _create_file_menu(self, menubar):
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open File         ", command=self._open_file)
        filemenu.add_command(label="Open Dir    Ctrl+O", command=self._open_dir)
        self.root.bind("<Control-o>", self._open_dir)
        filemenu.add_separator()
        filemenu.add_command(label="Save        Ctrl+S", command=self._save)
        self.root.bind("<Control-s>", self._save)
        filemenu.add_command(label="Save As", command=self._save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Quit        Ctrl+Q", command=self._quit)
        self.root.bind("<Control-q>", self._quit)
        menubar.add_cascade(label="File", menu=filemenu)

    def _create_settings_menu(self, menubar):
        settingsmenu = Menu(menubar, tearoff=0)
        settingsmenu.add_command(label="Settings", command=self._edit_settings)
        settingsmenu.add_command(label="Restore Settings", 
                                 command=SETTINGS.restore_settings)
        menubar.add_cascade(label="Settings", menu=settingsmenu)

    def _create_tools_menu(self, menubar):
        toolsmenu = Menu(menubar, tearoff=0)
        toolsmenu.add_command(label="Set All Passed  Ctrl+P", 
                              command=lambda: self._set_status_passed(all=True))
        self.root.bind("<Control-p>", lambda x: self._set_status_passed(all=True))        
        toolsmenu.add_command(label='Set All Failed  Ctrl+F', 
                              command=lambda: self._set_status_failed(all=True))
        self.root.bind("<Control-f>", lambda x: self._set_status_failed(all=True))        
        toolsmenu.add_command(label='Add Tag     Ctrl+A', command=self._add_tag)
        self.root.bind("<Control-a>", self._add_tag)        
        toolsmenu.add_command(label='Remove Tag     Ctrl+R', command=self._remove_tag)
        self.root.bind("<Control-r>", self._remove_tag)
        menubar.add_cascade(label="Tools", menu=toolsmenu)

    def _create_help_menu(self, menubar):
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About Mabot   Ctrl+H", command=self._about)
        menubar.add_cascade(label="Help", menu=helpmenu)
        self.root.bind("<Control-h>", self._about)

    def _create_button(self, parent, label, command):
        button = Button(parent, text=label, command=command)
        button.pack(side=LEFT, padx=5, pady=2, fill=Y)
        return button

    def _create_statusbar(self, root):
        statusbar = CommonFrame(root)
        self._statusbar_left = Label(statusbar, background='white')
        self._statusbar_left.pack(side=LEFT)
        self._statusbar_right = Label(statusbar, background='white')
        self._statusbar_right.pack(side=RIGHT)
        statusbar.pack(side=BOTTOM, fill=X)

