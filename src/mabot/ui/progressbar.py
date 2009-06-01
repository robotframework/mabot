#  Copyright 2009 Nokia Siemens Networks Oyj
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


import os
from Tkinter import *
import thread
import time


class ProgressBar(Toplevel):
    
    def __init__(self, parent, title):
        self._parent = parent
        self._title = title
        self._init_progress_bar()

    def _init_progress_bar(self):
        if os.name != 'nt':
            self.not_created = True
            return
        Toplevel.__init__(self, self._parent)
        self.title(self._title)
        self.protocol("WM_DELETE_WINDOW", lambda: True) 
        self.width = 200
        self.height = 10
        self.geometry(self._get_location(parent))
        self.progress_bar_view = ProgressBarView(self, self.width, self.height)
        self.progress_bar_view.pack()
        parent.update()
        self._running = thread.allocate_lock()
        thread.start_new_thread(self._update, ())
    
    def add_ask_method(self, method):
        self._ask_method = method
        
    def call_ask_method(self, *args):
        self.destroy()
        result = self._ask_method(*args)
        self._init_progress_bar()
        return result

    def _get_location(self, parent):
        x = parent.winfo_rootx() + parent.winfo_width()/2 - self.width/2
        y = parent.winfo_rooty() + parent.winfo_height()/2 - self.height/2
        return "+%d+%d" % (x, y) 

    def _update(self):
        while self._running.acquire(0):
            self.progress_bar_view.update_progress()
            time.sleep(0.1)
            self._running.release()
            
    def destroy(self):
        if self.not_created:
            return
        self._running.acquire()
        Toplevel.destroy(self)

        
class ProgressBarView:
  
    def __init__(self, master, width, height):
        self.master=master
        self.value = 0
        self.width = width
        self.height = height
        #TODO: Test with Ubuntu
        self.fill_color  = 'blue'
        self.background = 'white'

        self.frame = Frame(self.master, bd=2, width=self.width, height=self.height)
        self.canvas = Canvas(self.frame, background=self.background, 
                             width=self.width, height=self.height)
        self.scale = self.canvas.create_rectangle(0, 0, self.width, self.height, 
                                                  fill=self.fill_color)
        self.canvas.pack(fill=BOTH, expand=YES)
        self.update()

    def update_progress(self):
        self.value += self.width / 20
        if self.value > self.width:
            self.value -= self.width
        self.update()

    def pack(self, *args, **kw):
        self.frame.pack(*args, **kw)

    def update(self):
        start = (float(self.value) / self.width * self.width) - self.width / 4 
        end = float(self.value) / self.width * self.width
        self.canvas.coords(self.scale, start, 0, end, self.height)
        self.canvas.update_idletasks()
