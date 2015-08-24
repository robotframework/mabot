# Create Packages #

## Tag release and create source distribution ##

**create tag:**
```
version=x.y
svn copy -m "Initial $version tag" https://robotframework-mabot.googlecode.com/svn/trunk/ \
    https://robotframework-mabot.googlecode.com/svn/tags/mabot-$version
```
**checkout the created tag:**
```
svn checkout https://robotframework-mabot.googlecode.com/svn/tags/mabot-$version
cd mabot-$version
emacs src/mabot/version.py
svn commit -m "version update"
python create_dists.py
```

## Create Windows installer in Windows ##
```
set version=x.y.x
svn checkout https://robotframework-mabot.googlecode.com/svn/tags/mabot-%version%
cd mabot-%version%
python create_dists.py
```

## Upload the distribution packages ##

  * Windows tags: Featured, Type-Installer, OpSys-Windows
  * Source tags: Featured, Type-Source, OpSys-All

# Update wiki #

  * releasenotes
```
tools/get_issues.py notes mabot x.y
```
  * update main page

# Send emails #

  * Public users and announcement mailing lists
  * NSN internal users and announcement lists