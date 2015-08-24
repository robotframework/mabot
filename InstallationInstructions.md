# Preconditions #

Before Mabot can be installed, following software must be installed:

  * [Python](http://python.org) Note: Python's graphical toolkit Tkinter is needed. In some Unix based Operating Systems that is not part of the Python's default installation. In Ubuntu you can install by `sudo apt-get install idle`.
  * [Robot Framework](http://robotframework.org), version 2.0 or newer


# Installation #

There are two distributions available:

  * Windows executable installer. The default values should be fine.
  * Source distribution. To install from source, extract and run `python setup.py install`

On Windows PythonInstallationDir\Scripts\ needs to be added to the PATH environment variable if you have not done that already (part of normal Robot Framework installation)

# Testing Installation #

After installation, command `mabot.py` starts the Mabot tool.