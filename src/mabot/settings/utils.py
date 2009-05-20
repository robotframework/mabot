import os
from pprint import pprint
import sys


if os.name == 'nt':
    SETTINGS_DIRECTORY = os.path.join(os.environ['APPDATA'], 'RobotFramework')
else:
    SETTINGS_DIRECTORY = os.path.expanduser('~/.robotframework')
if not os.path.exists(SETTINGS_DIRECTORY):
    os.mkdir(SETTINGS_DIRECTORY)


def get_settings_path(file_name=None):
    """Returns path to a setting file or, if no file given, to the setting directory."""
    if not file_name:
        return SETTINGS_DIRECTORY
    return os.path.join(SETTINGS_DIRECTORY, file_name)


class MissingSettings(Exception):
    """ Used when setting file does not exist."""


class InvalidSettings(Exception):
    """ Used when setting file exists, but it is not a valid Python file."""


class SettingsIO:
    
    def __init__(self, path):
        self.path = path
        sys.path.insert(0, os.path.dirname(self.path))
        self._settings_module_name = os.path.basename(self.path)[:-3]

        
    def write_settings(self, settings_dict):
        """ Writes given settings dict to settings file.
        
        Setting names (keys) should not contain spaces.
        """
        self._validate_setting_names(settings_dict)
        # settings can be read from old pyc if reading happens in the same second  
        self.remove_settings() 
        out = open(self.path, 'w')
        for key in settings_dict.keys():
            out.write('%s = ' % key)
            pprint(settings_dict[key], out)
        out.close()

    def remove_settings(self):
        for path in [self.path, '%sc' % self.path]:
            if os.path.exists(path):
                os.remove(path)

    def _validate_setting_names(self, settings_dict):
        for name in settings_dict.keys():
            if ' ' in name:
                msg = "Setting name '%s' contains space." % (name)
                raise InvalidSettings(msg)

    def read_settings(self):
        settings_module = self._load_settings_module()
        settings = {}
        for item in dir(settings_module):
            if not item.startswith('_'):
                settings[item] = getattr(settings_module, item)
        return settings

    def _load_settings_module(self):
        try:
            settings_module = __import__(self._settings_module_name)
            settings_module = reload(settings_module)
        except ImportError:
            message = "Could not import settings file '%s'" % self.path
            raise MissingSettings(message)
        except SyntaxError, e:
            message = "Settings file '%s' is not a valid Python file.\n%s" 
            message = message % (self.path, e)
            raise InvalidSettings(message)
        return settings_module
