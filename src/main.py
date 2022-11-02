import tkinter as tk
from tkinter import StringVar
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
        tk.Button(self,text="Select Folder", command=lambda:[self.FolderSelect(controller)]).pack(fill="both", expand=True)
        self.startButton = tk.Button(self,text="Begin Investigation", state="disabled", command=lambda:[controller.BeginInvestigation()])
        self.startButton.pack(fill="both", expand=True)

    # Start loading screen
    def addNotes(self, itemno, controller):
        window = tk.Frame()
        #Create a Toplevel window
        popup= tk.Toplevel(window)
        popup.geometry("750x250")

        #Create an Entry Widget in the Toplevel window
        noteEdit= tk.Entry(popup)
        noteEdit.insert(0, controller.fileData[itemno-1][3].get())
        noteEdit.place(width=400, height=150)

        #Create a Button Widget in the Toplevel Window
        button= tk.Button(popup, text="Done", command=lambda:self.editNotes(popup,noteEdit.get(),itemno, controller))
        button.pack(side = "bottom", pady=5)

    # Prompts user to select folder
    def FolderSelect(self, controller):
        folderName = filedialog.askdirectory()
        controller.investigationActive.set(True)

        # Set start button to be active
        self.startButton["state"] = "normal"


class FileLog(tk.Frame):
    def __init__(self, parent, controller):
        self.rowNo = tk.IntVar()
        self.rowNo.set(1)

        tk.Frame.__init__(self, parent)
        tk.Button(self,text="View Event Log", command=lambda:[controller.ShowFrame(EventLog)]).pack(fill="both", expand=True)
        tk.Button(self,text="View File Log", command=lambda:[controller.ShowFrame(FileLog)]).pack(fill="both", expand=True)
        Title = tk.Label(self, text="File Log").pack(fill="both", expand=True)
        tk.Label(self,textvariable= controller.investigatedFileCountString).pack(fill="both", expand=True)
        tk.Label(self,textvariable= controller.selectedFolder).pack(fill="both", expand=True)
        tk.Label(self,textvariable= controller.startTime).pack(fill="both", expand=True)

        # Timer to track investigation
        tk.Label(self,textvariable= controller.timer).pack(fill="both", expand=True)
        tk.Button(self,text="End Investigation", command=lambda:[controller.EndInvestigation()]).pack(fill="both", expand=True)

        # Create file table
        self.canvas = tk.Canvas(self, borderwidth=0, background="#FAF9F6")
        self.fileTableFrame = tk.Frame(self.canvas, background="#FAF9F6")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.frame_id = self.canvas.create_window(0, 0, window=self.fileTableFrame, anchor="nw",tags="self.fileTableFrame")

        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.fileTableFrame.bind("<Configure>", self.onFrameConfigure)

        # Headers
        tk.Label(self.fileTableFrame, text="No.", anchor="w", background="#FAF9F6").grid(row=0, column=0)
        tk.Label(self.fileTableFrame, text="File", anchor="w", background="#FAF9F6").grid(row=0, column=1)
        tk.Label(self.fileTableFrame, text="Classification", anchor="w", background="#FAF9F6").grid(row=0, column=2)
        tk.Label(self.fileTableFrame, text="Notes", anchor="w", background="#FAF9F6").grid(row=0, column=3)
        tk.Label(self.fileTableFrame, text="Edit", anchor="w", background="#FAF9F6").grid(row=0, column=4)

        self.populateData(controller)

        # Test button to append new entry
        #tk.Button(self, text="Append", anchor="w", command=lambda:[self.addNewFile([0, 1, 2, tk.StringVar()], controller)], background="#FAF9F6").pack(side="bottom")

    # Populate table with take data, to remove before deployment
    def populateData(self, controller):

        self.fileTableFrame.grid_columnconfigure(0, weight=1)

        options = [
            "Submissible",
            "Non-Submissible"
        ]

        # Populate table
        for row in controller.fileData:
            selectSubmissibility = StringVar()
            currentRowNo = self.rowNo.get()

            fileNo = tk.Label(self.fileTableFrame, text=row[0], anchor="w", background="#FAF9F6")
            fileNo.grid(row=currentRowNo, column=0, sticky="ew")
            tk.Label(self.fileTableFrame, text=row[1], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=1, sticky="ew")
            selectSubmissibility.set("Click to select")
            tk.OptionMenu( self.fileTableFrame , selectSubmissibility , *options).grid(row=currentRowNo, column=2)
            tk.Label(self.fileTableFrame, textvariable=row[3], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=3, sticky="ew")
            tk.Button(self.fileTableFrame, text="Edit", command=lambda itemNo = currentRowNo:[self.addNotes(itemNo, controller)]).grid(row=currentRowNo, column=4, sticky="ew")

            self.rowNo.set(currentRowNo+1)

        currentRowNo = self.rowNo.get()


    def UpdateSubmissibility(self, rowNo):
        print(rowNo)
        return None

    # To add a new file item:
    def addNewFile(self, data, controller):
        controller.fileData.append(data)
        currentRowNo = self.rowNo.get()
        selectSubmissibility = StringVar()

        options = [
            "Submissible",
            "Non-Submissible"
        ]

        fileNo = tk.Label(self.fileTableFrame, text=data[0], anchor="w", background="#FAF9F6")
        fileNo.grid(row=currentRowNo, column=0, sticky="ew")
        tk.Label(self.fileTableFrame, text=data[1], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=1, sticky="ew")
        selectSubmissibility.set("Click to select")
        tk.OptionMenu( self.fileTableFrame , selectSubmissibility , *options).grid(row=currentRowNo, column=2)
        tk.Label(self.fileTableFrame, textvariable=data[3], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=3, sticky="ew")
        tk.Button(self.fileTableFrame, text="Edit", command=lambda itemNo = currentRowNo:[self.addNotes(itemNo, controller)]).grid(row=currentRowNo, column=4, sticky="ew")

        self.rowNo.set(currentRowNo+1)

    # Edit the notes for the specific row
    def editNotes(self, popup, text, itemno, controller):
        controller.fileData[itemno-1][3].set(text)
        popup.destroy()

    # Open up popup window to prompt investigator to add notes
    def addNotes(self, itemno, controller):
        window = tk.Frame()
        #Create a Toplevel window
        popup= tk.Toplevel(window)
        popup.geometry("750x250")

        #Create an Entry Widget in the Toplevel window
        noteEdit= tk.Entry(popup)
        noteEdit.insert(0, controller.fileData[itemno-1][3].get())
        noteEdit.place(width=400, height=150)

        #Create a Button Widget in the Toplevel Window
        button= tk.Button(popup, text="Done", command=lambda:self.editNotes(popup,noteEdit.get(),itemno, controller))
        button.pack(side = "bottom", pady=5)

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # Function to resize frame to fit the canvas
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.frame_id, width=event.width)
        
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
        tk.Button(self,text="End Investigation", command=lambda:[controller.EndInvestigation()]).pack(fill="both", expand=True)

