import numpy as np
import os
import sys

# Write output to csv file
def exportCSV (path, data):
    # Not sure if this is legal but I replaced the newline character with a comma and it worked beautifully
    np.savetxt(path,data,fmt='%5.2f',delimiter=',',newline=',') 

# given file address, convert file to CSV
def convertCSV (address):
    npFile = np.genfromtxt(address, delimiter=',', skip_header=1, usecols=(0,1))
    return npFile

# Find the equivalent index of a flipped array
def flipInd (array, ind):
    index = len(array) - ind - 1
    return index

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


# Get the max value in each bucket
def findThresholds (periods, array, reversearray):
    buckets = makeBuckets(periods, array, reversearray)

    thresholds = [max(t) for t in buckets]
        
    return thresholds

# Get the minimum value inside of the considered interval
def qualityCheck (start, end, data):
    consider = data[start:end]
    localMin = min(consider[:,1])
    return localMin


# Adds value to bucket depending on length of interval
def addToBucket (periods, buckets, array, start, fin):

    interval = array[fin,0] - array[start,0]
    
    for k in range(0,len(periods)):
        if periods[k]-0.05 < interval < periods[k]+0.5:
            buckets[k].append(qualityCheck(start,fin, array))


    return buckets

# Do most of the calculations
def makeBuckets (periods, array, reverseArray):
    
    # Should automate creating these buckets so that this is more responsive
    buckets = [[],[],[],[],[],[]]

    for i in range(0,len(reverseArray)):

        fin = flipInd(reverseArray, i)
        
        for j in range(0,fin):
            
            buckets = addToBucket (periods, buckets, array, j, fin)

    return buckets

# Start Point
def main():
    
    # Define which ranges we want max sustained power for
    periods = [1,5,10,15,30, 60]

    inFolder = fileDialog()

    if checkFolderContents( inFolder ):

        pwrRaw = convertCSV( os.path.join(inFolder, "bothPower.csv") )
        cadence = convertCSV( os.path.join(inFolder, "bothCadence.csv") )

        # Find time of max power
        iMaxPwr = np.argmax( pwrRaw, axis=0 )[1]

        pwrThresholds = findThresholds( periods, pwrRaw, np.flip(pwrRaw, axis=0) )

        exportCSV( os.path.join(inFolder, "output.csv"), pwrThresholds )


    else:
        print("Selected folder missing required files")

# In case I want to make this part of a bigger program in the future
if __name__ == "__main__":
    main()
