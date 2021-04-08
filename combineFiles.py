import os
import sys
from tkinter import Tk, messagebox
from tkinter.filedialog import askdirectory, asksaveasfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json
import codecs
import tempfile


# Function to find crank angle at each data point
# Takes length between each local max and divides it into equal parts around a circle
def getAngles (indexList, la):
    for i in range(1, len(indexList)-1):
        dist = indexList[i+1]-indexList[i]
        angles = np.linspace(0,2*np.pi,dist).tolist()
        la = la + angles
    return la


# Function to downsample and smooth out pedal circle
def avgTorque(arrayIn):
    n = 75 # Number of divisions in circle for averaging
    avg = []
    circle = np.linspace(0, 2 * np.pi, n).tolist()
    for r in range(0, len(circle)-1):
        added = 0
        ind = [i for i, j in enumerate(arrayIn[0]) if (j >= circle[r]) & (j < circle[r+1])]
        for x in ind:
            try:
                added = added + arrayIn[1][x]
            except:
                continue

        if len(ind) > 0:
            avg.append(added/len(ind))
        else:
            avg.append(0)

    circle.pop(n-1)

    return circle, avg


# Function to align crank angles with torque info
def rotate(l, pos):
    l[:] = l[-pos:] + l[:-pos]

    return l
    

# Main code to do stuff with
def main():
    # Get desired directory from user
    Tk().withdraw()
    inFolder = askdirectory()

    if inFolder:
        try:
        # read csv files from target folder
            tL = pd.read_csv(os.path.join(inFolder,"leftBurst.csv"), delimiter=",", usecols=[0,1], header = 0, names=['time', 'Ltorque'])
            tR = pd.read_csv(os.path.join(inFolder,"rightBurst.csv"), delimiter=",", usecols=[0,1], header = 0, names=['time', 'Rtorque'])
            tB = pd.read_csv(os.path.join(inFolder,"bothBurst.csv"), delimiter=",", usecols=[0,1], header = 0, names=['time', 'torque'])
            cad = pd.read_csv(os.path.join(inFolder,"bothCadence.csv"), delimiter=",", usecols=[0,1], header = 0, names=['time', 'cadence'])
            pB = pd.read_csv(os.path.join(inFolder,"bothPower.csv"), delimiter=",", usecols=[0,1], header = 0, names=['time', 'power'])
        except:
            messagebox.showerror("Error", "Missing required csv file")
            sys.exit("Failed to load files")
    else:
        sys.exit()

    # Find index and time of max torque value
    iMax = tR['Rtorque'].idxmax()
    tMax = tR.at[iMax, 'time']

    # Remove data outside of 5s before and 5s after net torque goes below 0
    tStart = tMax - 5

    tFin = tB.at[np.where((tB['torque'] < 0) & (tB['time'] > tStart+5 ))[0][0], 'time']
    tB = tB.loc[((tB['time'] > tStart) & (tB['time'] < tFin))]
    tL = tL.loc[((tL['time'] > tStart) & (tL['time'] < tFin))]
    tR = tR.loc[((tR['time'] > tStart) & (tR['time'] < tFin))]
    cad = cad.loc[((cad['time'] > tStart) & (cad['time'] < tFin))]
    pB = pB.loc[((pB['time'] > tStart) & (pB['time'] < tFin))]

    # Merge DataFrames and set index to time for export
    allData = pB.merge(tB, on = 'time', how = 'left').merge(cad, on = 'time', how = 'left')

    # Rename dataframe to match existing format and add extra columns for json format
    allData = allData.rename(columns = {'time': 'SECS', 'power': 'WATTS', 'torque': 'NM', 'cadence': 'CAD'})
    allData['ALT'] = 240
    allData['TEMP'] = 22

    # Output temp file with data
    with tempfile.NamedTemporaryFile(mode='r+') as tmp:
        allData.to_json(tmp, orient='records')

        #Take output from temp file and write to SAMPLES element in dict
        #dataFile = open(os.path.join(inFolder, 'tmp.json'))
        tmp.seek(0)
        dataFile = json.load(tmp)

    with open('template.json', "r", encoding = 'utf-8-sig') as header:
        f = json.load(header)
        f["RIDE"]["SAMPLES"] = dataFile

    with open(os.path.join(inFolder, 'allData.json'), "w") as outFile:
        outFile.write(json.dumps(f, indent = 4))

    ####################################
    # Make graphs for interesting things
    ####################################

    # Locate local maximums (assume they occur at about the same crank angle)
    tL['maxL'] = tL.Ltorque[(tL.Ltorque.shift(1) < tL.Ltorque) & (tL.Ltorque.shift(-1) < tL.Ltorque)] 
    tR['maxR'] = tR.Rtorque[(tR.Rtorque.shift(1) < tR.Rtorque) & (tR.Rtorque.shift(-1) < tR.Rtorque)] 

    # Compute crank angle for each crank and plot crank angle vs torque
    # Assumes max torque occurs at theta = 0 for all pedal strokes
    lMaxes = tL['maxL'].dropna()
    indexList = list(lMaxes.index.array)
    #la = [0]*indexList[0] # Find the first max to orient the circle with
    la = []

    # For right leg
    rMaxes = tR['maxR'].dropna()
    indexListR = list(rMaxes.index.array)
    #ra = [0]*indexListR[0]
    ra = []

    # Get list of crank angles based on local maxes of torque
    la = getAngles(indexList, la)
    ra = getAngles(indexListR, ra)

    # Calculate average torque for given crank angle 
    avgLV, avgLT = avgTorque([la, tL['Ltorque'].tolist()])
    avgRV, avgRT = avgTorque([ra, tR['Rtorque'].tolist()])

    # Align torque and cranks
    avgLV = rotate(avgLV, avgLT.index(max(avgLT)))
    avgRV = rotate(avgRV, avgRT.index(max(avgRT)))

    # Make a plot with L and R side by side
    axL = plt.subplot(121, projection='polar')
    axR = plt.subplot(122, projection='polar')
    axL.set_theta_zero_location('W')
    axR.set_theta_direction(-1)
    axL.title.set_text('Left Leg')
    axR.title.set_text('Right Leg')
    axL.plot(avgLV, avgLT)
    axR.plot(avgRV, avgRT)

    # Change spacing of subplots
    plt.subplots_adjust(wspace = 0.7)

    # Save image in input folder
    plt.savefig(os.path.join(inFolder, 'pedalStroke.png'))


if __name__ == "__main__":
    main()
