import tkinter as tk
from tkinter import StringVar
from tkinter import filedialog
import time
import os
import threading
from datetime import datetime
import pyautogui
import pytz
import hashlib
import multiprocessing
import shutil
import meta
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        self.folderSelected = tk.BooleanVar()
        self.folderSelected.set(False)
        tk.Frame.__init__(self, parent)
        tk.Label(self,text="Select the folder that will be used in the investigation.").pack(fill="both", expand=True)
        tk.Label(self,textvariable= controller.selectedFolder).pack(fill="both", expand=True)
        tk.Button(self,text="Select Investigation Folder", command=lambda:[self.FolderSelect(controller)]).pack(fill="both", expand=True)
        self.startButton = tk.Button(self,text="Begin Investigation", state="disabled", command=lambda:[controller.BeginInvestigation()])
        self.startButton.pack(fill="both", expand=True)

    # Prompts user to select folder
    def FolderSelect(self, controller):
        self.startButton["state"] = "disabled"
        folderName = filedialog.askdirectory()
        if os.path.isdir(folderName):
            self.folderSelected.set(True)
            controller.selectedFolder.set(folderName)
        else:
            self.folderSelected.set(False)

        # Set start button to be active
        if self.folderSelected.get():
            self.startButton["state"] = "normal"

    # Check status of completion for loading
    def LoadingTracker(self, controller):
        while self.investigationActive.get() == False:
            i = 1

class MonitorFolder(FileSystemEventHandler):
    def __init__(self, hash_dict, eventLog):
        self.hash_dict = hash_dict
        self.eventLog = eventLog

    def hash_file(self,file):
        try:
            result = subprocess.check_output(f'certutil -hashfile "{file}" MD5', shell=True)
            hash = result.splitlines()[1]
        except Exception as e:
            print(e)
            return ""
        return hash.decode('utf-8')

    def on_file_open(self, file):
        # Check if open or modified
        filehash = self.hash_file(file)
        try: 
            if filehash != self.hash_dict[file]:
                self.hash_dict[file] = filehash
                self.eventLog.addNewEvent([file,"File Modified"])
        except Exception as e:
            print("Something went wrong:" , e)

    def on_created(self, event):
        self.hash_dict[event.src_path] = self.hash_file(event.src_path)
        self.eventLog.addNewEvent([event.src_path,"File Created"])

    def on_modified(self, event):
        if os.path.isfile(event.src_path):
            self.on_file_open(event.src_path)

    def on_deleted(self, event):
        self.hash_dict.pop(event.src_path)
        self.eventLog.addNewEvent([event.src_path,"File Deleted"])

    def on_moved(self,event):
        self.hash_dict[event.dest_path] = self.hash_file(event.dest_path)
        self.hash_dict.pop(event.src_path)
        self.eventLog.addNewEvent([event.dest_path, f"{event.src_path} Moved to {event.dest_path}"])

