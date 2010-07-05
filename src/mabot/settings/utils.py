from copy import copy
import os
from pprint import pprint
import sys


if os.name == 'nt':
    SETTINGS_DIRECTORY = os.path.join(os.environ['APPDATA'], 'RobotFramework')
else:
    SETTINGS_DIRECTORY = os.path.expanduser('~/.robotframework')
if not os.path.exists(SETTINGS_DIRECTORY):
    os.mkdir(SETTINGS_DIRECTORY)


class InvalidSettings(Exception):
    """ Used when setting file exists, but it is not a valid Python file."""


class SettingsIO:

    def __init__(self, tool_name=None, file_name=None, path=None):
        """tool_name is used to create folder for tool specific settings.
        In case file name is given, that is used to create the settings file.
        Only valid suffix for file_name is is '.py'.
        In case path is given, it is used instead of tool_name and file_name.
        """
        if path:
            self.directory = os.path.dirname(path)
            self._path = path
        else:
            self.directory, self._path = self._get_paths(tool_name, file_name)
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)

    def _get_paths(self, tool_name, file_name):
        if not file_name:
            file_name = tool_name + 'settings.py'
        settings_dir = os.path.join(SETTINGS_DIRECTORY, tool_name)
        return settings_dir, os.path.join(settings_dir, file_name)

    def write(self, settings_dict):
        """ Writes given settings dictionary to settings file.

        Setting names (keys) should not contain spaces.
        """
        self._validate_setting_names(settings_dict)
        out = open(self._path, 'w')
        for key in settings_dict.keys():
            out.write('%s = ' % key)
            pprint(settings_dict[key], out)
        out.close()

    def _validate_setting_names(self, settings_dict):
        for name in settings_dict.keys():
            if ' ' in name:
                msg = "Setting name '%s' contains space." % (name)
                raise InvalidSettings(msg)

    def read(self):
        """Returns given settings from saved settings."""
        if not os.path.exists(self._path):
            return {}
        namespace = {}
        f = open(self._path, 'r')
        try:
            exec f in namespace
        except SyntaxError, error:
            message = "Settings file '%s' is not a valid Python file.\n%s"
            message = message % (self._path, error)
            raise InvalidSettings(message)
        finally:
            f.close()
        for key in namespace.keys():
            if key.startswith('_'):
                namespace.pop(key)
        return namespace

    def remove(self):
        """Removes settings file."""
        if os.path.exists(self._path):
            os.remove(self._path)


class RFSettings(SettingsIO):

    def __init__(self, tool_name=None, file_name=None, path=None, defaults={},
                 logger=None):
        """tool_name is used to create folder for tool specific settings.
        In case file name is given, that is used to create the settings file.
        In case path is given, it is used instead of tool_name and file_name.
        Default values to the settings can be also given. It can be dictionary
        or path to python file.
        logger is method which is called with message if any error occurs
        when loading or saving settings.
        """
        self._settings = {}
        self._logger = logger or (lambda x: None)
        SettingsIO.__init__(self, tool_name, file_name, path)
        self.update(defaults, save=False)
        self._defaults = copy(self._settings)
        self.load()

    def __setitem__(self, name, value):
        #TODO: Check value type
        self._settings[name] = value

    def __getitem__(self, name):
        return self._settings[name]

    # TODO: Is there need def set(self, value) which could return boolean if
    # value have changed.

    def update(self, settings, save=True):
        """Updates based on the given settings.
        Settings can be dictionary or path to python file.
        In case of python file, it is imported and all attributes
        not starting with underscore are considered as settings.
        """
        if not settings:
            return
        if isinstance(settings, dict):
            for key in settings.keys():
                if not key.startswith('_'):
                    self._settings[key] = settings[key]
        else:
            try:
                self.update(SettingsIO(path=settings).read(), save)
            except (InvalidSettings), error:
                self._logger(error.message)
        if save:
            self.save()

    def save(self):
        self.write(self._settings)

    def load(self):
        try:
            settings = self.read()
        except InvalidSettings, error:
            self._logger(str(error))
            return
        for key in settings.keys():
            self._settings[key] = settings[key]

    def restore(self):
        self._settings = {}
        self.update(self._defaults)
