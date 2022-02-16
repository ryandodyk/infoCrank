## Import data from infocrank CSVs and allow user to select part to consider

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from tkinter.filedialog import askdirectory
import tkinter as tk
import os
import sys

def onSelect (xmin, xmax):
    indmin, indmax = np.searchsorted(x, (xmin, xmax))
    indmax = min(len(x) - 1, indmax)

    region_x = x[indmin:indmax]
    region_y = y[indmin:indmax]
    line2.set_data(region_x, region_y)
    ax2.set_xlim(region_x[0], region_x[-1])
    ax2.set_ylim(region_y.min(), region_y.max())
    fig.canvas.draw_idle()

def selectEffort(inFolder):
    pwr = convertCSV(os.path.join(inFolder,"bothPower.csv"))
    
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(211)
    x = pwr[0,:]
    y = pwr[1,:]
    
    ax.plot(x,y, '-')

    ax2 = fig.add_subplot(212)
    line2, = ax2.plot([], [])

    span = SpanSelector(ax, onSelect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))
    
    plt.show()

    

def openDir():
    fileWindow = tk.Toplevel()
    fileWindow.title("Select Effort")
    directory = askdirectory()
    fileWindow.destroy()
    selectEffort(directory)

def convertCSV(address):
    npFile = np.genfromtxt(address, delimiter=',', skip_header=1, usecols=(0,1))
    return npFile
    
def main():
    root = tk.Tk()
    root.title("InfoCrank Tools Beta")
    root.geometry("500x500")

    tk.Button(root, text="import", command=openDir).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
