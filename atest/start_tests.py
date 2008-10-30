from os.path import dirname, join
import subprocess

base = dirname(__file__)
mabot_path = join(base, '..', 'src', 'mabot', 'run.py')
test_path = join(base, 'tests')
subprocess.call('python %s %s' % (mabot_path, test_path))