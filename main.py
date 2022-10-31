import tkinter as tk
from tkinter import filedialog
import time
import os
import threading
from datetime import datetime

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Label(self,text="Select the folder that will be used in the investigation.").pack(fill="both", expand=True)
        tk.Label(self,textvariable= controller.selectedFolder).pack(fill="both", expand=True)
        tk.Button(self,text="Select Folder", command=lambda:[BeginInvestigation(controller)]).pack(fill="both", expand=True)
        tk.Button(self,text="Begin Investigation", command=lambda:[controller.ShowFrame(EventLog)]).pack(fill="both", expand=True)

class EventLog(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        tk.Button(self,text="View Event Log", command=lambda:[controller.ShowFrame(EventLog)]).grid(row=0, column=2, sticky="ew")
        tk.Button(self,text="View File Log", command=lambda:[controller.ShowFrame(FileLog)]).grid(row=1, column=2, sticky="ew")
        Title = tk.Label(self, text="Event Log").grid(row=3, column=2, sticky="ew")
        tk.Label(self,textvariable= controller.totalFileCount).grid(row=4, column=2, sticky="ew")
        tk.Label(self,textvariable= controller.selectedFolder).grid(row=5, column=2, sticky="ew")
        tk.Label(self,textvariable= controller.startTime).grid(row=6, column=2, sticky="ew")

        # Timer to track investigation
        tk.Label(self,textvariable= controller.timer).grid(row=7, column=2, sticky="ew")
        

        # Table to display event logs
        data = [
            # Time, Filename, Action, Notes, Active
            [1000,   "hello.py", "action 1", "notes 1", True],
            [1345,   "bomb.txt", "action 2", "notes 2",  False],
            [1711,   ".gitignore", "action 3", "notes 3",  True],
            ]

        # Buttons to do stuff
        tk.Button(self, text="Append", command=lambda newFile=[1234, "newfile", "action ?", "notes ?",  True], eventlog=data: self.appendFileEntry(newFile,eventlog)).grid(row=8, column=2)
        tk.Button(self, text="Debug list", command=lambda eventlog=data: self.debugShowlist(eventlog)).grid(row=9, column=2)

        # Button to end investigation, to be at bottom
        tk.Button(self,text="End Investigation", command=lambda:[EndInvestigation(controller)]).grid(row=10, column=2, sticky="ew")

        self.grid_columnconfigure(1, weight=1)
        tk.Label(self, text="Time", anchor="w").grid(row=11, column=0, sticky="ew")
        tk.Label(self, text="Filename", anchor="w").grid(row=11, column=1, sticky="ew")
        tk.Label(self, text="Action", anchor="w").grid(row=11, column=2, sticky="ew")
        tk.Label(self, text="Notes", anchor="w").grid(row=11, column=3, sticky="ew")
        tk.Label(self, text="View Change", anchor="w").grid(row=11, column=4, sticky="ew")

        rows = 12
        for (timeModified, name, action, notes, active) in data:
            nr_label = tk.Label(self, text=str(timeModified), anchor="w")
            name_label = tk.Label(self, text=name, anchor="w")
            actionLabel = tk.Label(self, text=action, anchor="w")
            notesLabel = tk.Label(self, text=notes, anchor="w")
            viewChangeButton = tk.Button(self, text="Click to View", command=lambda name=name: self.viewChange(name))

            nr_label.grid(row=rows, column=0, sticky="nw")
            name_label.grid(row=rows, column=1, sticky="nw")
            actionLabel.grid(row=rows, column=2, sticky="nw")
            notesLabel.grid(row=rows, column=3, sticky="nw")
            viewChangeButton.grid(row=rows, column=4, sticky="nw")

            rows += 1

        

    def delete(self, name):
        print("deleting...file=", name)

    def appendFileEntry(self, newFile, eventlog):
        print("Appending...", newFile)
        eventlog.append(newFile)


    def viewChange(self, name):
        print("Viewing change of file", name)

    def debugShowlist(self, data):
        print(data)
        
class FileLog(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        Title = tk.Label(self, text="File Log").pack(fill="both", expand=True)

class Report(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        Title = tk.Label(self, text="Investigation Report").pack(fill="both", expand=True)

class Windows(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.selectedFolder = tk.StringVar()
        self.selectedFolder.set("Selected folder: ")
        self.investigationActive = tk.BooleanVar()
        self.investigationActive.set(False)
        self.totalFileCount = tk.StringVar()
        self.selectedFolder.set("Total files investigated: ")
        self.startTime = tk.StringVar()
        self.timer = tk.StringVar()

        self.wm_title("The Watcher")
        container = tk.Frame(self, height=400, width=600)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary of frames to manage the different pages
        self.frames = {}

        for F in (MainMenu, EventLog, FileLog, Report):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Using a method to switch frames
        self.ShowFrame(MainMenu)

    # To swap between frames
    def ShowFrame(self, cont):
        frame = self.frames[cont]
        # raises the current frame to the top
        frame.tkraise()

def countFiles(filepath):
    counter = 0
    for path in os.listdir(filepath):
        if os.path.isfile(os.path.join(filepath, path)):
            counter += 1
    return counter

def Timer(controller, starttime):
    while controller.investigationActive.get() == True:
        currenttime = int(round(time.time() * 100)) - starttime
        controller.timer.set('Time elapsed: {:02d}:{:02d}:{:02d}'.format((currenttime // 100) // 60 // 60, (currenttime // 100) // 60,(currenttime // 100) % 60))
        time.sleep(1)
    print("Timer exited")

# To start investigation
def BeginInvestigation(controller):
    global selectedFolder
    folderName = filedialog.askdirectory()
    controller.selectedFolder.set("Selected folder: "+folderName)
    controller.investigationActive.set(True)
    controller.totalFileCount.set("Total files investigated: " + '0' + '/' + str(countFiles(folderName)))
    now = datetime.now()
    controller.startTime.set("Start time: " + now.strftime("%d/%m/%Y %H:%M:%S"))
    starttime = int(round(time.time() * 100))
    timerThread = threading.Thread(target=Timer, args=(controller, starttime), daemon=True)
    timerThread.start()

def EndInvestigation(controller):
    controller.investigationActive.set(False)
    controller.ShowFrame(Report)

if __name__ == "__main__":
    investigationActive = False

    mainProgram = Windows()
    mainProgram.mainloop()