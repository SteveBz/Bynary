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
            'SOURCE_ID': row.source_id,
            'RA_': row.RA_,
            #'RA_ERROR': row.RA_ERROR,
            'DEC_': row.DEC_,
            #'DEC_ERROR': row.DEC_ERROR,
            #'PARALLAX': row.parallax,
            #'PARALLAX_ERROR': row.parallax_error,
            'phot_g_mean_mag': row.phot_g_mean_mag,
            #'PHOT_G_MEAN_FLUX_OVER_ERROR': row.phot_g_mean_flux_over_error,
            #'PHOT_BP_MEAN_FLUX_OVER_ERROR': row.phot_bp_mean_flux_over_error,
            #'PHOT_RP_MEAN_FLUX_OVER_ERROR': row.phot_rp_mean_flux_over_error,
            #'BP_RP': row.bp_rp,
            #'RADIAL_VELOCITY': row.radial_velocity,
            #'RADIAL_VELOCITY_ERROR':row.RADIAL_VELOCITY_ERROR,
            #'PHOT_VARIABLE_FLAG': row.PHOT_VARIABLE_FLAG,
            #'TEFF_VAL': row.TEFF_VAL,PHOT_G_MEAN_FLUX_OVER_ERROR
            #'A_G_VAL':row.A_G_VAL,
            'PMRA': row.pmra,
            'PMRA_ERROR': row.pmra_error,
            'PMDEC': row.pmdec,
            'PMDEC_ERROR': row.pmdec_error,
            'RELEASE_': row.RELEASE_,
            'RUWE': row.ruwe,
            'DIST': row.DIST,
            'PAIRING': ccdm,
            'INDEX': idx,
            
            'phot_g_mean_flux_over_error':row.phot_g_mean_flux_over_error,	
            #'phot_rp_mean_flux_over_error':row.phot_rp_mean_flux_over_error
            #'phot_bp_mean_flux_over_error':row.phot_bp_mean_flux_over_error
            'mass_flame':row.mass_flame,
            #'mass_flame_upper':row.mass_flame_upper
            #'mass_flame_lower':row.mass_flame_lower
            'age_flame':row.age_flame,
            #'age_flame_upper':row.age_flame_upper
            #'age_flame_lower':row.age_flame_lower
            'classprob_dsc_specmod_binarystar':row.classprob_dsc_specmod_binarystar
            }
        if not pd.isna(row.parallax):
            self.star_rows[idx]['PARALLAX']=row.parallax
        else:
            self.star_rows[idx]['PARALLAX']=0
        if not pd.isna(row.parallax_error):
            self.star_rows[idx]['PARALLAX_ERROR']=row.parallax_error
        else:
            self.star_rows[idx]['PARALLAX_ERROR']=0
            
        if not pd.isna(row.phot_g_mean_mag):
            self.star_rows[idx]['PHOT_G_MEAN_MAG']=row.phot_g_mean_mag
        else:
            self.star_rows[idx]['PHOT_G_MEAN_MAG']=0
            
        if not pd.isna(row.phot_g_mean_flux_over_error):
            self.star_rows[idx]['PHOT_G_MEAN_FLUX_OVER_ERROR']=row.phot_g_mean_flux_over_error
        else:
            self.star_rows[idx]['PHOT_G_MEAN_FLUX_OVER_ERROR']=0
            
        if not pd.isna(row.phot_bp_mean_flux_over_error):
            self.star_rows[idx]['PHOT_BP_MEAN_FLUX_OVER_ERROR']=row.phot_bp_mean_flux_over_error
        else:
            self.star_rows[idx]['PHOT_BP_MEAN_FLUX_OVER_ERROR']=0
            
        if not pd.isna(row.phot_rp_mean_flux_over_error):
            self.star_rows[idx]['PHOT_RP_MEAN_FLUX_OVER_ERROR']=row.phot_rp_mean_flux_over_error
        else:
            self.star_rows[idx]['PHOT_RP_MEAN_FLUX_OVER_ERROR']=0
            
        if not pd.isna(row.bp_rp):
            self.star_rows[idx]['BP_RP']=row.bp_rp
        else:
            self.star_rows[idx]['BP_RP']=0
            
        if not pd.isna(row.radial_velocity):
            self.star_rows[idx]['RADIAL_VELOCITY']=row.radial_velocity
        else:
            self.star_rows[idx]['RADIAL_VELOCITY']=0
            
        if not pd.isna(row.radial_velocity):
            self.star_rows[idx]['mass_flame']=row.mass_flame
        else:
            self.star_rows[idx]['mass_flame']=0
            
        if not pd.isna(row.radial_velocity):
            self.star_rows[idx]['age_flame']=row.age_flame
        else:
            self.star_rows[idx]['age_flame']=0
        #self.star_rows[idx]['PHOT_G_MEAN_MAG']=row.phot_g_mean_mag,
        #self.star_rows[idx]['PHOT_G_MEAN_FLUX_OVER_ERROR']=row.phot_g_mean_flux_over_error
        #self.star_rows[idx]['PHOT_BP_MEAN_FLUX_OVER_ERROR']=row.phot_bp_mean_flux_over_error
        #self.star_rows[idx]['PHOT_RP_MEAN_FLUX_OVER_ERROR']=row.phot_rp_mean_flux_over_error
        #self.star_rows[idx]['BP_RP']=row.bp_rp
        #self.star_rows[idx]['RADIAL_VELOCITY']=row.radial_velocity
        #print('self.star_rows[idx]',  self.star_rows[idx])   
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
            if float(self.primary.phot_g_mean_mag)>float(row.phot_g_mean_mag):
                self.star2=self.primary
                self.primary=row
            else:
                self.star2=row
        except Exception:
            self.star2=row
            
        self.R=float(self.calcR())
        # V and Verr are 2 D vectors.
        (self.V,self.Verr)=self.calcV()
        self.M=self.calcM()
        self.deselect()
        return (self.R, self.V, self.Verr, self.M)
    
    def calcM(self):
        
        #Solar mass = 1
        Mo=1
        #Calculate magnitudes of primary and secondary stars.
        if not pd.isnull(self.primary.mass_flame):
            Mass1=self.primary.mass_flame
        else:
            Mag1=float(self.primary.phot_g_mean_mag-5*math.log10(self.primary.DIST/10))
            #Calculate and return combined mass of binary
            Mass1=10**(.0725*(4.76-Mag1))*Mo
        
        if not pd.isnull(self.star2.mass_flame):
            Mass2=self.star2.mass_flame
        else:
            Mag2=float(self.star2.phot_g_mean_mag-5*math.log10(self.star2.DIST/10))
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
        #print(self.primary)
        try:
            # V Calculation (See WM Smart pp16-21)
            self.U1=-(const474*self.primary.pmra/self.primary.parallax)*math.sin((self.primary.RA_/360)*2*math.pi)-(const474*self.primary.pmdec/self.primary.parallax)*math.cos((self.primary.RA_/360)*2*math.pi)*math.sin((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.cos((self.primary.RA_/360)*2*math.pi)*math.cos((self.primary.DEC_/360)*2*math.pi)
            self.V1=(const474*self.primary.pmra/self.primary.parallax)*math.cos((self.primary.RA_/360)*2*math.pi)-(const474*self.primary.pmdec/self.primary.parallax)*math.sin((self.primary.RA_/360)*2*math.pi)*math.sin((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.sin((self.primary.RA_/360)*2*math.pi)*math.cos((self.primary.DEC_/360)*2*math.pi)
            self.W1=(const474*self.primary.pmdec/self.primary.parallax)*math.cos((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.sin((self.primary.DEC_/360)*2*math.pi)
            MuAlphaS=self.primary.pmra-(-self.U1*math.sin(self.star2.RA_*2*math.pi/360)+self.V1*math.cos(self.star2.RA_*2*math.pi/360))*self.star2.parallax/const474
            MuDeltaS=self.primary.pmdec-(-self.U1*math.cos(self.star2.RA_*2*math.pi/360)*math.sin(self.star2.DEC_*2*math.pi/360)-self.V1*math.sin(self.star2.RA_*2*math.pi/360)*math.sin(self.star2.DEC_*2*math.pi/360)+self.W1*math.cos(self.star2.DEC_*2*math.pi/360))*self.star2.parallax/const474
            
            meanParallax=(self.star2.parallax+self.primary.parallax)/2
            VelRA=abs(float(const474*(self.star2.pmra/self.star2.parallax-self.primary.pmra/self.primary.parallax+MuAlphaS/meanParallax)))
            VelDec=abs(float(const474*(self.star2.pmdec/self.star2.parallax-self.primary.pmdec/self.primary.parallax+MuDeltaS/meanParallax)))
            # V Error calculation
            VAlphaErr=float(const474*(self.star2.pmra_error/self.star2.parallax+self.primary.pmra_error/self.primary.parallax+abs(self.star2.pmra)*self.star2.parallax_error/self.star2.parallax**2+abs(self.primary.pmra)*self.primary.parallax_error/self.primary.parallax**2))
            VDeltaErr=float(const474*(self.star2.pmdec_error/self.star2.parallax+self.primary.pmdec_error/self.primary.parallax+abs(self.star2.pmdec)*self.star2.parallax_error/self.star2.parallax**2+abs(self.primary.pmdec)*self.primary.parallax_error/self.primary.parallax**2))
        except Exception:
            VelRA=0
            VAlphaErr=0
            VelDec=0
            VDeltaErr=0
        #Return Velocity array and error array
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
