import numpy as np
import matplotlib.pyplot as plt
import os
import sys


# Eventually replace this with a file dialogue but this is easier for testing
inFile = sys.argv[1]

# Read CSV file
pwrRaw = np.genfromtxt(inFile, delimiter=',', skip_header=1, usecols=(0,1))

# Find time of max power
imax = np.argmax(pwrRaw, axis=0)[1]
pwrFlip = np.flip(pwrRaw, axis=0)
iflip = len(pwrFlip) - imax - 1 #np.argmax(pwrFlip, axis=0)[1]

# Define which ranges we want max sustained power for
periods = [1,5,10,15,30]

# Initialize output array
out = []

# iterate through each row to find where time is in correct range and power matches criteria
for period in periods:
    thresholds = [0]
    for i in range(0, len(pwrFlip)):
        start = len(pwrFlip)-i-1
        for j in range(start, len(pwrRaw)):
            # Find the timespan being considered by the program
            interval = abs(pwrRaw[j,0] - pwrRaw[start,0])

            # Filter out when interval is right size
            if interval <= (period+0.5) and interval > (period-0.05): 
                if min(pwrRaw[start,1], pwrRaw[j,1]) > max(thresholds):
                    fin = j
                    t = 0
                    # QC check to make sure that it takes the minimum value in the time range
                    for k in range(min(start, fin), max(start, fin)):
                        if t== 0:
                            t= pwrRaw[k,1]
                        if pwrRaw[k,1] < t:
                            t= pwrRaw[k,1] 
                    thresholds.append(t)

    # Add identified value to output array
    out.append(max(thresholds))


print(out)
