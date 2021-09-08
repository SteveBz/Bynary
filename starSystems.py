#!/usr/bin/env python

import math
import pandas as pd
class binaryStarSystems():

    def __init__(self, numberStars):
        self.binaryList={}
        #column_names = ["SOURCE_ID", "RA_", "RA_ERROR", "DEC_", "DEC_ERROR",
        #        "PARALLAX", "PARALLAX_ERROR", "PHOT_G_MEAN_MAG", "BP_RP", "RADIAL_VELOCITY",
        #        "RADIAL_VELOCITY_ERROR", "PHOT_VARIABLE_FLAG", "TEFF_VAL", "A_G_VAL",
        #        "PMRA", "PMRA_ERROR", "PMDEC", "PMDEC_ERROR" ]

        #self.star_rows = pd.DataFrame(columns=column_names)
        self.star_rows = {}
        self.index=0 #  zero-based index
        self.numberStars=numberStars
    
    def getIndex(self):
        #  zero-based index
        index=self.index
        self.index=self.index+1
        return index
        
    def addSystem(self, row, ccdm, rfactor=0):
        R=0             # Separation
        V=[0.0,0.0]     # Radial velocity (RA and DEC float)
        Verr=[0.0,0.0]  # Velocity error bar (RA and DEC float)
        BIN=0           # Bianry or not.
        M=0             # Total combined mass
        # If it's already in the list, then this entry makes it binary
        # If not, it's the first entry and it might be binary or unary, we set it as unary.
        #
                  
        # Using 'Pair' as the column name
        # and equating it to the list
        idx=self.getIndex()
        self.star_rows[idx]={
            'SOURCE_ID': row.SOURCE_ID,
            'RA_': row.RA_,
            #'RA_ERROR': row.RA_ERROR,
            'DEC_': row.DEC_,
            #'DEC_ERROR': row.DEC_ERROR,
            'PARALLAX': row.PARALLAX,
            'PARALLAX_ERROR': row.PARALLAX_ERROR,
            'PHOT_G_MEAN_MAG': row.PHOT_G_MEAN_MAG,
            'BP_RP': row.BP_RP,
            'RADIAL_VELOCITY': row.RADIAL_VELOCITY,
            #'RADIAL_VELOCITY_ERROR':row.RADIAL_VELOCITY_ERROR,
            #'PHOT_VARIABLE_FLAG': row.PHOT_VARIABLE_FLAG,
            #'TEFF_VAL': row.TEFF_VAL,
            #'A_G_VAL':row.A_G_VAL,
            'PMRA': row.PMRA,
            'PMRA_ERROR': row.PMRA_ERROR,
            'PMDEC': row.PMDEC,
            'PMDEC_ERROR': row.PMDEC_ERROR,
            'RELEASE_': row.RELEASE_,
            'RUWE': row.RUWE,
            'DIST': row.DIST,
            'PAIRING': ccdm,
            'INDEX': idx}
                
        label=''
        if str(ccdm) in self.binaryList.keys():
            binary=self.binaryList[str(ccdm)]
            (R, V, Verr, M) =binary.binaryStarSystem(row, str(ccdm))
            BIN=1
        else:
            BIN=0
            unary = starSystem(row, rfactor=0)
            self.binaryList[str(ccdm)]=unary
        
        return (ccdm, R, V, Verr, M, BIN)
        
    def getStar_rows(self):
        
        return self.star_rows

