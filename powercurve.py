import numpy as np
from tkinter import Tk, messagebox
from tkinter.filedialog import askdirectory, asksaveasfile
import os
import sys

# Write output to csv file
def exportCSV ( path, data ):
    try:
        # Not sure if this is legal but I replaced the newline character with a comma and it worked beautifully
        np.savetxt(path,data,fmt='%5.2f',delimiter=',',newline=',') 
        sys.exit("File written successfully")
    except PermissionError:
        sys.exit("File failed to write, check your folder permissions")

# given file address, convert file to CSV
def convertCSV ( address ):
    npFile = np.genfromtxt(address, delimiter=',', skip_header=1, usecols=(0,1))
    return npFile

# Run a dialog to select a directory
def fileDialog():
    # Eventually replace this with an actual file dialog
    Tk().withdraw()
    directory = askdirectory()
    return directory

# Check that folder has the required files in it
def checkFolderContents( directory ):
    if os.path.isfile(os.path.join(directory, "bothPower.csv")) and os.path.isfile(os.path.join(directory, "bothCadence.csv")) and os.path.isfile(os.path.join(directory, "bothBurst.csv")):
        return True
    else:
        return False

# Find size of output array based on length of input
# outputSize :: npArray -> List -> Int
def outputSize ( array, periods ):
    duration = array[len(array)-1,0] - array[0,0] 
    try:
        size = list(map(lambda k: k > duration, periods)).index(True) - 1
    except:
        size = len(periods)

    return size

def cadCalc( find, searchArray, cadenceArray ):
    cadences = []
    for f in range(0,len(find)):
        index = np.where( searchArray == find[f] )[0]
        cadences.append(cadenceArray[index[0]][1])
    print(cadences)
    return index


# Calculate the thresholds of given array based on locations
# findThresholds :: tuple -> array -> list
def findThresholds ( locations, array ):
    mmxCalc (locations, array)

    thresholds = [max(t) for t in buckets]
        
    return thresholds

# calculate the mean of whatever you pass into it (power, cadence, torque, etc)
# mmxCalc :: tuple -> npArray -> float
def mmxCalc ( location, data ):
    # consider is np.ndarray type
    consider = data[location[0]:location[1],1]
    mmx = sum(consider)/len(consider)
    return mmx

# Make "Buckets" with all of the potential start and end times for each period to be checked later
# makeBuckets :: list -> npArray -> array
def makeBuckets ( periods, array ):

    # Find how big to make buckets array
    
    size = outputSize( array, periods )
    
    # Should automate creating these buckets so that this is more responsive
    buckets = [[]for y in range(size)]

    for i in range(0,len(array)):

        for j in range(i+1,len(array)):
            interval = array[j,0] - array[i,0]
            if interval > 65:
                break
            
            for k in range(0,len(buckets)):
                if periods[k]-0.05 < interval < periods[k]+0.5:
                    mmp = mmxCalc((i,j),array)
                    buckets[k].append([array[i,0],array[j,0],mmp])

    # Buckets are list of tuples populated with numpy.float64
    return buckets

# Find the start and end index of the MMP for each zone
# findIndices :: array -> npArray -> list of tuples
def findIndex ( buckets, array ):
    indices = []
    for bucket in buckets:
        mmp = max([x[2] for x in bucket])
        
        # Find the bucket element holding the max mean power to get the start and end time data
        loc = np.where( np.isin(bucket, mmp, assume_unique=True) == True )[0][0]

        # Find index of array at start and end times 
        start = np.where(np.isin(array, bucket[loc][0], assume_unique=True) == True)[0][0]
        end = np.where(np.isin(array, bucket[loc][1], assume_unique=True) == True)[0][0]

        indices.append((start,end))

    return indices

# Start Point
def main():
    
    # Define which ranges we want max sustained power for
    periods = [1,5,10,15,30, 60]

    while True:
        inFolder = fileDialog()

        if checkFolderContents( inFolder ):
           
            pwrRaw = convertCSV( os.path.join(inFolder, "bothPower.csv") )
            cadence = convertCSV( os.path.join(inFolder, "bothCadence.csv") )
            trq = convertCSV( os.path.join(inFolder, "bothBurst.csv") )

            buckets = makeBuckets ( periods, pwrRaw )

            pwrInd = findIndex ( buckets, pwrRaw )
            trqInd = findIndex ( buckets, trq )

            output = [max(cadence[:,1])]

            # This could probably also be it's own function but it's easy enough here
            # Combines all of the outputs together and adds zeros if missing values
            for p in range(0,len(periods)):
                if p < len(pwrInd):
                    output.append(mmxCalc(pwrInd[p],pwrRaw))
                    output.append(mmxCalc(pwrInd[p],cadence))
                else:
                    output.append(0)

            for q in range(0,len(periods)):
                if q < len(trqInd):
                    output.append(mmxCalc(trqInd[q],trq))
                else:
                    output.append(0)

            # This might be a hack but the parentheses don't print when I use zip even though it should give a tuple
            exportCSV( os.path.join( inFolder, "output.csv"), output )

        else:
            messagebox.showerror("Error", "Missing required csv file")

# In case I want to make this part of a bigger program in the future
if __name__ == "__main__":
    main()
