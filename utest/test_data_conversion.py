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


import os
import sys
import unittest
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from mabot.ui.editors import get_text_parts

class TestDataConversion(unittest.TestCase):

    def test_basic(self):
        text = 'hello'
        _equals(get_text_parts(text), ((text, 'normal'),))

    def test_basic_link(self):
        text = 'http://www.google.com'
        _equals(get_text_parts(text), ((text, 'link'),))

    def test_basic_file(self):
        text = 'file://my/file'
        _equals(get_text_parts(text), ((text, 'link'),))


    def test_link_with_data_both_sides(self):
        text = 'hello\n\n\nhttp://www.google.com world!\n'
        _equals(get_text_parts(text), (('hello\n\n\n', 'normal'),
                                  ('http://www.google.com', 'link'), 
                                  (' world!\n', 'normal')))

    def test_multiple_links(self):
        text = 'hello http://www.google.com world!\n other http://my.com'
        _equals(get_text_parts(text), (('hello ', 'normal'),
                                  ('http://www.google.com', 'link'), 
                                  (' world!\n other ', 'normal'),
                                  ('http://my.com', 'link')))

    def test_simple_bold(self):
        text = '*hello*'
        _equals(get_text_parts(text), (('hello', 'bold'), ))


    def test_two_bolds(self):
        text = 'some *hello* other *bold*\n'
        _equals(get_text_parts(text), (('some', 'normal'), (' hello ', 'bold'), 
                                  ('other', 'normal'), (' bold\n', 'bold')))

    def test_two_italics(self):
        text = 'some _hello_ other _bold_\n'
        _equals(get_text_parts(text), (('some', 'normal'), (' hello ', 'italic'), 
                                  ('other', 'normal'), (' bold\n', 'italic')))

    def test_file_name_with_underscores(self):
        text = 'some data and then path that should not be converted My_file_name and some more text.\n'
        _equals(get_text_parts(text), ((text, 'normal'), ))

    def test_performance(self):
        starttime = time.time()
        _equals(get_text_parts(long_message), ((long_message, 'normal'), ))
        self.assertTrue(time.time() - starttime < 2)
        
long_message = """
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
lksadjflkdsjf
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
lkjsdlskjglkdjgsome asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
lkjsgldskjgldskjglkjsome asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
kjsdhfkjshdfkh kj hdsfkjh sd
 skd hflds
  sldk hflkdsh fds
  f sd hfldskhf sd
   ldsk hfldks hflds f
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
some asjdkasjd alkjshd ksaj hdksad hkjsa hdksaj hdksaj hdksahd ksaj hdksaj hdk
----------asdkjsadk jhaskd hksaj hdksa hdksaj hd --hh as-d h-as hd-sal dhsald h
"""

def _equals(actual, expected):
    try:
        assert actual == expected
    except AssertionError, e:
        raise AssertionError("\n'%s' !=\n'%s'" % (actual, expected))

if __name__ == "__main__":
    unittest.main()