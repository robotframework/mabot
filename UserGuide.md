

# Introduction #

All the relevant features of the Mabot tool are presented below.

# Starting Mabot #

Mabot tool can be started with command `mabot.py`. See usage of Mabot with command `mabot.py --help`.

# Loading Data #

## Mabot Datasources ##

The Mabot tool can read data in two formats. Main datasource for the Mabot are test cases defined in [Robot Framework](http://robotframework.org)'s data formats, html and tsv. Also Robot Framework's XML output data can be modified with Mabot and Mabot saves data to that same XML output format. That makes it possible to use Robot Framework's reporting tool rebot for combining manual and automated test cases results to one combined report.

## Loading Data from Command Line ##

When starting Mabot you can specify whether to load datasource (folder, html or tsv in Robot Framework's data format) or saved data (Robot Framework's output format). Datasource is given as last argument for the Mabot command like `mabot.py --include manual my_tests.html`

## Loading Data from GUI ##

It is also possible to load the data from File Menu. There are two options Open File for opening html, tsv or XML file and Open Directory for opening folder that contains Robot Framework's test case files.

# Marking Test Results #

## Basic Use ##

After you have started the tool, there will be tree view showing all the test suites, test cases and keywords. Basic use is to mark the test cases and keywords to state PASS or FAIL and give an explanation to the message field. At the beginning all the elements in the tree are black meaning that those have not been executed. After items are changed those colour is changed to red or green based on the status. This makes it easy to see which test cases are not tested yet.

## Modifying Tags ##

It is possible to modify test cases tags with add tags and remove tags functionality. There is also setting [Tags Added to Modified Tests](#Tags_Added_to_Modified_Tests.md) which can be used to define tags that are added automatically to the modified test cases. Note: In all tag related settings separator is comma and space ', '.

## Changing Visibility ##

In case there are more test cases it might be useful to select visible test cases based on the test cases tag(s). This is possible using the filter available above the tree view. There is two filters.

To the first filter you can write simple pattern to match the test cases' tags. There are three ways to give that pattern:
  1. One tag as a simple pattern. Tests having a tag matching the pattern are included. Example: 'it-`*`'
  1. Two or more tags (or patterns) separated by '&' or 'AND'. Only tests having all these tags are included. Examples: 'tag1&tag2', 'smokeANDowner-`*`ANDit-10'
  1. Two or more tags (or patterns) separated by 'NOT'. Tests having the first tag but not any of the latter ones are included. Example: 'it-10NOTsmoke'

The second drop down menu filter contains all the tags that test cases matching the first filter have. From that menu you can select one tag at a time as a visible tag.

# Saving Files #

Results are saved to same XML format which Robot Framework is using. Reports and logs can be generated from the XML using Robot Framework's rebot script. See more from [Robot Framework's User Guide](http://code.google.com/p/robotframework/wiki/UserGuide). By default XML file is written to the path where Mabot was started with name output.xml. See also how setting [Always Load Old Data From XML](#Always_Load_Old_Data_From_XML.md) affects on output files name. You can also save the results with what ever name you want by using Save as.

# Settings #

There is multiple settings in Mabot tool that can be used for automatically loading data from saved XML file, adding needed tags for executed tests and so on. All these settings are described below.

## Default Message ##

This is the message that is shown for test cases that are not executed. By default when test case is loaded, it has the default message. Executing means changing test case's status, message or steps' (keywords) status or message. In case the message is changed, Mabot automatically replaces all default messages with the new default message.

## Ask Tags Added to Modified Tests at Startup ##

Defines whether or not ask [Tags Added to Modified Tests](#Tags_Added_to_Modified_Tests.md) at startup time. Quite often test cases are executed using one build, so it might be useful to use this setting to ask that information when ever the Mabot tool is opened.

## Tags Added to Modified Tests ##

Defines the tags that are added to the modified test cases. Information like test executor and build number can be easily added to the test cases with this feature. See also [Ask Tags Added to Modified Tests at Startup](#Ask_Tags_Added_to_Modified_Tests_at_Startup.md) setting above.

## Tags Allowed Only Once ##

Defines prefixes which are allowed only once per test case. If tags are added with "Add Tags" or "Tags Added to Modified Tests" functionality and added tag matches the one of the prefixes, all tags matching that prefix are removed automatically. This functionality is mainly useful with [Tags Added to Modified Tests](#Tags_Added_to_Modified_Tests.md) as you can for example specify that executed-by- is allowed only once and when ever that is added to modified test, old executed-by- tag is removed.

## Always Load Old Data From XML ##

This setting defines whether to read or not to read saved data from XML when opening file or folder. It also changes the the default output path to the XML file even the XML file does not exist. The XML file name is created in following way:

  * XML is added to directory path i.e. some/dir -> some/dir.xml
  * With test data files .html or .tsv is replaced with .xml i.e. my\_tests.html -> my\_tests.xml

## Include Tags ##

Defines tags that are used to include tests when opening test data file or directory.

## Exclude Tags ##

Same as include, but for excluding tags.

## Check Simultaneous Save ##

This option is used when the result XML is saved to i.e. network drive and it is possible that there is simultaneous saves to the same XML file. When this option is used, the data is read from the XML before saving data. In case there are conflicts, those are shown to the user. Note that this option makes saving slower.