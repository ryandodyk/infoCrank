import numpy as np
import matplotlib.pyplot as plt
import os
import sys

# given file address, convert file to CSV
def convertCSV (address):
    npFile = np.genfromtxt(address, delimiter=',', skip_header=1, usecols=(0,1))
    return npFile

# Find the equivalent index of a flipped array
def flipInd (array, ind):
    index = len(array) - ind - 1
    return index

# Get the minimum value inside of the considered interval
def qualityCheck (start, end, data):
    consider = data[start:end]
    localMin = min(consider[:,1])
    return localMin

# Run a dialog to select a directory
def fileDialog():
    # Eventually replace this with an actual file dialog
    directory = sys.argv[1]
    return directory

# Check that folder has the required files in it
def checkFolderContents(directory):
    if os.path.isfile(os.path.join(directory, "bothPower.csv")) and os.path.isfile(os.path.join(directory, "bothCadence.csv")):
        return True
    else:
        return False

# Do most of the calculations
def thresholdCalc (periods, array, reverseArray):
    out = []
    # iterate through each row to find where time is in correct range and power matches criteria
    for period in periods:
        thresholds = [0]

        for i in range(0, len(reverseArray)):
            start = flipInd(reverseArray, i)

            for j in range(start, len(array)):
                # Find the timespan being considered by the program
                interval = abs(array[j,0] - array[start,0])

                # Filter out when interval is right size
                if interval <= (period+0.5) and interval > (period-0.05): 
                    if min(array[start,1], array[j,1]) > max(thresholds):

                        thresholds.append( qualityCheck(min(start,j), max(start,j), array) )


        out.append(max(thresholds))
    return out

# Start Point
def main():
    
    # Define which ranges we want max sustained power for
    periods = [1,5,10,15,30]

    inFolder = fileDialog()

    if checkFolderContents(inFolder):

        pwrRaw = convertCSV(os.path.join(inFolder, "bothPower.csv"))

        # Find time of max power
        iMaxPwr = np.argmax(pwrRaw, axis=0)[1]

        pwrThresholds = thresholdCalc( periods, pwrRaw, np.flip(pwrRaw, axis=0) )

        print(pwrThresholds)

    else:
        print("Selected folder missing required files")

"""
# Initialize output array
out = []

# iterate through each row to find where time is in correct range and power matches criteria
for period in periods:
    thresholds = [0]
    for i in range(0, len(pwrFlip)):
        start = flipInd(pwrFlip, i)

        for j in range(start, len(pwrRaw)):
            # Find the timespan being considered by the program
            interval = abs(pwrRaw[j,0] - pwrRaw[start,0])

            # Filter out when interval is right size
            if interval <= (period+0.5) and interval > (period-0.05): 
                if min(pwrRaw[start,1], pwrRaw[j,1]) > max(thresholds):
                    fin = j
                    # QC check to make sure that it takes the minimum value in the time range

                    for k in range(min(start, fin), max(start, fin)):
                        if t== 0:
                            t= pwrRaw[k,1]
                        if pwrRaw[k,1] < t:
                            t= pwrRaw[k,1] 

                    thresholds.append( qualityCheck(min(start,fin), max(start,fin), pwrRaw) )

    # Add identified value to output array
    out.append(max(thresholds))


print(out)
"""
if __name__ == "__main__":
    main()
