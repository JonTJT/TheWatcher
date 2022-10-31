import pandas as pd
import numpy as np

import sys 
from tkinter import * 

root = Tk()
root.geometry('580x250')

dates = pd.date_range('20210101', periods=8)
dframe = pd.DataFrame(np.random.randn(8,4),index=dates,columns=list('ABCD'))

txt = Text(root) 
txt.pack() 

class PrintToTXT(object): 
 def write(self, s): 
     txt.insert(END, s)

sys.stdout = PrintToTXT() 

print ('Pandas date range of 8 values in 1 timestamp column adjacent to a numpy random float array of 8 rows and 4 columns, displayed in a Tkinter table') 

print (dframe)

mainloop()