import tkinter as tk
from tkinter import StringVar, ttk
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
        tk.Button(self,text="Select Folder", command=lambda:[FolderSelect(controller,self)]).pack(fill="both", expand=True)
        self.startButton = tk.Button(self,text="Begin Investigation", state="disabled", command=lambda:[BeginInvestigation(controller)])
        self.startButton.pack(fill="both", expand=True)

class EventLog(tk.Frame):
    def __init__(self, parent, controller):
        self.rowNo = tk.IntVar()
        self.rowNo.set(1)

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

        # Create file table
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.fileTableFrame = tk.Frame(self.canvas, background="#ffffff")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.fileTableFrame, anchor="nw",
                                  tags="self.fileTableFrame")

        self.fileTableFrame.bind("<Configure>", self.onFrameConfigure)

        # Data
        self.fileData = [
            [1, "testfile.mp4", "Submissible", "This file was determined to be useless."],
            [2, "testfile1.mp4", "Submissible", "This file was determined to be useless."],
            [3, "testfile2.mp4", "Non-Submissible", "This file was determined to be useless."],
            [4, "testfile3.mp4", "Submissible", "This file was determined to be useless."],
            [5, "testfile1.mp4", "Submissible", "This file was determined to be useless."],
            [6, "testfile2.mp4", "Non-Submissible", "This file was determined to be useless."],
        ]

        # Headers
        tk.Label(self.fileTableFrame, text="No.", anchor="w").grid(row=0, column=0)
        tk.Label(self.fileTableFrame, text="File", anchor="w").grid(row=0, column=1)
        tk.Label(self.fileTableFrame, text="Classification", anchor="w").grid(row=0, column=2)
        tk.Label(self.fileTableFrame, text="Notes", anchor="w").grid(row=0, column=3)
        tk.Label(self.fileTableFrame, text="Edit", anchor="w").grid(row=0, column=4)

        self.populateData()

    def UpdateSubmissibility(self, rowNo):
        print(rowNo)
        return None

    def populateData(self):
        # Populate table
        for row in self.fileData:
            self.submissibility = StringVar()
            currentRowNo = self.rowNo.get()
            tk.Label(self.fileTableFrame, text=row[0], anchor="w").grid(row=currentRowNo, column=0)
            tk.Label(self.fileTableFrame, text=row[1], anchor="w").grid(row=currentRowNo, column=1)
            tk.Radiobutton(self.fileTableFrame, variable=self.submissibility, value="Submissible", text="Submissible", command=self.UpdateSubmissibility(currentRowNo)).grid(row=currentRowNo, column=2)
            tk.Radiobutton(self.fileTableFrame, variable=self.submissibility, value="Non-Submissible", text="Non-Submissible", command=self.UpdateSubmissibility(currentRowNo)).grid(row=currentRowNo, column=3)
            tk.Label(self.fileTableFrame, text=row[3], anchor="w").grid(row=currentRowNo, column=4)
            tk.Button(self.fileTableFrame, text="Edit", command=lambda:[self.addNotes()]).grid(row=currentRowNo, column=5)
            self.rowNo.set(currentRowNo+1)

    # To add a new file item:
    def addNewFile(self, data):
        filedata = self.fileData
        self.fileData.append(data)
        currentRowNo = self.rowNo.get()
        tk.Label(self.fileTableFrame, text=data[0], anchor="w").grid(row=currentRowNo, column=0)
        tk.Label(self.fileTableFrame, text=data[1], anchor="w").grid(row=currentRowNo, column=1)
        tk.Radiobutton(self.fileTableFrame, text="Submissible", command=self.UpdateSubmissibility(currentRowNo)).grid(row=currentRowNo, column=2)
        tk.Radiobutton(self.fileTableFrame, text="Non-Submissible", command=self.UpdateSubmissibility(currentRowNo)).grid(row=currentRowNo, column=3)
        tk.Label(self.fileTableFrame, text=data[3], anchor="w").grid(row=currentRowNo, column=3)
        tk.Button(self.fileTableFrame, text="Edit", command=lambda:[self.addNotes()]).grid(row=currentRowNo, column=4)
        self.rowNo.set(currentRowNo+1)

    def addNotes(self):
        self.fileData

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
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
    counter = sum([len(files) for r, d, files in os.walk(filepath)])
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

# Prompts user to select folder
def FolderSelect(controller, menuframe):
    folderName = filedialog.askdirectory()
    controller.selectedFolder.set("Selected folder: "+folderName)
    controller.investigationActive.set(True)

    # Set start button to be active
    menuframe.startButton["state"] = "normal"

# To start investigation
def BeginInvestigation(controller):
    now = datetime.now()
    controller.startTime.set("Start time: " + now.strftime("%d/%m/%Y %H:%M:%S"))
    starttime = int(round(time.time() * 100))
    
    # Start timer thread
    timerThread = threading.Thread(target=Timer, args=(controller, starttime), daemon=True)
    timerThread.start()

    # Set file count
    controller.totalFileCount.set(countFiles(controller.selectedFolder.get().replace("Selected folder: ",'')))
    controller.investigatedFileCountString.set("Files investigated: "+ "0/" + str(controller.totalFileCount.get()))

    controller.ShowFrame(EventLog)

def EndInvestigation(controller):
    controller.investigationActive.set(False)
    controller.ShowFrame(Report)

if __name__ == "__main__":
    investigationActive = False

    mainProgram = Windows()
    mainProgram.mainloop()