class Report(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        Title = tk.Label(self, text="Investigation Report").pack(fill="both", expand=True)

class Controller(tk.Tk):
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

        # Data for filelog and event log (To remove data before deployment)
        self.fileData = [
            [1, "testfile.mp4", "Submissible", tk.StringVar()],
            [2, "testfile1.mp4", "Submissible", tk.StringVar()],
            [3, "testfile2.mp4", "Non-Submissible", tk.StringVar()],
            [4, "testfile3.mp4", "Submissible", tk.StringVar()],
            [5, "testfile1.mp4", "Submissible", tk.StringVar()],
            [6, "testfile2.mp4", "Non-Submissible", tk.StringVar()],
        ]

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

    # Timer function for the investigation
    def Timer(self, starttime):
        while self.investigationActive.get() == True:
            currenttime = int(round(time.time() * 100)) - starttime
            self.timer.set('Time elapsed: {:02d}:{:02d}:{:02d}'.format((currenttime // 100) // 60 // 60, (currenttime // 100) // 60,(currenttime // 100) % 60))
            time.sleep(1)
        print("Timer exited")

    # File counter function to count number of files within folder and all subfolders.
    def countFiles(self, filepath):
        counter = sum([len(files) for r, d, files in os.walk(filepath)])
        return counter

    # To start investigation
    def BeginInvestigation(self):
        now = datetime.now()
        self.startTime.set("Start time: " + now.strftime("%d/%m/%Y %H:%M:%S"))
        starttime = int(round(time.time() * 100))
        
        # Start timer thread
        timerThread = threading.Thread(target=self.Timer, args=[starttime], daemon=True)
        timerThread.start()

        # Set file count
        self.totalFileCount.set(self.countFiles(self.selectedFolder.get()))
        self.investigatedFileCountString.set("Files investigated: "+ "0/" + str(self.totalFileCount.get()))
        self.selectedFolder.set("Selected folder: "+ self.selectedFolder.get())

        self.ShowFrame(EventLog)

    # End of investigation, direct user to report page
    def EndInvestigation(self):
        self.investigationActive.set(False)
        self.ShowFrame(Report)

# To be called when a file has been successfully investigated.
def FileInvestigated(controller):
    fileCount = controller.investigatedFileCount.get()+1
    controller.investigatedFileCount.set(fileCount)
    controller.investigatedFileCountString.set("Total files investigated: " + str(fileCount) + '/' + str(controller.totalFileCount.get()))


if __name__ == "__main__":
    investigationActive = False

    mainProgram = Controller()
    mainProgram.geometry("800x400")
    mainProgram.mainloop()