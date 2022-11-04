import tkinter as tk
from tkinter import StringVar
from tkinter import filedialog
import time
import os
import threading
from datetime import datetime
import pyautogui
import pytz
import shutil 
import glob
import meta

class MainMenu(tk.Frame):
    def __init__(self, parent, controller):
        self.folderSelected = tk.BooleanVar()
        self.folderSelected.set(False)
        tk.Frame.__init__(self, parent)
        tk.Label(self,text="Select the folder that will be used in the investigation.").pack(fill="both", expand=True)
        tk.Label(self,textvariable= controller.selectedFolder).pack(fill="both", expand=True)
        tk.Button(self,text="Select Folder", command=lambda:[self.FolderSelect(controller)]).pack(fill="both", expand=True)
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
        tk.Label(self.fileTableFrame, text="View Changes", anchor="w", background="#FAF9F6").grid(row=0, column=5)
        tk.Label(self.fileTableFrame, text="Screenshot", anchor="w", background="#FAF9F6").grid(row=0, column=6)

        onInvestigationStartThread = threading.Thread(target=self.WaitForInvestigation, args=[controller], daemon=True)
        onInvestigationStartThread.start()

        # To remove: Test button to append new file entry
        #tk.Button(self, text="Append", anchor="w", command=lambda:[self.addNewFile([0, "Insert full file path", tk.StringVar(), tk.StringVar()], controller)], background="#FAF9F6").pack(side="bottom")

    # Timer function for the investigation
    def WaitForInvestigation(self, controller):
        while controller.investigationActive.get() == False:
            time.sleep(0.1)
        self.populateData(controller)

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
            tk.Button(self.fileTableFrame, text="View", command=lambda itemNo = currentRowNo:[self.viewChanges(itemNo, controller)]).grid(row=currentRowNo, column=5, sticky="ew")
            tk.Button(self.fileTableFrame, text="Take", command=lambda x=row[0]:[self.addScreenshot(x, controller)], background="#FAF9F6").grid(row=currentRowNo, column=6, sticky="ew")

            self.rowNo.set(currentRowNo+1)

        currentRowNo = self.rowNo.get()


    def UpdateSubmissibility(self, rowNo):
        return None

    # Open up popup window to prompt investigator to add notes
    def viewChanges(self, itemno, controller):
        window = tk.Frame()
        #Create a Toplevel window
        popup= tk.Toplevel(window)
        popup.geometry("750x250")

        # To display the changes stored in the filedata

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
        screenshotName = controller.screenshotFolder + "\\" + controller.fileData[rowNo-1][1] + "_" + str(nowSgTime.strftime("%Y-%m-%d_%H.%M.%S")) + ".png"
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
        tk.Label(self.eventsTableFrame, text="No.", anchor="w", background="#FAF9F6").grid(row=0, column=0)
        tk.Label(self.eventsTableFrame, text="Time", anchor="w", background="#FAF9F6").grid(row=0, column=1)
        tk.Label(self.eventsTableFrame, text="File name and path", anchor="w", background="#FAF9F6").grid(row=0, column=2, ipadx=5)
        tk.Label(self.eventsTableFrame, text="Event", anchor="w", background="#FAF9F6").grid(row=0, column=3)

        self.populateData(controller)

        # To remove: Test button to add new event
        #tk.Button(self.eventsTableFrame, text="Append", anchor="w", command=lambda:[self.addNewEvent(["testfile.mp3", "File opened"],controller)], background="#FAF9F6").grid(row=currentRowNo, column=1, sticky="ew")


    def UpdateSubmissibility(self, rowNo):
        return None

    def populateData(self, controller):
        self.eventsTableFrame.grid_columnconfigure(0, weight=1)
        # Populate table
        for row in controller.eventData:
            self.submissibility = StringVar()
            currentRowNo = self.eventRowNo.get()
            tk.Label(self.eventsTableFrame, text=row[0], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=0, sticky="ew")
            tk.Label(self.eventsTableFrame, text=row[1], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=1, sticky="ew")
            tk.Label(self.eventsTableFrame, text=row[2], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=2, sticky="ew")
            tk.Label(self.eventsTableFrame, text=row[3], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=3, sticky="ew")
            self.eventRowNo.set(currentRowNo+1)

        currentRowNo = self.eventRowNo.get()
    # To add a new event item:
    def addNewEvent(self, data, controller):
        # Add timestamp and index to data
        now = datetime.now()
        data.insert(0,now.strftime("%d/%m/%Y %H:%M:%S"))
        currentRowNo = self.eventRowNo.get()
        data.insert(0,currentRowNo)

        # Add the new data to the database
        controller.eventData.append(data)

        tk.Label(self.eventsTableFrame, text=data[0], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=0, sticky="ew")
        tk.Label(self.eventsTableFrame, text=data[1], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=1, sticky="ew")
        tk.Label(self.eventsTableFrame, text=data[2], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=2, sticky="ew")
        tk.Label(self.eventsTableFrame, text=data[3], anchor="w", background="#FAF9F6").grid(row=currentRowNo, column=3, sticky="ew")
        
        self.eventRowNo.set(currentRowNo+1)

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
        tk.Button(self,text="Select Folder", command=lambda:[self.ReportFolderSelect(controller)]).pack(fill="both", expand=True)
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

        # Data for filelog and event log (To remove data before deployment)
        self.fileData = [
        ]

        self.eventData = [
            [1, "02/11/2022 19:21:05", "testfile.mp4", "File opened", tk.StringVar()],
            [2, "02/11/2022 19:21:07", "testfile1.mp4", "File opened", tk.StringVar()],
            [3, "02/11/2022 19:21:10", "testfile2.mp4", "File modified", tk.StringVar()],
            [4, "02/11/2022 19:21:12", "testfile3.mp4", "File opened", tk.StringVar()],
            [5, "02/11/2022 19:21:15", "testfile1.mp4", "File opened", tk.StringVar()],
            [6, "02/11/2022 19:21:16", "testfile2.mp4", "File modified", tk.StringVar()],
        ]

        # Create directory to save screenshots
        now = datetime.now()
        sgTime = pytz.timezone("Asia/Singapore")
        nowSgTime = sgTime.localize(now)
        self.screenshotFolder = "TheWatcherScreenshots" + "_" + str(nowSgTime.strftime("%Y-%m-%d_%H.%M.%S"))
        os.mkdir(self.screenshotFolder)

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

    # File counter function to count number of files within folder and all subfolders.
    def countFiles(self, filepath):
        counter = 0
        for file in glob.iglob(filepath+'/**/*.*',recursive = True):
            counter += 1
            self.addNewFile(file)
        return counter

    # To start investigation
    def BeginInvestigation(self):
        time.sleep(2)
        self.LoadingBar()
        now = datetime.now()
        self.startTime.set("Investigation start time: " + now.strftime("%d/%m/%Y %H:%M:%S"))
        starttime = int(round(time.time() * 100))

        # Start timer thread
        timerThread = threading.Thread(target=self.Timer, args=[starttime], daemon=True)
        timerThread.start()

        # Set file count
        self.totalFileCount.set(self.countFiles(self.selectedFolder.get()))
        self.investigatedFileCountString.set("Files investigated: "+ "0/" + str(self.totalFileCount.get()))
        self.selectedFolder.set("Selected folder: "+ self.selectedFolder.get())

        self.investigationActive.set(True)
        self.ShowFrame(EventLog)
        
    def LoadingBar(self):
        #Create a Toplevel window
        loadingpopup= tk.Toplevel()
        loadingpopup.geometry("300x200")
        #Loading percentage for entire program
        tk.Label(loadingpopup,text= "Collecting hashes of all files...").pack(fill="both", expand=True)
        tk.Label(loadingpopup,text= "Please wait").pack(fill="both", expand=True) 
        loadingpopup.update()
        checkProgressThread = threading.Thread(target=self.checkLoadingProgress, args=[loadingpopup], daemon=True)
        checkProgressThread.start()

    def checkLoadingProgress(self, loadingpopup):
        while (self.investigationActive.get() == False):
            loadingpopup.update()
        loadingpopup.destroy()

    # To add a new file item:
    def addNewFile(self, filename):
        # Order of data: [(0)Index, (1)Full file name, (2)Submissibility, (3)Notes, (4)Metadata, (5)Screenshots]
        if (len(self.fileData) == 0):
            newdata = [0, filename, tk.StringVar(), tk.StringVar(), {}, []]
            self.fileData.append(newdata)
        itemnumber = self.fileData[-1][0]
        newdata = [itemnumber, filename, tk.StringVar(), tk.StringVar(), {}, []]
        self.fileData.append(newdata)
        print(self.fileData)

    # End of investigation, direct user to report page
    def EndInvestigation(self):
        self.investigationActive.set(False)
        self.ShowFrame(Report)

    # Generate report of investigation
    def GenerateReport(self, folderpath):
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
                        data[3] = data[3].get()
                        for item in data:
                            lines.insert(i+1, "<td>" + str(item) + "</td>")
                            i+=1
                        if (len(data[5]) > 0):
                            # Insert the slideshow button
                            lines.insert(i+1, "<td><input type=\"button\" onclick=\"createSlideShow('fileno"+str(data[0])+"', "+str(len(data[5]))+", "+ str(data[5])+")\"value=\"View Screenshots\"></input></td>")
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
                        data[4] = data[4].get()
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
def FileInvestigated(controller):
    fileCount = controller.investigatedFileCount.get()+1
    controller.investigatedFileCount.set(fileCount)
    controller.investigatedFileCountString.set("Total files investigated: " + str(fileCount) + '/' + str(controller.totalFileCount.get()))

if __name__ == "__main__":
    mainProgram = Controller()
    mainProgram.geometry("800x400")
    mainProgram.mainloop()