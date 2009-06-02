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
import tkSimpleDialog
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
from progressbar import ProgressBar
from ui import *


class Mabot:
    
    def __init__(self, datasource, options):
        self.root = Tk()
        self._save_options(options)
        self.io = IO()
        self.suite = self.io.load_data(None)
        self._create_ui()
        self._load_data_and_update_ui(datasource)
        self._ask_additional_tags()
        self.root.mainloop()

    def _save_options(self, options):
        if options['include']:
            SETTINGS['include'] = options['include']
        if options['exclude']:
            SETTINGS['exclude'] = options['exclude']
        if options['include'] or options['exclude']:
            SETTINGS.save()

    def _load_data_and_update_ui(self, datasource):
        progress = ProgressBar(self.root, 'Loading...')
        try:
            self.suite = self.io.load_data(datasource)
            progress.destroy()
        except IOError, error:
            progress.destroy()
            self._show_error(error, 'Loading Failed!')
        except Exception, error:
            progress.destroy()
            self._show_error(error, "Unexpected error while loading data!")
        else:
            self._update_ui()

    def _show_error(self, error, message):
        tkMessageBox.showerror(message, error[0])            

    def _create_ui(self):
        self._create_root()
        self._create_menu()
        self._create_middle_window()
        self._create_statusbar(self.root)

    def _update_ui(self):
        self._init_tree_view()
        self._create_new_editor()

    def _ask_additional_tags(self):
        if SETTINGS['ask_additional_tags_at_startup']:
            prompt = "Give tag(s) that you want to add to all the test cases\n"\
                     "you are going to report (i.e. env-x, build-y):"
            tags = tkSimpleDialog.askstring("Additional Tags", prompt,
                            initialvalue=', '.join(SETTINGS['additional_tags']))
            SETTINGS['additional_tags'] = utils.get_tags_from_string(tags)
            SETTINGS.save()

    def _create_root(self):
        self.root.destroy()
        self.root = Tk()
        name = 'Mabot'
        if self.suite.name:
            name = '%s - %s' % (self.suite.name, name)
        self.root.title(name)
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
        self.current_editor.update()
            
    def _add_tag(self, event=None):
        if self._active_node.item.model_item.is_keyword():
            self._statusbar_right.configure(text=
                            "No test suite or test case selected")
        else:
            tags = tkSimpleDialog.askstring('Add Tags', 
                            "Add tags (separated with ', ' i.e. tag-1, tag-2)")
            self._add_new_tags(tags)

    def _remove_tag(self, event=None):
        if self._active_node.item.model_item.is_keyword():
            self._statusbar_right.configure(text=
                            "No test suite or test case selected")
        else:
            tags = sorted(self._active_node.item.model_item.get_all_visible_tags([]))
            dialog = RemoveTagsDialog(self.root, tags)
            if dialog.pressed == 'OK':
                self._remove_old_tag(dialog.tags)
            dialog.destroy()
    
    def _add_new_tags(self, tags):
        for tag in utils.get_tags_from_string(tags):
            self._active_node.item.model_item.add_tag(tag)
        self._create_new_editor()
        self._update_visibility()

    def _remove_old_tag(self, tags):
        for tag in tags:
            self._active_node.item.model_item.remove_tag(tag)
        self._create_new_editor()
        self._update_visibility()
            
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
                self._load_data_and_update_ui(path)
        
    def _open_dir(self, event=None):
        if self._continue_without_saving():
            directory = tkFileDialog.Directory().show()
            if directory:
                self._load_data_and_update_ui(directory)
                
    def _save(self, path=None):
        progress = ProgressBar(self.root, 'Saving...')
        progress.add_ask_method(tkMessageBox.askyesno)
        try:
            saved, changes = self.io.save_data(path, progress.call_ask_method)
            progress.destroy()
        except Exception, error:
            progress.destroy()
            tkMessageBox.showerror('Saving Failed!', error.message)
            return
        if changes:
            self._init_tree_view()
            self._update_visibility()
            self._create_new_editor()
        if saved:
            self._statusbar('Wrote output to ' + self.io.output)
            self.current_editor.update()
        else:
            if changes:
                self._statusbar('Loaded changes from ' + self.io.output)
            else:
                self._statusbar('No changes to be saved')        
                 
    def _statusbar(self, message):
        self._statusbar_right.configure(text=message)
       
    def _save_as(self):
        path = tkFileDialog.SaveAs().show()
        if path:
            self._save(path)
    
    def _quit(self, event=None):
        if self._continue_without_saving():
            self.root.destroy()

    def _continue_without_saving(self):
        return not DATA_MODIFIED.is_modified() or \
            tkMessageBox.askyesno("Unsaved data", 
                    "Data is not Saved!\n Continue?")

    def _edit_settings(self):
        settings_dialog = SettingsDialog(self.root, "Settings")
        SETTINGS.update_settings(settings_dialog.new_settings, self.suite)
        self.current_editor.update()
                        
    def _about(self, event=None):
        msg = '''Mabot, version %s

More information: http://code.google.com/p/robotframework-mabot/''' % (version)
        tkMessageBox.showinfo("About Mabot", msg)
     
    def _create_menu(self):
        menubar = Menu(self.root)
        self._create_file_menu(menubar)
        self._create_edit_menu(menubar)
        self._create_settings_menu(menubar)
        self._create_tools_menu(menubar)
        self._create_help_menu(menubar)        
        self.root.config(menu=menubar) # display the menu
        self._create_popup_menu()

    def _create_file_menu(self, menubar):
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open File         ", command=self._open_file)
        filemenu.add_command(label="Open Dir    Ctrl+O", command=self._open_dir)
        self.root.bind("<Control-o>", self._open_dir)
        filemenu.add_separator()
        filemenu.add_command(label="Save        Ctrl+S", command=lambda: self._save())
        self.root.bind("<Control-s>", lambda x: self._save())
        filemenu.add_command(label="Save As", command=self._save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Quit        Ctrl+Q", command=self._quit)
        self.root.bind("<Control-q>", self._quit)
        menubar.add_cascade(label="File", menu=filemenu)

    def _create_edit_menu(self, menubar):
        editmenu = Menu(menubar, tearoff=0)
        self._create_copy_paste(editmenu)
        self.root.bind("<Control-x>", lambda x: self._cut)
        self.root.bind("<Control-c>", lambda x: self._copy)
        self.root.bind("<Control-v>", lambda x: self._paste)
        menubar.add_cascade(label="Edit", menu=editmenu)

    def _create_copy_paste(self, menu):
        menu.add_command(label="Cut   Ctrl-X", command=self._cut)
        menu.add_command(label="Copy   Ctrl-C", command=self._copy)
        menu.add_command(label="Paste  Ctrl+V", command=self._paste)

    def _create_popup_menu(self):
        popup = Menu(self.root, tearoff=0)
        self._create_copy_paste(popup)
        self.root.bind("<Button-3>", lambda x: popup.tk_popup(x.x_root + 50, 
                                                              x.y_root + 10, 0))        
    def _cut(self):
        self.root.focus_get().event_generate('<<Cut>>')

    def _copy(self):
        self.root.focus_get().event_generate('<<Copy>>')
    
    def _paste(self):
        self.root.focus_get().event_generate('<<Paste>>')
    
    def _create_settings_menu(self, menubar):
        settingsmenu = Menu(menubar, tearoff=0)
        settingsmenu.add_command(label="Settings", command=self._edit_settings)
        settingsmenu.add_command(label="Restore Settings", 
                                 command=SETTINGS.restore)
        menubar.add_cascade(label="Settings", menu=settingsmenu)

    def _create_tools_menu(self, menubar):
        toolsmenu = Menu(menubar, tearoff=0)
        toolsmenu.add_command(label="Set All Passed  Ctrl+P", 
                              command=lambda: self._set_status('PASS', all=True))
        self.root.bind("<Control-p>", lambda x: self._set_status('PASS', all=True))        
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

