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
        tk.Button(self,text="View Event Log", command=lambda:[controller.ShowFrame(EventLog)]).pack(fill="both", expand=True)
        tk.Button(self,text="View File Log", command=lambda:[controller.ShowFrame(FileLog)]).pack(fill="both", expand=True)
        Title = tk.Label(self, text="Event Log").pack(fill="both", expand=True)
        tk.Label(self,textvariable= controller.investigatedFileCountString).pack(fill="both", expand=True)
        tk.Label(self,textvariable= controller.selectedFolder).pack(fill="both", expand=True)
        tk.Label(self,textvariable= controller.startTime).pack(fill="both", expand=True)

        # Timer to track investigation
        tk.Label(self,textvariable= controller.timer).pack(fill="both", expand=True)
        tk.Button(self,text="End Investigation", command=lambda:[EndInvestigation(controller)]).pack(fill="both", expand=True)

        # Create events table
        # Headers
        tk.Label(self, text="File", anchor="w").pack(side="left")
        tk.Label(self, text="Classification", anchor="w").pack(side="left")
        tk.Label(self, text="Notes", anchor="w").pack(side="left")
        tk.Label(self, text="Edit", anchor="w").pack(side="left")

        # Data
        data = [
            ["testfile.mp4", "Submissible", "Notes"]
        ]

        # Populate table
        for row in data:
            tk.Label(self, text=row[0], anchor="w").pack(side="left")
            tk.Label(self, text="Classification", anchor="w").pack(side="left")
            tk.Label(self, text=row[2], anchor="w").pack(side="left")
            tk.Button(self,text="Edit", command=lambda:[controller.ShowFrame(FileLog)]).pack(side="left")
        
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
        self.investigatedFileCount = tk.IntVar()
        self.totalFileCount = tk.IntVar()
        self.investigatedFileCountString = tk.StringVar()
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

# File counter function to count number of files within folder and all subfolders.
def countFiles(filepath):
    counter = 0
    for path in os.listdir(filepath):
        if os.path.isfile(os.path.join(filepath, path)):
            counter += 1
    return counter

# Timer function for the investigation
def Timer(controller, starttime):
    while controller.investigationActive.get() == True:
        currenttime = int(round(time.time() * 100)) - starttime
        controller.timer.set('Time elapsed: {:02d}:{:02d}:{:02d}'.format((currenttime // 100) // 60 // 60, (currenttime // 100) // 60,(currenttime // 100) % 60))
        time.sleep(1)
    print("Timer exited")

# To be called when a file has been successfully investigated.
def FileInvestigated(controller):
    fileCount = controller.investigatedFileCount.get()+1
    controller.investigatedFileCount.set(fileCount)
    controller.investigatedFileCountString.set("Total files investigated: " + str(fileCount) + '/' + str(controller.totalFileCount.get()))

# To start investigation
def BeginInvestigation(controller):
    global selectedFolder
    folderName = filedialog.askdirectory()
    controller.selectedFolder.set("Selected folder: "+folderName)
    controller.investigationActive.set(True)
    controller.totalFileCount.set(countFiles(folderName))
    controller.investigatedFileCountString.set("Files investigated: "+ "0/" + str(controller.totalFileCount.get()))
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