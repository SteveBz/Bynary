#!/usr/bin/env python

import math

class binOrganiser():
    def __init__(self, binCount, lowerBinContentCount=10):
        self.binCount=binCount
        self.xBins=[] 
        self.yBins=[] 
        self.yBinSquares=[] 
        self.vxerrvSquares=[] 
        self.errors=[] 
        self.labels=[] 
        self.data1=[] 
        self.binLowerBounds=[] 
        self.binMidPoints=[] 
        self.binUpperBounds=[] 
        self.dataCount=0
        self.lowerBinContentCount=lowerBinContentCount
        
    def newBin(self, binLowerBound, binUpperBound):
        self.xBins.append([] )
        self.yBins.append([] )
        self.yBinSquares.append([] )
        self.vxerrvSquares.append([] )
        self.errors.append([] )
        self.binLowerBounds.append(binLowerBound)
        self.binUpperBounds.append(binUpperBound)
        self.binMidPoints.append(math.sqrt(binLowerBound*binUpperBound))
        
    def binAddDataPoint(self, x, y, dy='', value=1):
        y=abs(y)
        x=abs(x)
        dy=abs(dy)
        #print(y)
        vOverErr=float(y/dy)
        if abs(vOverErr)<value:
            return 1
        for i in range(self.binCount):
            if x>self.binLowerBounds[i] and x<=self.binUpperBounds[i]:
                self.xBins[i].append(x)
                self.yBins[i].append(y)
                vxverr2=(y*dy)**2
                y2=y**2
                self.yBinSquares[i].append(y2)
                self.vxerrvSquares[i].append(vxverr2)
                self.errors[i].append(dy)
                return 0
        return 1
    def splitBin(self):
        
        #Filter out currently inluded rows only
        indexStatus = self.parent.status.index
        condition = self.parent.status.include == True
        statusIndices = indexStatus[condition]
        statusIndicesList = statusIndices.tolist()
        
        
    def getBinYLabelArray(self):
 
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
        if type=='mean':
            for i in range(self.binCount):
                # Mean of the data
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    mean = sum(self.xBins[i])/len(self.xBins[i])
                    data.append(mean) 
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
        return data
        
    def getBinYArray(self, type='rms'):
 
        data=[] 
        if type=='mean':
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
        if type=='rms':
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

    def getBinXVarArray(self, type='var'):
        errbinM=[] 
        errbinP=[] 
        for i in range(self.binCount):
            if len(self.yBins[i])>=self.lowerBinContentCount:
                array=self.getBinXArray('centre')
                errorBarM = abs(array[i]-self.binLowerBounds[i])
                errorBarP = abs(array[i]-self.binUpperBounds[i])
                errbinM.append(errorBarM)
                errbinP.append(errorBarP)
            else:
                errbinP.append(math.nan)
                errbinM.append(math.nan)
        return [errbinM,errbinP]
        
    def getBinYVarArray(self, type='qrms'):
        errbin=[] 
        if type=='qrms':
            for i in range(self.binCount):
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    #Remove nans so length of list (n) is correct
                    vxerrvList = [vxerrv for vxerrv in self.vxerrvSquares[i] if math.isnan(vxerrv) == False]
                    Ylist = [y for y in self.yBinSquares[i] if math.isnan(y) == False]
                    try:
                        error = math.sqrt(sum(vxerrvList)/ ((len(Ylist)-1)*sum(Ylist)))
                        #if i<2:
                            #print(f'vxerrvSquares({i}) = {vxerrvList}')
                            #print(f'yBinSquares({i}) = {Ylist}')
                            #print(f'sum (v * Err) = {sum(vxerrvList)}')
                    except Exception:
                        error = math.nan
                    errbin.append(error) 
                else:
                    errbin.append(math.nan)
        if type=='var':
            for i in range(self.binCount):
                # Square deviations
                if len(self.yBins[i])>=self.lowerBinContentCount:
                    deviation = [(y - self.yData[i]) ** 2 for y in self.yBins[i]]
                    # Variance
                    variance = sum(deviation) / len(self.yBins[i])
                    errbin.append(variance) 
                else:
                    errbin.append(math.nan)
        return errbin

