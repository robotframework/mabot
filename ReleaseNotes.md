## Mabot 0.10 ##

Mabot 0.10 comes with a bundled Robot Framework. This should solve compatibility issues with different Robot versions. We also changed the start script to be just "mabot" instead of "mabot.py".

| **ID** | **Type** | **Priority** | **Summary** |
|:-------|:---------|:-------------|:------------|
| [Issue 66](https://code.google.com/p/robotframework-mabot/issues/detail?id=66) | Enhancement | High         | Bundle robot with Mabot |
| [Issue 65](https://code.google.com/p/robotframework-mabot/issues/detail?id=65) | Defect   | Medium       | Unable to Update Test Status in output.xml. Getting error "AttributeError: 'Message' object has no attribute 'serialize'" |

Altogether 2 issues.

## Mabot 0.9 ##

Fixes bugs when working with Robot Framework 2.7.x.

| **ID** | **Type** | **Priority** | **Summary** |
|:-------|:---------|:-------------|:------------|
| [Issue 59](https://code.google.com/p/robotframework-mabot/issues/detail?id=59) | Defect   | Critical     | Timestamp is set to 00000000 00:00:00.000 when keyword is set to FAIL |
| [Issue 60](https://code.google.com/p/robotframework-mabot/issues/detail?id=60) | Defect   | Medium       | Documentation shows \n instead of newline |

## Mabot 0.8 ##

Fixes a critical bug that prevented Mabot from working with Robot Framework 2.6.x and 2.7. This version is now compatible with all 2.5, 2.6 and 2.7 Robot Framework versions.

| **ID** | **Type** | **Priority** | **Summary** |
|:-------|:---------|:-------------|:------------|
| [Issue 57](https://code.google.com/p/robotframework-mabot/issues/detail?id=57) | Defect   | Critical     | Mabot is not compatible with Robot Framework 2.6 nor 2.7 |


## Mabot 0.7.1 ##

Fixes a critical bug that prevented Mabot from working with Robot Framework 2.5.3. This version is now compatible with all 2.5.x versions.

| **ID** | **Type** | **Priority** | **Summary** |
|:-------|:---------|:-------------|:------------|
| [Issue 55](https://code.google.com/p/robotframework-mabot/issues/detail?id=55) | Defect   | Critical     | Mabot 0.7 incompatible with RF 2.5.3 |

Altogether 1 issues.


## Mabot 0.7 ##

This version is mainly compatibility release and makes Mabot compatible with Robot Framework 2.5. Unfortunately it was not possible to maintain support for older Robot Framework versions and therefore 0.7 works
only with RF 2.5. If RF 2.1.3 or older is needed, Mabot 0.6.1 needs to be used.

| **ID** | **Type** | **Priority** | **Summary** |
|:-------|:---------|:-------------|:------------|
| [Issue 53](https://code.google.com/p/robotframework-mabot/issues/detail?id=53) | Defect   | Critical     | TXT and RST file formats are not supported |
| [Issue 51](https://code.google.com/p/robotframework-mabot/issues/detail?id=51) | Enhancement | Critical     | Robotframework 2.5 compatibility |
| [Issue 45](https://code.google.com/p/robotframework-mabot/issues/detail?id=45) | Defect   | High         | ON/OFF settings does not work with 2.6.x Python |


## Mabot 0.6.1 ##

This minor release contains only few bug fixes which are listed below. Reason for the release was [issue 41](https://code.google.com/p/robotframework-mabot/issues/detail?id=41). In case you are not using "Tags Added to Modified Tests" setting there is no reason to update to this r
elease.

| **ID** | **Type** | **Priority** | **Summary** |
|:-------|:---------|:-------------|:------------|
| [Issue 41](https://code.google.com/p/robotframework-mabot/issues/detail?id=41) | Defect   | High         | Tags are not added to test case when keyword status is changed and when "Tags Added to Modified Tests" contains tags |
| [Issue 39](https://code.google.com/p/robotframework-mabot/issues/detail?id=39) | Defect   | Medium       | Exiting with unsaved changes is not clear |
| [Issue 42](https://code.google.com/p/robotframework-mabot/issues/detail?id=42) | Enhancement | Medium       | Information that tags should be separated with comma and space should be visible in settings dialog |

## Mabot 0.6 ##

Main change is compatibility with Robot Framework 2.1 ([Issue 25](https://code.google.com/p/robotframework-mabot/issues/detail?id=25)). All fixes included to this release are listed below. Note that fix to [issue 26](https://code.google.com/p/robotframework-mabot/issues/detail?id=26) required changing how settings are saved. Therefore settings saved with previous Mabot versions does not work and you need to set your personal settings again.


| **ID** | **Type** | **Priority** | **Summary** |
|:-------|:---------|:-------------|:------------|
| [Issue 25](https://code.google.com/p/robotframework-mabot/issues/detail?id=25) |Enhancement | Critical     | Robot Framework 2.1 compatibility |
| [Issue 26](https://code.google.com/p/robotframework-mabot/issues/detail?id=26) | Defect   | High         | Saving settings does not work without rights to installation directory |
| [Issue 27](https://code.google.com/p/robotframework-mabot/issues/detail?id=27) | Enhancement | High         | Remove tags should show tags that can be removed |
| [Issue 32](https://code.google.com/p/robotframework-mabot/issues/detail?id=32) | Enhancement | High         | Remove tags when test is modified |
| [Issue 33](https://code.google.com/p/robotframework-mabot/issues/detail?id=33) | Enhancement | High         | When "Set All Failed" is used, non-default messages are not modified at all |
| [Issue 22](https://code.google.com/p/robotframework-mabot/issues/detail?id=22) | Defect   | Medium       | Any keyword fail, the whole case should be failed |
| [Issue 28](https://code.google.com/p/robotframework-mabot/issues/detail?id=28) | Enhancement | Medium       | Add tags should allow list of tags to be added |
| [Issue 30](https://code.google.com/p/robotframework-mabot/issues/detail?id=30) | Defect   | Medium       | Cancel does not work in additional tags asked at startup |


## Mabot 0.5.2 ##

This is bug fix release.

| **ID** | **Type** | **Priority** | **Summary** |
|:-------|:---------|:-------------|:------------|
| [Issue 21](https://code.google.com/p/robotframework-mabot/issues/detail?id=21) | Enhancement | High         | Long suite hierarchy could be shorten as one item in suite tree |
| [Issue 23](https://code.google.com/p/robotframework-mabot/issues/detail?id=23) | Defect   | High         | Only ALL MATCHING TAGS VISIBLE visible with folder suite |
| [Issue 20](https://code.google.com/p/robotframework-mabot/issues/detail?id=20) | Defect   | Medium       | Keyword arguments are incorrect if keyword contains other keywords |


## Mabot 0.5.1 ##

This is bug fix release which contains also XML-files backup improvement and progressbar for longer operations.

| **ID** | **Type** | **Priority** | **Summary** |
|:-------|:---------|:-------------|:------------|
| [Issue 18](https://code.google.com/p/robotframework-mabot/issues/detail?id=18) | Defect   | Critical     | Saving keyword data failed |
| [Issue 16](https://code.google.com/p/robotframework-mabot/issues/detail?id=16) | Enhancement | High         | Create backup from XML |
| [Issue 17](https://code.google.com/p/robotframework-mabot/issues/detail?id=17) | Enhancement | Medium       | Provide progress information to user |


## Mabot 0.5 ##

Main change is compatibility with Robot Framework 2.0.3 ([Issue 11](https://code.google.com/p/robotframework-mabot/issues/detail?id=11)). All fixes included to this release are listed below:

| **ID** | **Type** | **Priority** | **Summary** |
|:-------|:---------|:-------------|:------------|
| [Issue 11](https://code.google.com/p/robotframework-mabot/issues/detail?id=11) | Defect   | Critical     | Mabot does not work with Robot Framework 2.0.3 |
| [Issue 10](https://code.google.com/p/robotframework-mabot/issues/detail?id=10) | Defect   | Medium       | If user keyword used in test cases is defined multiple time |
| [Issue 13](https://code.google.com/p/robotframework-mabot/issues/detail?id=13) | Defect   | Medium       | XML file name is incorrect when suite folder is given from command line with last path separator  |
| [Issue 14](https://code.google.com/p/robotframework-mabot/issues/detail?id=14) | Defect   | Medium       | Mabot sometimes cannot paste. |
| [Issue 15](https://code.google.com/p/robotframework-mabot/issues/detail?id=15) | Defect   | Medium       | Tags are not loaded from html if results are loaded from XML |