class FileLog(tk.Frame):
    def __init__(self, parent, controller):
        self.rowNo = tk.IntVar()
        self.rowNo.set(1)

        tk.Frame.__init__(self, parent)
        tk.Button(self,text="View Event Log", command=lambda:[controller.ShowFrame(EventLog)]).pack(fill="x")
        tk.Button(self,text="View File Log", command=lambda:[controller.ShowFrame(FileLog)]).pack(fill="x")
        Title = tk.Label(self, text="File Log").pack(fill="x")
        tk.Label(self,textvariable= controller.investigatedFileCountString).pack(fill="x")
        tk.Label(self,textvariable= controller.selectedFolder).pack(fill="x")
        tk.Label(self,textvariable= controller.startTime).pack(fill="x")

        # Timer to track investigation
        tk.Label(self,textvariable= controller.timer).pack(fill="x")
        tk.Button(self,text="End Investigation", command=lambda:[controller.EndInvestigation()]).pack(fill="x")

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
        tk.Label(self.fileTableFrame, text="No.", anchor="w", background="#FAF9F6").grid(row=0, column=0, sticky="ew")
        tk.Label(self.fileTableFrame, text="File", anchor="w", background="#FAF9F6").grid(row=0, column=1, sticky="ew")
        tk.Label(self.fileTableFrame, text="Classification", anchor="w", background="#FAF9F6").grid(row=0, column=2, sticky="ew")
        tk.Label(self.fileTableFrame, text="Notes", anchor="w", background="#FAF9F6").grid(row=0, column=3, sticky="ew")
        tk.Label(self.fileTableFrame, text="Edit", anchor="w", background="#FAF9F6").grid(row=0, column=4, sticky="ew")
        tk.Label(self.fileTableFrame, text="View Changes", anchor="w", background="#FAF9F6").grid(row=0, column=5, sticky="ew")
        tk.Label(self.fileTableFrame, text="Screenshot", anchor="w", background="#FAF9F6").grid(row=0, column=6, sticky="ew")

        onInvestigationStartThread = threading.Thread(target=self.WaitForInvestigation, args=[controller], daemon=True)
        onInvestigationStartThread.start()

    # Timer function for the investigation
    def WaitForInvestigation(self, controller):
        while controller.investigationActive.get() == False:
            time.sleep(0.1)
        self.populateData(controller)

    # Populate table
    def populateData(self, controller):

        self.fileTableFrame.grid_columnconfigure(0, weight=1)
        self.fileTableFrame.grid_columnconfigure(1, weight=3)
        self.fileTableFrame.grid_columnconfigure(2, weight=1)
        self.fileTableFrame.grid_columnconfigure(3, weight=1)
        self.fileTableFrame.grid_columnconfigure(4, weight=1)
        self.fileTableFrame.grid_columnconfigure(5, weight=1)
        self.fileTableFrame.grid_columnconfigure(6, weight=1)

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
            tk.Label(self.fileTableFrame, text=row[1], anchor="w", background="#FAF9F6", wraplength=200).grid(row=currentRowNo, column=1, sticky="ew")
            selectSubmissibility.set("Click to select")
            submissibility = tk.OptionMenu( self.fileTableFrame, selectSubmissibility, command= lambda submissibility = selectSubmissibility , itemno = currentRowNo :[self.UpdateSubmissibility(itemno, controller, submissibility)], *options)
            submissibility.grid(row=currentRowNo, column=2, sticky="ew")
            tk.Label(self.fileTableFrame, textvariable=row[3], anchor="w", background="#FAF9F6", wraplength=400).grid(row=currentRowNo, column=3, sticky="ew")
            tk.Button(self.fileTableFrame, text="Edit", command=lambda itemNo = currentRowNo:[self.addNotes(itemNo, controller)]).grid(row=currentRowNo, column=4, sticky="ew")
            tk.Button(self.fileTableFrame, text="View", command=lambda itemNo = currentRowNo:[self.viewChanges(itemNo, controller)]).grid(row=currentRowNo, column=5, sticky="ew")
            tk.Button(self.fileTableFrame, text="Take", command=lambda x=row[0]:[self.addScreenshot(x, controller)], background="#FAF9F6").grid(row=currentRowNo, column=6, sticky="ew")

            self.rowNo.set(currentRowNo+1)

        currentRowNo = self.rowNo.get()

    # Set file submissibility
    def UpdateSubmissibility(self, rowNo, controller, submissibility):
        for item in controller.fileData:
            if item[0] == rowNo:
                item[2].set(submissibility)
        controller.FileInvestigated()

    # Open up popup window to prompt investigator to view metadata changes
    def viewChanges(self, itemno, controller):
        window = tk.Frame()
        #Create a Toplevel window
        popup= tk.Toplevel(window)
        popup.geometry("1000x600")
        data = []
        for item in controller.fileData:
            if item[0] == itemno:
                data = item
                break
        
        title = tk.Label(popup,text= "Metadata Comparison", font=("Helvetica Bold",18))
        title.pack(fill="both")
        title.grid(row=0, column=0, sticky="ew")
        
        curRow = 1
        #original data
        ogTitle = tk.Label(popup,text= "Original Metadata:", font=("Helvetica Bold",18))
        ogTitle.grid(row=curRow, column=0, sticky="ew")

        for key in data[4]:
            curRow += 1
            tk.Label(popup,text=key).grid(row=curRow, column=0, sticky="ew")
            tk.Label(popup,text=data[4][key]).grid(row=curRow, column=1, sticky="ew")

        #current data
        curResult = meta.fileMeta(data[1])
        curTitle = tk.Label(popup,text= "Current Metadata:", font=("Helvetica Bold",18))
        curRow += 1
        curTitle.grid(row=curRow, column=0, sticky="ew")

        for key in curResult:
            curRow += 1
            tk.Label(popup,text=key).grid(row=curRow, column=0, sticky="ew")
            tk.Label(popup,text=curResult[key]).grid(row=curRow, column=1, sticky="ew")

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

    def addScreenshot(self, rowNo, controller):
        # Minimize window
        controller.iconify()
        time.sleep(0.5)

        # Screenshot
        screenshot = pyautogui.screenshot()
        now = datetime.now()
        sgTime = pytz.timezone("Asia/Singapore")
        nowSgTime = sgTime.localize(now)
        filename = controller.fileData[rowNo-1][1].split('\\') #controller.fileData[rowNo-1][1] issue with filename if image path is not same directory as main.py
        screenshotName = controller.screenshotFolder + "\\" + filename[-1] + "_" + str(nowSgTime.strftime("%Y-%m-%d_%H.%M.%S")) + ".png"
        screenshot.save(screenshotName)
        controller.fileData[rowNo-1][5].append(screenshotName)

        # Open window
        time.sleep(0.5)
        controller.deiconify()

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # Function to resize frame to fit the canvas
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.frame_id, width=event.width)
        
