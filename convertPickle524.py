#!/usr/bin/env python
import os
import pandas as pd
#import astroquery
dirFrom='/home/image/x-Stronomy/bindata/fDR3/KEB-0.50pc/'
dirTo='/home/image/x-Stronomy/bindata/eDR3/KEB-0.50pc/'
files = [f for f in os.listdir(dirFrom) if os.path.isfile(os.path.join(dirFrom, f))]
for file in files:
    if file[-3:]=='csv' or file[-3:]=='pdf' or file[-3:]=='png' or file[-4:]=='json' :
        continue
    print(file)
    picklefile=pd.read_pickle(dirFrom+file)
    fileOut=file.replace('gaia_fDR3','gaia_eDR3')
    picklefile.to_csv(dirTo+fileOut+'.csv')
dirFrom='/home/image/x-Stronomy/bindata/fDR3/stars/'
dirTo='/home/image/x-Stronomy/bindata/eDR3/stars/'
files = [f for f in os.listdir(dirFrom) if os.path.isfile(os.path.join(dirFrom, f))]
for file in files:
    if file[-3:]=='csv' or file[-3:]=='pdf' or file[-3:]=='png' or file[-4:]=='json' :
        continue
    print(file)
    picklefile=pd.read_pickle(dirFrom+file)
    fileOut=file.replace('gaia_fDR3','gaia_eDR3')
    picklefile.to_csv(dirTo+fileOut+'.csv')
dirTo='/home/image/x-Stronomy/bindata/eDR3/KEB-0.50pc/'
files = [f for f in os.listdir(dirTo) if os.path.isfile(os.path.join(dirTo, f))]
for file in files:
    #if file[-3:]=='csv' or file[-3:]=='pdf' or file[-3:]=='png' or file[-4:]=='json' :
    #    continue
    print(file)
    picklefile=pd.read_csv(dirTo+file)
    fileOut=file.replace('.csv','')
    picklefile.to_pickle(dirTo+fileOut, protocol=4)
dirTo='/home/image/x-Stronomy/bindata/eDR3/stars/'
files = [f for f in os.listdir(dirTo) if os.path.isfile(os.path.join(dirTo, f))]
for file in files:
    print(file)
    picklefile=pd.read_csv(dirTo+file)
    fileOut=file.replace('.csv','')
    picklefile.to_pickle(dirTo+fileOut, protocol=4)