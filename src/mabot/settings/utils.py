import os
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
