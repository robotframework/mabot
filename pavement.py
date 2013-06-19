import sys
import os

from os.path import dirname, join, isdir, isfile
from paver.easy import *
from paver.setuputils import setup, find_package_data


ROOT_DIR = path(__file__).dirname()
SOURCE_DIR = ROOT_DIR/'src'
TEST_DIR = ROOT_DIR/'utest'
DIST_DIR = ROOT_DIR/'dist'
BUILD_DIR = ROOT_DIR/'build'
MABOT_PACKAGE = ROOT_DIR/'src'/'mabot'
LIB_TARGET = MABOT_PACKAGE/'lib'
LIB_SOURCE = ROOT_DIR/'lib'
MANIFEST = ROOT_DIR/'MANIFEST.in'


def find_packages(where):
    def is_package(path):
        return isdir(path) and isfile(join(path ,'__init__.py'))
    pkgs = []
    for dirpath, dirs, _ in os.walk(where):
        for dirname in dirs:
            pkg_path = join(dirpath, dirname)
            if is_package(pkg_path):
                pkgs.append('.'.join((pkg_path.split(os.sep)[1:])))
    return pkgs

def _get_version():
    sys.path.insert(0, join(dirname(__file__), 'src', 'mabot'))
    from version import version
    return version

setup(name         = 'mabot',
      version      =  _get_version(),
      description  = 'Manual test result reporting tool for Robot Framework',
      author       = 'Robot Framework Developers',
      author_email = 'robotframework-devel@googlegroups.com',
      url          = 'http://code.google.com/p/robotframework-mabot/',
      download_url = 'http://code.google.com/p/robotframework-mabot/downloads/list',
      license      = 'Apache License 2.0',
      platforms    = 'any',
      package_dir  = {'' : str(SOURCE_DIR)},
      packages     = find_packages(str(SOURCE_DIR)) + \
                        ['mabot.lib.%s' % str(name) for name
                         in find_packages(str(LIB_SOURCE))],
      package_data = find_package_data(str(SOURCE_DIR)),
      # Always install everything, since we may be switching between versions
      options      = { 'install': { 'force' : True } },
      scripts      = [ 'src/bin/mabot', 'src/bin/mabot.bat' ]
      )

@task
@needs('clean', '_prepare_build',  'generate_setup', 'minilib',
       'setuptools.command.sdist')
def sdist():
    """Creates source distribution with bundled dependencies"""
    _after_distribution()

@task
@needs('_windows', 'clean', '_prepare_build',
       'setuptools.command.bdist_wininst')
def wininst():
    """Creates Windows installer with bundled dependencies"""
    _after_distribution()

@task
@consume_args
def test(args):
    """Run unit tests (requires nose)"""
    _remove_bytecode_files()
    assert _run_nose(args) is True

def _run_nose(args):
    from nose import run as noserun
    _set_development_path()
    return noserun(defaultTest=TEST_DIR,
                   argv=['', '--with-xunit', '--xunit-file=nosetests.xml', '--m=^test_'] + args)

@task
def clean():
    _clean()

def _clean(keep_dist=False):
    if not keep_dist and DIST_DIR.exists():
        DIST_DIR.rmtree()
    if BUILD_DIR.exists():
        BUILD_DIR.rmtree()
    if LIB_TARGET.exists():
        LIB_TARGET.rmtree()
    for name in 'paver-minilib.zip', 'setup.py':
        p = path(name)
        if p.exists():
            p.remove()
    _remove_bytecode_files()

def _remove_bytecode_files():
    for d in LIB_SOURCE, SOURCE_DIR, TEST_DIR:
        for pyc in d.walkfiles(pattern='*.pyc'):
            os.remove(pyc)
        for clazz in d.walkfiles(pattern='*$py.class'):
            os.remove(clazz)

def _set_development_path():
    sys.path.insert(0, LIB_SOURCE)
    sys.path.insert(0, SOURCE_DIR)

@task
@consume_args
def run(args):
    """Start development version of Mabot"""
    _set_development_path()
    from mabot import run
    run(args)

@task
def _prepare_build():
    if not LIB_TARGET.exists():
        LIB_SOURCE.copytree(LIB_TARGET)

@task
def _windows():
    if os.sep != '\\':
        sys.exit('Windows installers may only be created in Windows')

def _after_distribution():
    _clean(keep_dist=True)