# The Watcher User Guide

<img src="./images/theWatcherLogo.png" alt="The Watcher Logo" style="zoom:80%;" />

## Table of Contents
  * [Installation](#installation)
  * [User Guide for The Watcher](#user-guide-for-the-watcher)
    + [Starting an investigation](#starting-an-investigation)
    + [Event Log](#event-log)
    + [File Log](#file-log)
    + [Ending the Investigation and Generate report](#ending-the-investigation-and-generate-report)

## Installation

The installation guide can be found [here](./README.md).

## User Guide for The Watcher
### Starting an investigation

To use The Watcher, run `main.py` in the `src` directory (Please run main.py from the src folder)

```
python main.py
```

<img src="./images/mainPage.png" alt="Main Page" style="zoom:80%;" />

Click on the "Select Investigation Folder" button, Navigate to the target folder and click on "Select Folder".

<img src="./images/selectFolder.png" alt="Select Folder" style="zoom:80%;" />

The path of the folder will be shown. Click on the "Begin Investigation".

<img src="./images/beginInvestigation.png" alt="Begin Investigation" style="zoom:80%;" />

Next, the program will start to collect the hashes of all the files in the directory. A new window would appear to indicate that the files are being hashed. This may take a while depending on the size of the directory and the number of files.

<img src="./images/hashingFiles.png" alt="Hashing Files" style="zoom:80%;" />

After that, the investigation will begin. Details such as the files investigated and time elapsed will be stated at the top of the GUI.

![investigationStart](.\images\investigationStart.png)

### Event Log

To view the Event Log, click on the "View Event Log" button as highlighted below. This will display all the file system events that have been captured by The Watcher.

<img src=".\images\eventLog.png" alt="eventLog" style="zoom:80%;" />

### File Log

To view the File Log, click on the "View File Log" button as highlighted below. This will display all the files that are part of the investigation.

<img src=".\images\fileLog.png" alt="fileLog" style="zoom:80%;" />

You can select the classification of the file by selecting the dropdown and selecting "Submissible" or "Non-Submissible"

<img src=".\images\submissible.png" alt="submissible" style="zoom:80%;" />

You can also add/edit the notes for each file in the File Log by clicking on the "Edit" button beside the file.

<img src=".\images\addNotes.png" alt="addNotes" style="zoom:80%;"/>

<img src=".\images\noteAdded.png" alt="noteAdded" style="zoom:80%;" />

You can view the changes made to the metadata of the file by clicking on the "View" button beside the file.

 <img src=".\images\viewChanges.png" alt="viewChanges" style="zoom:80%;" />

Finally, you can take a screenshot to be tagged with a file by clicking on the "Take" button beside the file. This will take a screenshot that can be viewed later when the report is generated.

### Ending the Investigation and Generate report

When you are finished investigating the folder, you may end the investigation by clicking on the "End Investigation" button highlighted below.

![investigationEnd](.\images\investigationEnd.png)

After ending the investigation, you will have to select the folder in which you would like to generate the report in. Click on the "Select Report Folder" to select the folder to save the report to.

<img src=".\images\selectReportFolder.png" alt="selectReportFolder" style="zoom:80%;" />

<img src=".\images\selectFolderForReport.png" alt="selectFolderForReport" style="zoom:80%;" />

Afterwards, the "Generate HTML report" button should become active. Click on it to generate the HTML report that will be stored in the folder specified.

<img src=".\images\generateReport.png" alt="generateReport" style="zoom:80%;" />

<img src=".\images\reportFolderHTML.png" alt="reportFolderHTML" style="zoom:80%;" />