class EventLog(tk.Frame):
    def __init__(self, parent, controller):
        self.eventRowNo = tk.IntVar()
        self.eventRowNo.set(1)
        self.controller = controller

        tk.Frame.__init__(self, parent)
        tk.Button(self,text="View Event Log", command=lambda:[controller.ShowFrame(EventLog)]).pack(fill="x")
        tk.Button(self,text="View File Log", command=lambda:[controller.ShowFrame(FileLog)]).pack(fill="x")
        Title = tk.Label(self, text="Event Log").pack(fill="x")
        tk.Label(self,textvariable= controller.investigatedFileCountString).pack(fill="x")
        tk.Label(self,textvariable= controller.selectedFolder).pack(fill="x")
        tk.Label(self,textvariable= controller.startTime).pack(fill="x")

        # Timer to track investigation
        tk.Label(self,textvariable= controller.timer).pack(fill="x")
        tk.Button(self,text="End Investigation", command=lambda:[controller.EndInvestigation()]).pack(fill="x")

        # Create file table
        self.canvas = tk.Canvas(self, borderwidth=0, background="#FAF9F6")
        self.eventsTableFrame = tk.Frame(self.canvas, background="#FAF9F6")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.frame_id = self.canvas.create_window(0, 0, window=self.eventsTableFrame, anchor="nw",
                                  tags="self.eventsTableFrame")

        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.eventsTableFrame.bind("<Configure>", self.onFrameConfigure)

        # Headers
        tk.Label(self.eventsTableFrame, text="No.", anchor="w", background="#FAF9F6").grid(row=0, column=0, sticky="ew")
        tk.Label(self.eventsTableFrame, text="Time", anchor="w", background="#FAF9F6").grid(row=0, column=1, sticky="ew")
        tk.Label(self.eventsTableFrame, text="File name and path", anchor="w", background="#FAF9F6").grid(row=0, column=2, sticky="ew") 
        tk.Label(self.eventsTableFrame, text="Event", anchor="w", background="#FAF9F6").grid(row=0, column=3, sticky="ew")

        self.eventsTableFrame.grid_columnconfigure(0, weight=1)
        self.eventsTableFrame.grid_columnconfigure(1, weight=1)
        self.eventsTableFrame.grid_columnconfigure(2, weight=2)
        self.eventsTableFrame.grid_columnconfigure(3, weight=2)
        
    # To add a new event item:
    def addNewEvent(self, data):
        controller=self.controller
        # Add timestamp and index to data
        now = datetime.now()
        data.insert(0,now.strftime("%d/%m/%Y %H:%M:%S"))
        currentRowNo = self.eventRowNo.get()
        data.insert(0,currentRowNo)

        # Add the new data to the database
        controller.eventData.append(data)

        tk.Label(self.eventsTableFrame, text=data[0], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=0, sticky="ew")
        tk.Label(self.eventsTableFrame, text=data[1], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=1, sticky="ew")
        tk.Label(self.eventsTableFrame, text=data[2], anchor="w", background="#FAF9F6", wraplength=400).grid(row=currentRowNo, column=2, sticky="ew")
        tk.Label(self.eventsTableFrame, text=data[3], anchor="w", background="#FAF9F6", wraplength=400).grid(row=currentRowNo, column=3, sticky="ew")
        
        self.eventRowNo.set(currentRowNo+1)

    def UpdateSubmissibility(self, rowNo):
        return None

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    # Function to resize frame to fit the canvas
    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.frame_id, width=event.width)