class starSystem():
    
    def __init__(self, row, rfactor=0):
        self.primary=row
        self.selectedCount=0
        self.rfactor=rfactor
        
    def binaryStarSystem(self, row, ccdm):
        
        try:
            if float(self.primary.PHOT_G_MEAN_MAG)>float(row.PHOT_G_MEAN_MAG):
                self.star2=self.primary
                self.primary=row
            else:
                self.star2=row
        except Exception:
            self.star2=row
            
        self.R=float(self.calcR())
        # V and Verr are 2 D vectors.
        (self.V,self.Verr)=self.calcV()
        try:
            self.M=self.calcM()
        except Exception:
            self.M=0
        self.deselect()
        return (self.R, self.V, self.Verr, self.M)
    
    def calcM(self):
        
        #Calculate magnitudes of primary and secondary stars.
        Mag1=float(self.primary.PHOT_G_MEAN_MAG-5*math.log10(self.primary.DIST/10))
        Mag2=float(self.star2.PHOT_G_MEAN_MAG-5*math.log10(self.star2.DIST/10))
        #Solar mass = 1
        Mo=1
        #Calculate and return combined mass of binary
        Mass1=10**(.0725*(4.76-Mag1))*Mo
        Mass2=10**(.0725*(4.76-Mag2))*Mo
        return Mass1+Mass2
    
    def calcR(self):
        try:
            cosTheta=math.sin(self.star2.DEC_*2*math.pi/360)* math.sin(self.primary.DEC_*2*math.pi/360) + math.cos(self.star2.DEC_*2*math.pi/360) *math.cos(self.primary.DEC_*2*math.pi/360) *math.cos(self.star2.RA_*2*math.pi/360 - self.primary.RA_*2*math.pi/360)
            R=math.sqrt(2)/2*(float(self.primary.DIST)+(self.star2.DIST))*math.sqrt(1.0-cosTheta)
        except Exception:
            R=0
        return R
    
    def calcV(self):
        const474=4.74
        
        try:
            # V Calculation
            self.U1=-(const474*self.primary.PMRA/self.primary.PARALLAX)*math.sin(self.primary.RA_/360*2*math.pi)-(const474*self.primary.PMDEC/self.primary.PARALLAX)*math.cos(self.primary.RA_/360*2*math.pi)*math.sin(self.primary.DEC_/360*2*math.pi)+self.primary.RADIAL_VELOCITY*math.cos(self.primary.RA_/360*2*math.pi)*math.cos(self.primary.DEC_/360*2*math.pi)
            self.V1=(const474*self.primary.PMRA/self.primary.PARALLAX)*math.cos(self.primary.RA_/360*2*math.pi)-(const474*self.primary.PMDEC/self.primary.PARALLAX)*math.sin(self.primary.RA_/360*2*math.pi)*math.sin(self.primary.DEC_/360*2*math.pi)+self.primary.RADIAL_VELOCITY*math.sin(self.primary.RA_/360*2*math.pi)*math.cos(self.primary.DEC_/360*2*math.pi)
            self.W1=(const474*self.primary.PMDEC/self.primary.PARALLAX)*math.cos(self.primary.DEC_/360*2*math.pi)+self.primary.RADIAL_VELOCITY*math.sin(self.primary.DEC_/360*2*math.pi)
            MuAlphaS=self.primary.PMRA-(-self.U1*math.sin(self.star2.RA_*2*math.pi/360)+self.V1*math.cos(self.star2.RA_*2*math.pi/360))*self.star2.PARALLAX/const474
            MuDeltaS=self.primary.PMDEC-(-self.U1*math.cos(self.star2.RA_*2*math.pi/360)*math.sin(self.star2.DEC_*2*math.pi/360)-self.V1*math.sin(self.star2.RA_*2*math.pi/360)*math.sin(self.star2.DEC_*2*math.pi/360)+self.W1*math.cos(self.star2.DEC_*2*math.pi/360))*self.star2.PARALLAX/const474
            VelRA=abs(float(const474*(self.star2.PMRA/self.star2.PARALLAX-self.primary.PMRA/self.primary.PARALLAX+MuAlphaS/self.star2.PARALLAX)))
            VelDec=abs(float(const474*(self.star2.PMDEC/self.star2.PARALLAX-self.primary.PMDEC/self.primary.PARALLAX+MuDeltaS/self.primary.PARALLAX)))
            #V=math.sqrt(VelRA**2+VelDec**2)
            # V Error calculation
            VAlphaErr=abs(float(const474*(self.star2.PMRA_ERROR/self.star2.PARALLAX+self.primary.PMRA_ERROR/self.primary.PARALLAX+self.star2.RA_*self.star2.PARALLAX_ERROR/self.star2.PARALLAX**2+self.primary.RA_*self.primary.PARALLAX_ERROR/self.primary.PARALLAX**2)))
            VDeltaErr=abs(float(const474*(self.star2.PMDEC_ERROR/self.star2.PARALLAX+self.primary.PMDEC_ERROR/self.primary.PARALLAX+self.star2.DEC_*self.star2.PARALLAX_ERROR/self.star2.PARALLAX**2+self.primary.DEC_*self.primary.PARALLAX_ERROR/self.primary.PARALLAX**2)))
            #Verr = abs(2*(VelRA*VAlphaErr + VelDec*VDeltaErr))
        except Exception:
            #V=0
            #Verr=0
            VelRA=0
            VAlphaErr=0
            VelDec=0
            VDeltaErr=0
        #print (f'VelRA = {float(VelRA)}')
        return ([VelRA,VelDec],[VAlphaErr,VDeltaErr])
    
    def deselect(self):
        if self.rfactor:
            if abs(self.primary.DIST - self.star2.DIST) > self.R*int(self.rfactor):
                self.V = math.nan
        
        #if self.primary.source_id  in self.selected:
        #    self.selectedCount=self.selectedCount+1
        #    print(self.selectedCount)
        pass
    
    def printDetails(self, ccdm):
        if not hasattr(self, 'star2'):
            pass
            #print (ccdm)
        
#        #################################  Table Header (Start) #####################################################################
