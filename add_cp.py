#!/usr/local/bin python

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

COPYRIGHT = open('COPYRIGHT.txt', 'r').readlines()
COPYRIGHT = [ '#  %s' % line for line in COPYRIGHT ]
COPYRIGHT.append('\n')
COPYRIGHT.append('\n')


def add_cps(path):
    print "Scanning directory '%s' for files needing copyright..." % path
    for name in os.listdir(path):
        print name
        fpath = os.path.abspath(os.path.join(path, name))
        if name.endswith('.py'):
            add_cp(fpath)
        elif os.path.isdir(fpath) and not name in ['.svn', '.settings']:
            add_cps(fpath)

def add_cp(path):
    outfile = open(path, 'r+')
    content = outfile.readlines()
    if COPYRIGHT[0] in content:
        outfile.close()
        return
    print "Adding copyrights to", path
    outfile.seek(0)
    outfile.truncate()
    outfile.writelines(COPYRIGHT)
    outfile.writelines(content)
    outfile.close()


if __name__ == '__main__':
    add_cps('.')

