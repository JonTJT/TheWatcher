import tkinter as tk
import time

class Eventviewer(tk.LabelFrame):
    def __init__(self, *args, **kwargs):
        tk.LabelFrame.__init__(self, *args, **kwargs)
        data = [
            # Time, Filename, Action, Notes, Active
            [1000,   "ST", "action 1", "notes 1", True],
            [1345,   "SO", "action 2", "notes 2",  False],
            [1711,   "SX", "action 3", "notes 3",  True],
            ]

        self.grid_columnconfigure(1, weight=1)
        tk.Label(self, text="Time", anchor="w").grid(row=0, column=0, sticky="ew")
        tk.Label(self, text="Filename", anchor="w").grid(row=0, column=1, sticky="ew")
        tk.Label(self, text="Action", anchor="w").grid(row=0, column=2, sticky="ew")
        tk.Label(self, text="Notes", anchor="w").grid(row=0, column=3, sticky="ew")
        tk.Label(self, text="View Change", anchor="w").grid(row=0, column=4, sticky="ew")

        row = 1
        for (nr, name, action, notes, active) in data:
            nr_label = tk.Label(self, text=str(nr), anchor="w")
            name_label = tk.Label(self, text=name, anchor="w")
            # action_button = tk.Button(self, text="Delete", command=lambda nr=nr: self.delete(nr))
            actionLabel = tk.Label(self, text=action, anchor="w")
            notesLabel = tk.Label(self, text=notes, anchor="w")
            #active_cb = tk.Checkbutton(self, onvalue=True, offvalue=False)
            viewChangeButton = tk.Button(self, text="Click to View", command=lambda nr=nr: self.viewChange(nr))
            # if active:
            #     active_cb.select()
            # else:
            #     active_cb.deselect()

            nr_label.grid(row=row, column=0, sticky="ew")
            name_label.grid(row=row, column=1, sticky="ew")
            actionLabel.grid(row=row, column=2, sticky="ew")
            notesLabel.grid(row=row, column=3, sticky="ew")
            # active_cb.grid(row=row, column=2, sticky="ew")
            # action_button.grid(row=row, column=3, sticky="ew")
            viewChangeButton.grid(row=row, column=4, sticky="ew")

            row += 1

        tk.Button(self, text="Append", command=lambda newFile=[1234,   "newfile", "action ?", "notes ?",  True]: self.appendFileEntry(newFile))

    def delete(self, nr):
        print("deleting...nr=", nr)

    def appendFileEntry(self, newFile):
        print("Appending...")

    def viewChange(self, nr):
        print("Viewing change of file", nr)

if __name__ == "__main__":
    root = tk.Tk()
    Eventviewer(root, text="Event Viewer").pack(side="top", fill="both", expand=True, padx=10, pady=10)
    root.mainloop()