class Report(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.reportFolderSelected = tk.BooleanVar()
        self.reportFolderSelected.set(False)

        Title = tk.Label(self, text="Investigation Report").pack(fill="both", expand=True)
        tk.Button(self,text="Select Report Folder", command=lambda:[self.ReportFolderSelect(controller)]).pack(fill="both", expand=True)
        self.generateReport = tk.Button(self,state="disabled",text="Generate HTML report", command=lambda:[controller.GenerateReport(controller.selectedReportFolder.get())])
        self.generateReport.pack(fill="both", expand=True)

    # Prompts user to select folder to store report and all related files
    def ReportFolderSelect(self, controller):
        self.generateReport["state"] = "disabled"
        folderName = filedialog.askdirectory()
        if os.path.isdir(folderName):
            self.reportFolderSelected.set(True)
            controller.selectedReportFolder.set(folderName)
        else:
            self.reportFolderSelected.set(False)

        # Set start button to be active
        if self.reportFolderSelected.get():
            self.generateReport["state"] = "normal"

class Controller(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.selectedFolder = tk.StringVar()
        self.selectedReportFolder = tk.StringVar()
        self.investigationActive = tk.BooleanVar()
        self.investigationActive.set(False)
        self.investigatedFileCount = tk.IntVar()
        self.totalFileCount = tk.IntVar()
        self.investigatedFileCountString = tk.StringVar()
        self.startTime = tk.StringVar()
        self.timer = tk.StringVar()
        self.percentageCompletion = tk.IntVar()
        self.unreadableFileList = []

        self.hashDictMutex = multiprocessing.Lock()
        self.startHashDict = {}
        self.endHashDict = {}

        # Data for filelog and event log 
        self.fileData = []
        self.eventData = []

        # Create directory to save screenshots
        now = datetime.now()
        sgTime = pytz.timezone("Asia/Singapore")
        nowSgTime = sgTime.localize(now)
        self.screenshotFolder = "TheWatcherScreenshots" + "_" + str(nowSgTime.strftime("%Y-%m-%d_%H-%M-%S"))
        os.mkdir(self.screenshotFolder)

        self.wm_title("The Watcher")
        container = tk.Frame(self, height=400, width=600)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary of frames to manage the different pages
        self.frames = {}

        for F in (MainMenu, FileLog, Report):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Event Log 
        frame = EventLog(container,self)
        self.frames[EventLog] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        self.eventLog = frame

        # Using a method to switch frames
        self.ShowFrame(MainMenu)

    # To swap between frames
    def ShowFrame(self, cont):
        frame = self.frames[cont]
        # raises the current frame to the top
        frame.tkraise()
 
    # Timer function for the investigation
    def Timer(self, starttime, observer):
        while self.investigationActive.get() == True:
            currenttime = int(round(time.time() * 100)) - starttime
            self.timer.set('Time elapsed: {:02d}:{:02d}:{:02d}'.format((currenttime // 100) // 60 // 60, (currenttime // 100) // 60,(currenttime // 100) % 60))
            time.sleep(1)
        observer.stop()
        observer.join()

    # File counter function to count number of files within folder and all subfolders. 
    def countFiles(self, filepath):
        counter = 0
        for path, folders, files in os.walk(filepath):
            for file in files:
                counter += 1
                self.addNewFile(os.path.join(path, file))
        return counter

    def LoadingBar(self):
        #Create a Toplevel window
        loadingpopup= tk.Toplevel()
        loadingpopup.geometry("300x200")
        #Loading popup for entire program
        tk.Label(loadingpopup,text= "Collecting hashes of all files...").pack(fill="both", expand=True)
        tk.Label(loadingpopup,text= "Please wait").pack(fill="both", expand=True) 
        loadingpopup.update()
        checkProgressThread = threading.Thread(target=self.checkLoadingProgress, args=[loadingpopup], daemon=True)
        checkProgressThread.start()

    # To start investigation
    def BeginInvestigation(self):

        time.sleep(2)
        self.LoadingBar()
        now = datetime.now()
        self.startTime.set("Investigation start time: " + now.strftime("%d/%m/%Y %H:%M:%S"))
        starttime = int(round(time.time() * 100))

        # Set file count
        self.totalFileCount.set(self.countFiles(self.selectedFolder.get()))
        self.investigatedFileCountString.set("Files investigated: "+ "0/" + str(self.totalFileCount.get()))

        #Hash all the files before investigation
        self.hashMultithreading(1)
        
        if len(self.unreadableFileList) > 0:
            self.viewUnreadableFiles()

        event_handler = MonitorFolder(self.startHashDict, self.eventLog)
        observer = Observer()
        observer.schedule(event_handler, path=self.selectedFolder.get(), recursive=True)
        observer.start()
        print("Monitoring started")        

        self.selectedFolder.set("Selected folder: "+ self.selectedFolder.get())

        # Start timer thread
        timerThread = threading.Thread(target=self.Timer, args=[starttime, observer], daemon=True)
        timerThread.start()

        self.investigationActive.set(True)
        self.ShowFrame(EventLog)
        
    def viewUnreadableFiles(self):
        window = tk.Frame()
        #Create a Toplevel window
        popup= tk.Toplevel(window)
        popup.geometry("1000x600")
        tk.Label(popup,text= "Unable to get hash for the following files:").grid(row=0, sticky="ew")
        tk.Label(popup,text= "File:").grid(row=1, column=0, sticky="ew")
        tk.Label(popup,text= "Error:").grid(row=1, column=1, sticky="ew")
        popup.grid_columnconfigure(0, weight=1)
        popup.grid_columnconfigure(1, weight=1)

        totalno = len(self.unreadableFileList)
        for i in range(totalno):
            for j in range(2):
                e = tk.Label(popup, wraplength=400, text=self.unreadableFileList[i][j])
                e.grid(row=i+2, column=j, sticky="ew")

    def checkLoadingProgress(self, loadingpopup):
        while (self.investigationActive.get() == False):
            loadingpopup.update()
        loadingpopup.destroy()

    # To add a new file item:
    def addNewFile(self, filename):
        # Order of data: [(0)Index, (1)Full file name, (2)Submissibility, (3)Notes, (4)Metadata, (5)Screenshots]
        orgMetadata = meta.fileMeta(filename)
        if (len(self.fileData) == 0):
            newdata = [1, filename, tk.StringVar(), tk.StringVar(), orgMetadata, []]
            self.fileData.append(newdata)
        else:
            itemnumber = self.fileData[-1][0]+1
            newdata = [itemnumber, filename, tk.StringVar(), tk.StringVar(), orgMetadata, []]
            self.fileData.append(newdata)

    # To add a new event item:
    def addNewEvent(self, data):
        # Add timestamp and index to data
        now = datetime.now()
        data.insert(0,now.strftime("%d/%m/%Y %H:%M:%S"))
        currentRowNo = self.eventRowNo.get()
        data.insert(0,currentRowNo)

        # Add the new data to the database
        self.eventData.append(data)

        tk.Label(self.eventsTableFrame, text=data[0], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=0, sticky="ew")
        tk.Label(self.eventsTableFrame, text=data[1], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=1, sticky="ew")
        tk.Label(self.eventsTableFrame, text=data[2], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=2, sticky="ew")
        tk.Label(self.eventsTableFrame, text=data[3], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=3, sticky="ew")
        
        self.eventRowNo.set(currentRowNo+1)

    # End of investigation, direct user to report page
    def EndInvestigation(self):
        self.investigationActive.set(False)
        self.hashMultithreading(0)
        self.ShowFrame(Report)

    # Multithreaded hashing of all files marked submissible
    def hashMultithreading(self, isStart):
        pool = multiprocessing.Pool(4)
        for row in self.fileData:
            pool.apply_async(self.hashmd5(row[1], isStart))
        
        pool.close()
        pool.join()

    # Function to be threaded
    def hashmd5(self, file, isStart):
        try:
            with open(file,"rb") as f:
                hash_md5 = hashlib.md5()
                with open(file, "rb") as f:
                    for chunk in iter(lambda:f.read(4096), b""):
                        hash_md5.update(chunk)
                self.hashDictMutex.acquire()
                if isStart:
                    self.startHashDict[file] = hash_md5.hexdigest()
                else:
                    self.endHashDict[file] = hash_md5.hexdigest()
                self.hashDictMutex.release()
        except Exception as e:
            self.unreadableFileList.append([file,e])

    # To be called when a file has been successfully investigated.
    def FileInvestigated(controller):
        fileCount = controller.investigatedFileCount.get()+1
        controller.investigatedFileCount.set(fileCount)
        controller.investigatedFileCountString.set("Total files investigated: " + str(fileCount) + '/' + str(controller.totalFileCount.get()))
        
    # Generate report of investigation
    def GenerateReport(self, folderpath):
        originalfolder = self.selectedFolder.get().replace("Selected folder: ", "")
        with open('./Templates/template.html', 'r+') as f: 
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "<!-- File data -->" in line:
                    # Create a table row for each file log.
                    for data in self.fileData:
                        lines.insert(i+1, "<div id = 'fileno"+str(data[0])+"'>")
                        i+=1
                        lines.insert(i+1, "<tr>")
                        i+=1
                        data[2] = data[2].get()
                        data[3] = data[3].get()
                        for x in range (0, 6):
                            if x < 4:
                                lines.insert(i+1, "<td>" + str(data[x]) + "</td>")
                                i+=1
                            elif x == 4:
                                if (data[x] != None):
                                    lines.insert(i+1, "<td> Original Metadata: " + str(data[x]) + "<br>Current Metadata: " + str(meta.fileMeta(data[1])) +"</td>")
                                    i+=1
                                else:
                                    lines.insert(i+1, "<td> None </td>")
                                    i+=1
                            else:
                                lines.insert(i+1, "<td>" + str(len(data[x])) + "</td>")
                                i+=1
                        if (len(data[5]) > 0):
                            # Insert the slideshow button
                            lines.insert(i+1, "<td><input type=\"button\" onclick=\"createSlideShow('fileno"+str(data[0])+"', "+str(len(data[5]))+", "+ str(data[5])+")\"value=\"View Screenshots\"></input></td>")
                            i+=1
                        else:
                            # Insert empty cell
                            lines.insert(i+1, "<td></td>")
                            i+=1
                        lines.insert(i+1, "</tr>")
                        i+=1
                        lines.insert(i+1, "</div>")
                        i+=1
                if "<!-- Enter investigation start time here -->" in line:
                    lines.insert(i+1, "<h2>" + self.startTime.get() + "</h2>")
                    i+=1
                    lines.insert(i+1, "<h2>" + self.selectedFolder.get() + "</h2>")
                    i+=1
                    lines.insert(i+1, "<h2>" + "Investigation End Time: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "</h2>")
                    i+=1
                if "<!-- Event data -->" in line:
                    # Create a table row for each event log.
                    for data in self.eventData:
                        lines.insert(i+1, "<tr>")
                        i+=1
                        for item in data:
                            lines.insert(i+1, "<td>" + str(item) + "</td>")
                            i+=1
                        lines.insert(i+1, "</tr>")
                        i+=1

            f.seek(0)
            starttime = self.startTime.get().replace("Investigation start time: ","")
            starttime = starttime.replace("/","_")
            starttime = starttime.replace(":","_")
            with open( (folderpath+"/WatcherReport"+starttime+".html"), 'w+') as newhtml:
                for line in lines:
                    newhtml.write(line)
            # Move screenshot folder
            shutil.move("./"+self.screenshotFolder, folderpath)

            exit()
            
    # To be called when a file has been successfully investigated.
    def FileInvestigated(self):
        fileCount = self.investigatedFileCount.get()+1
        self.investigatedFileCount.set(fileCount)
        self.investigatedFileCountString.set("Total files investigated: " + str(fileCount) + '/' + str(self.totalFileCount.get()))

if __name__ == "__main__":
    mainProgram = Controller()
    mainProgram.state('zoomed')
    mainProgram.mainloop()