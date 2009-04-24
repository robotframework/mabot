import os


def get_settings_file(file_name):
    if 'NT' in os.name:
        RF_SETTINGS_DIRECTORY = os.path.join(os.environ['APPDATA'], 'robotframework')
    else:
        RF_SETTINGS_DIRECTORY = os.path.expanduser('~/.robotframework')
    if not os.path.exists(RF_SETTINGS_DIRECTORY):
        os.mkdir(RF_SETTINGS_DIRECTORY)
    return os.path.join(RF_SETTINGS_DIRECTORY, file_name)

