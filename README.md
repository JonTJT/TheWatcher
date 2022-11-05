# TheWatcher :eyes:

## Introduction
There is insufficient focus on proper auditing and documentation when conducting digital forensics investigation.

There is an oversaturated market for tools to conduct the analysis of evidence, and few existing solutions exist that focus on the documentation and auditing of the investigation process. This can result in possible tampering or general mishandling of the exhibits during an investigation, which discredits the investigator and the gathered evidence. As a solution, our team has come up with “**The Watcher**”. A system that tracks events and documents every step of the investigation process.

## Project Members:
Keefe - https://github.com/keefelee <br>
Wesley - https://github.com/wesleychiau <br>
Meng Rong - https://github.com/GMengRong <br>
Jon - https://github.com/JonTJT <br>

## Features:
- Monitor start and end time of investigation session
- Log and show file system changes during investigation
- Allow investigators to provide documentation when analysing files
- Show what changed in file (hex compare)
- Mark files and submissible or non-submissible evidence

## Benefits:
- Provide forensic investigators with an audit trial to bolster their credibility and accountability when presenting evidence
- Help document the investigative process to help investigators
- Provide a perspicuous view of the steps and finding of the investigation


## Installation:
1. Clone the latest version of the repository from the "main branch at https://github.com/JonTJT/TheWatcher/tree/main<br>
``` git clone "https://github.com/JonTJT/TheWatcher.git ```
2. After cloning the repository, go to the repository and install the requirements. <br>
``` pip install -r src/requirements.txt ```
3. To run the program, run main.py in the src folder (Please take note to run the program from the src folder)
``` python main.py ```
