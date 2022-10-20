from genericpath import isfile
from tracemalloc import start
import PySimpleGUI as gui
import os
from datetime import datetime
import time
import threading

def appendToList(window, the_list):
    """Testing if I can add stuff to the list"""
    the_list.append(["test", "test", "test", "test", "test"])
    window["-TABLE-"].update(values=the_list)
    

def countFiles(filepath):
    counter = 0
    for path in os.listdir(filepath):
        if os.path.isfile(os.path.join(filepath, path)):
            counter += 1
    return counter

def updateTimer(window, starttime):
    global investigationActive
    while investigationActive:
        currenttime = int(round(time.time() * 100)) - starttime
        window['TimeElapsed'].update('Time elapsed: {:02d}:{:02d}'.format((currenttime // 100) // 60,(currenttime // 100) % 60))


# Theme
gui.theme('DarkAmber')

InvestigationHeader = [
    [gui.Button('Events'), gui.Button('Files')],
    [gui.Text(key = "FileCount")],
    [gui.Text(key = "SelectedFolder")],
    [gui.Text("Watchdog is running... ")],
    [gui.Text(key="StartTime")],
    [gui.Text(key="TimeElapsed")],
    [gui.Button("End investigation")]
]

FileLog = [
    [gui.Text("This is the file log page.")],
]

filelist = [
        ["fuck", "this", "shit", "im", "out"],
        ["coffee", "tea", "whiskey", "and", "me"],
        ["ded", "meeeep", "one espresso depresso please thankyou", "meat bicycle", "chocolate milo shake"]
    ]

filelist_headings = ["Time", "Filename", "Action", "Notes", "View Change"]

EventLog = [
        [gui.Table(values=filelist,
                   headings=filelist_headings,
                   max_col_width=100,
                   auto_size_columns=True,
                   display_row_numbers=False,
                   justification="right",
                   num_rows=10,
                   key="-TABLE-",
                   row_height=35)],
        [gui.Button("Append")]
        
    ]

MainMenu = [
    [gui.Text("Select the hard drive/ folder that will be investigated.")],
    [gui.Text("Select Folder:"), gui.Input(key="-IN-"), gui.FolderBrowse()],
    [gui.Exit(), gui.Button("Commence investigation")],
]

ProgramController = [
    [gui.Column(MainMenu, key='MainMenu'),gui.Column(InvestigationHeader, visible=False, key='InvestigationHeader')],
    [gui.Column(FileLog, visible=False, key='FileLog'), gui.Column(EventLog, visible=False, key='EventLog')]
]

window = gui.Window("The Watcher", ProgramController)

# Selected folder for investigation
selectedfolder = ""
investigationActive = False

totalfilecount = 0
# Counter for investigated files
filecount = 0
currenttime = 0


while True:
    event, values = window.read()
    selectedfolder = values['Browse']
    
    # User exit application
    if event in (gui.WINDOW_CLOSED, "Exit"):
        investigationActive = False
        break

    # When the user starts an investigation
    if event == "Commence investigation":
        investigationActive = True
        totalfilecount = countFiles(selectedfolder)
        window["MainMenu"].update(visible=False)
        window['InvestigationHeader'].update(visible=True)
        window['EventLog'].update(visible=True)
        starttime = datetime.now()
        window['StartTime'].update("Start time: "+ starttime.strftime("%d/%m/%Y %H:%M:%S"))
        starttime = int(round(time.time() * 100))
        timerThread = threading.Thread(target=updateTimer, args=(window, starttime))
        timerThread.start()
    
    # While investigation is active
    if investigationActive:
        window['FileCount'].update("Files investigated: " + str(filecount) + '/' + str(totalfilecount))
        window['SelectedFolder'].update("Folder under investigation: "+selectedfolder)
        if event == "Events":
            window['FileLog'].update(visible=False)
            window['EventLog'].update(visible=True)        
        if event == "Files":
            window['FileLog'].update(visible=True)
            window['EventLog'].update(visible=False)           

    # When the user clicks on end investigation, it should redirect to the report page. For now, it will close the program.
    if event in (gui.WINDOW_CLOSED, "End investigation"):
        investigationActive = False
        break

    if event == "Append":
        appendToList(window, filelist)

window.close()