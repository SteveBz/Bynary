#!/usr/bin/env python

import math
import numpy as np
import statistics

class binOrganiser():
    def __init__(self, binCount, lowerBinContentCount=10):
        #__init__: This is the constructor method, which is called when an object of this class is created.
        #The constructor takes two arguments: binCount and lowerBinContentCount.
        #binCount is the number of bins, while lowerBinContentCount is the minimum number of content count in each bin.
        #The constructor also initializes several lists and variables.
        self.binCount=binCount
        self.xBins=[] 
        self.yBins=[] 
        self.yBinSquares=[]
        
        self.vxerrvSquares=[] 
        self.errvSquares=[] 
        self.errors=[]
        self.indices=[]
        self.labels=[] 
        self.data1=[] 
        self.binLowerBounds=[] 
        self.binMidPoints=[] 
        self.binUpperBounds=[] 
        self.dataCount=0
        self.lowerBinContentCount=lowerBinContentCount
        
    def newBin(self, binLowerBound, binUpperBound):
        #newBin: This method creates a new bin by adding its lower bound and upper bound to the list of bin lower bounds and bin upper bounds, respectively. It also calculates the midpoint of the bin and adds it to the list of bin midpoints.

        self.xBins.append([] )
        self.yBins.append([] )
        self.yBinSquares.append([] )
        self.vxerrvSquares.append([])
        self.errvSquares.append([])
        self.errors.append([] )
        self.indices.append([] )
        self.binLowerBounds.append(binLowerBound)
        self.binUpperBounds.append(binUpperBound)
        self.binMidPoints.append(math.sqrt(binLowerBound*binUpperBound))
        
    def binCalculateDataPoints(self, binNum, percent):
        
        #binCalculateDataPoints: This method calculates the indices of the top 'percent' of the values in a bin.
        #Calculate array of indices to remove top 'percent' of values.

        #print(f'Remove 1: {percent}% from bin {binNum}')
        indices=[]
        #If no percentage, don't bother
        if not percent:
            return indices
        # How many items does bin array have?
        binLength=len(self.xBins[binNum])
        
        #print(f'Remove 2: {percent}% from {binLength} in bin {binNum}')
        #print(self.xBins)
        if binLength==0:
            return []
        
        #print(f'Remove 3: {percent}% from {binLength} in bin {binNum}')
        # Round percentage up so that always remove at least 1 (except for percent=0) and then zero-base it (the -1)
        removeNValues=int(round(binLength*percent/100.0 + 0.5,0)) -1
        
        #Find value of threshold bin value
        dummyArray=sorted(self.yBins[binNum], key=float, reverse=True)
        thresholdRemoval=dummyArray[removeNValues]
        
        #collect indices at or above threshold value.
        for index in range(binLength):
            if self.yBins[binNum][index]>=thresholdRemoval:
                indices.append(index)
                
        #print(f'Remove 4:{len(indices)}# from {binLength}')
        return indices
    
    def binAddDataPoint(self, x, y, dy='', threshold_value=1, idx=0):
        
        # This method adds a data point (x, y, dy, threshold_value, idx) to the appropriate bin.
        # It calculates the value of vOverErr (Signal to noise ratio for v)
        # and adds the x, y, dy, vxverr2, verr2, y2, idx values to the corresponding lists for the bin.
        # Only S/R greater than 'threshold_value' are added. 
        y=abs(y)
        x=abs(x)
        dy=abs(dy)
        if dy:
            vOverErr = float(y / dy)
        else:
            # Handle the divide by zero case
            print(f'Error: vOverErr = float(y / dy) -  divide by zero error, dy = 0 or null, x = {x}, y = {y}')
            return 0

        if abs(vOverErr)<threshold_value:
            return 0
        for i in range(self.binCount):
            if x>self.binLowerBounds[i] and x<=self.binUpperBounds[i]:
                self.xBins[i].append(x)
                self.yBins[i].append(y)
                vxverr2=(y*dy)**2
                verr2=(dy)**2
                y2=y**2
                self.yBinSquares[i].append(y2)
                self.vxerrvSquares[i].append(vxverr2)
                self.errvSquares[i].append(verr2)
                self.errors[i].append(dy)
                self.indices[i].append(idx)
                return 1
        return 1
    def splitBin(self):
        
        #splitBin:
        #This method filters out the rows in a given data frame that are currently included.
        #Filter out currently inluded rows only
        
        indexStatus = self.parent.status.index
        condition = self.parent.status.include == True
        statusIndices = indexStatus[condition]
        statusIndicesList = statusIndices.tolist()
        
        
    def getBinYLabelArray(self):
        #getBinYLabelArray: This method returns the array of y-values (labels) for the bins.
 
        labels=[] 
        for i in range(self.binCount):
            # rms of the data
            if len(self.yBins[i])>=self.lowerBinContentCount:
                newlist = [x for x in self.yBinSquares[i] if math.isnan(x) == False]
                labels.append(len(newlist))
            else:
                labels.append(math.nan)
        self.label=labels  
        return labels

    def getBinXArray(self, type='centre'):
        data=[] 
        if type=='ari-mean':
            for i in range(self.binCount):
                # Arithmetic Mean of the data
                if len(self.Bins[i])>=self.lowerBinContentCount:
                    mean = sum(self.xBins[i])/len(self.xBins[i])
                    data.append(mean) 
                else:
                    data.append(math.nan)
        if type=='mean':
            for i in range(self.binCount):
                # Geometric Mean of the data
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    # Geometric Mean of List
                    # using loop + formula
                    newlist = [x for x in self.xBins[i] if math.isnan(x) == False and x > 0]
                    product = 0
                    for j in range(0, len(newlist)):
                        product = product + math.log10(newlist[j])
                    geoMean = product / float(len(newlist))
                    data.append(10**geoMean)
                else:
                    data.append(math.nan)
        if type=='centre':
            for i in range(self.binCount):
                # Product of the data
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    product = math.sqrt(self.binLowerBounds[i]*self.binUpperBounds[i])
                    data.append(product) 
                else:
                    data.append(math.nan)
        #print(f'type ({type}) =', data)
        return data
        
    def getBinYArray(self, mean_type='rms'):
 
        data=[] 
        if mean_type=='mean':
            for i in range(self.binCount):
                # Mean of the data
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    newlist = [x for x in self.yBins[i] if math.isnan(x) == False]
                    try:
                        mean = sum(newlist)/len(newlist)
                    except Exception:
                        mean = math.nan
                    data.append(mean) 
                else:
                    data.append(math.nan)
        elif mean_type=='median':
            for i in range(self.binCount):
                # Median of the data
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    newlist = [x for x in self.yBins[i] if math.isnan(x) == False]
                    try:
                        #print (newlist)
                        median = statistics.median(newlist)
                        #print(median)
                    except Exception as e:
                        print (f"mean_type='{mean_type}', error='{e}'")
                        median = math.nan
                    data.append(median) 
                else:
                    data.append(math.nan)
        elif mean_type=='rms':
            for i in range(self.binCount):
                # rms of the data
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    newlist = [x for x in self.yBinSquares[i] if math.isnan(x) == False]
                    #if i==0:
                    #    print('yBinSquares[0]=',newlist)
                    try:
                        rms = math.sqrt(sum(newlist)/len(newlist))
                    except Exception:
                        rms = math.nan
                    data.append(rms)
                else:
                    data.append(math.nan)
        self.yData=data  
        return data

    def getBinXVarArray(self, type='centre'):
        errbinM=[] 
        errbinP=[] 
        array=self.getBinXArray(type)
        #data=[]
        #gsd_data=[]
        if type=='centre':
            for i in range(self.binCount):
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    errorBarM = abs(array[i]-self.binLowerBounds[i])
                    errorBarP = abs(array[i]-self.binUpperBounds[i])
                    errbinM.append(errorBarM)
                    errbinP.append(errorBarP)
                else:
                    errbinP.append(math.nan)
                    errbinM.append(math.nan)
            #print(f'Error bars =', [errbinM,errbinP])
        elif type=='mean':
            for i in range(self.binCount):
                if len(self.yBins[i]) >= self.lowerBinContentCount:
                    # Filter out invalid or zero values from the list
                    newlist = [x for x in self.xBins[i] if not math.isnan(x) and x > 0]
    
                    if len(newlist) > 0:
                        # Compute the geometric mean
                        log_sum = sum(math.log10(x) for x in newlist)
                        geoMean = 10 ** (log_sum / len(newlist))
                        #data.append(geoMean)
    
                        # Calculate the GSD (Geometric Standard Deviation)
                        variance = sum((math.log10(x) - math.log10(geoMean)) ** 2 for x in newlist) / len(newlist)
                        gsd = 10 ** math.sqrt(variance / len(newlist))
                        #gsd_data.append(gsd)
    
                        # Calculate error bars based on GSD
                        errorBarM = geoMean / gsd  # Lower error bar
                        errorBarP = geoMean * gsd  # Upper error bar
                        errbinM.append(geoMean - errorBarM)
                        errbinP.append(errorBarP - geoMean)
                    else:
                        #data.append(math.nan)
                        #gsd_data.append(math.nan)
                        errbinM.append(math.nan)
                        errbinP.append(math.nan)
                else:
                    #data.append(math.nan)
                    #gsd_data.append(math.nan)
                    errbinM.append(math.nan)
                    errbinP.append(math.nan)
                #print(f'Error bars =', [errbinM,errbinP])
            
        return [errbinM,errbinP]
        
    def getBinYVarArray(self, type='qrms', mean_type='rms'):
        errbin=[]
        if type=='meanerror':
            for i in range(self.binCount):
                # Square deviations
                if len(self.errvSquares[i])>=self.lowerBinContentCount:
                    #Remove nans so length of list (n) is correct
                    errv2List = [math.sqrt(errv2) for errv2 in self.errvSquares[i] if math.isnan(errv2) == False]
                    # Variance
                    meanerror = sum(errv2List) / len(errv2List)
                    errbin.append(meanerror) 
                else:
                    errbin.append(math.nan)
        if type=='qrms':
            #Not sure that this is right!!!
            #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #Its the [sum of (v.dv)** 2]/ [n.sum of (v)** 2]
            for i in range(self.binCount):
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    #Remove nans so length of list (n) is correct
                    # 1) List all the squares of the measurement errors. 
                    vxerrv2List = [vxerrv2 for vxerrv2 in self.vxerrvSquares[i] if math.isnan(vxerrv) == False]
                    # 2) List all the squares of the measurements (ie v_squared).
                    Y2list = [y2 for y2 in self.yBinSquares[i] if math.isnan(y) == False]
                    try:
                        error = math.sqrt(sum(vxerrv2List)/ (len(Y2list)*sum(Y2list)))
                    except Exception:
                        error = math.nan
                    errbin.append(error) 
                else:
                    errbin.append(math.nan)
        if type=='var':
            for i in range(self.binCount):
                # List all square deviations from the mean
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    y_mean = np.mean(self.yBins[i])
                    deviation = [(y - y_mean) ** 2 for y in self.yBins[i] if math.isnan(y) == False]
                    # Variance
                    variance = sum(deviation) / len(self.yBins[i])
                    errbin.append(variance) 
                else:
                    errbin.append(math.nan)
        if type=='var_qrms':
            for i in range(self.binCount):
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    #Remove nans so length of list (n) is correct
                    # RMS of error, ie average of the square of the errors.
                    # 1) List all the squares of the measurement errors (QRMS)
                    errv2List = [errv2 for errv2 in self.errvSquares[i] if math.isnan(errv2) == False]
                    try:
                        qrms = sum(errv2List)/ len(errv2List)
                    except Exception:
                        errbin.append(math.nan)
                        continue
                    # 2) List all square deviations from the mean
                    #if mean_type=='rms':
                    #    y_mean = np.sqrt(np.mean(self.yBins[i]**2))  # RMS
                        
                    if mean_type == 'rms':          # RMS
                        y_mean = np.sqrt(np.mean(np.array(self.yBins[i])**2))  # Convert to numpy array first
    
    
                    elif mean_type=='mean':
                        y_mean = np.mean(self.yBins[i])
                    if mean_type=='median':
                        # Calculate the median
                        y_mean = np.median(self.yBins[i])
                        ## Calculate the variance using the median
                        #y_mean = np.mean((self.yBins[i] - median)**2)
                    deviation_sq = [(y - y_mean) ** 2 for y in self.yBins[i] if math.isnan(y) == False]
                    # Variance of a Gaussian distribution, hence the extra "2"
                    variance = sum(deviation_sq) / (2 * len(self.yBins[i]))
                else:
                    errbin.append(math.nan)
                    continue
                #qrms = 0
                #/ len(self.yBins[i])
                error = math.sqrt(qrms + variance/ len(self.yBins[i]) ) 
                errbin.append(error)
        return errbin

