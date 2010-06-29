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


def get_tags_from_string(tags_string):
    """Return list of tags from given string"""
    if tags_string:
        tags = tags_string.split(', ')
    else:
        tags = []
    return [ tag for tag in tags if tag ]

def get_status_color(item):
    colours = {"PASS":"green", "FAIL":"red", "NOT_EXECUTED":"black"}
    return colours.get(item.get_execution_status(), "black")
