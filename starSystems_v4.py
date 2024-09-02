#!/usr/bin/env python

from astropy.coordinates import Galactic, SkyCoord # pip3 install astropy
import astropy.units as u
import re
import math
import pandas as pd
class binaryStarSystems():

    def __init__(self, numberStars, Mass_Correction):
        self.binaryList={}
        #column_names = ["SOURCE_ID", "RA_", "RA_ERROR", "DEC_", "DEC_ERROR",
        #        "PARALLAX", "PARALLAX_ERROR", "PHOT_G_MEAN_MAG", "BP_RP", "RADIAL_VELOCITY",
        #        "RADIAL_VELOCITY_ERROR", "PHOT_VARIABLE_FLAG", "TEFF_VAL", "A_G_VAL",
        #        "PMRA", "PMRA_ERROR", "PMDEC", "PMDEC_ERROR" ]

        #self.star_rows = pd.DataFrame(columns=column_names)
        self.star_rows = {}
        self.index=0 #  zero-based index
        self.numberStars=numberStars
        self.Mass_Correction=float(Mass_Correction)
    
    def getIndex(self):
        #  zero-based index
        index=self.index
        self.index=self.index+1
        return index
        
    def addSystem(self, row, ccdm, rfactor=0):
        rowCopy = row.copy()
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
            'SOURCE_ID': rowCopy.source_id,
            'RA_': rowCopy.RA_,
            #'RA_ERROR': rowCopy.RA_ERROR,
            'DEC_': rowCopy.DEC_,
            #'DEC_ERROR': rowCopy.DEC_ERROR,
            #'PARALLAX': rowCopy.parallax,
            #'PARALLAX_ERROR': rowCopy.parallax_error,
            'phot_g_mean_mag': rowCopy.phot_g_mean_mag,
            #'PHOT_G_MEAN_FLUX_OVER_ERROR': rowCopy.phot_g_mean_flux_over_error,
            #'PHOT_BP_MEAN_FLUX_OVER_ERROR': rowCopy.phot_bp_mean_flux_over_error,
            #'PHOT_RP_MEAN_FLUX_OVER_ERROR': rowCopy.phot_rp_mean_flux_over_error,
            #'BP_RP': rowCopy.bp_rp,
            #'RADIAL_VELOCITY': rowCopy.radial_velocity,
            #'RADIAL_VELOCITY_ERROR':rowCopy.RADIAL_VELOCITY_ERROR,
            #'PHOT_VARIABLE_FLAG': rowCopy.PHOT_VARIABLE_FLAG,
            #'TEFF_VAL': rowCopy.TEFF_VAL,PHOT_G_MEAN_FLUX_OVER_ERROR
            #'A_G_VAL':rowCopy.A_G_VAL,
            'PMRA': rowCopy.pmra,
            'PMRA_ERROR': rowCopy.pmra_error,
            'PMDEC': rowCopy.pmdec,
            'PMDEC_ERROR': rowCopy.pmdec_error,
            'RELEASE_': rowCopy.RELEASE_,
            'RUWE': rowCopy.ruwe,
            'DIST': rowCopy.DIST,
            'PAIRING': ccdm,
            'INDEX': idx,
            
            'PARALLAX_PMRA_CORR':rowCopy.parallax_pmra_corr,
            'PARALLAX_PMDEC_CORR':rowCopy.parallax_pmdec_corr,
            'RA_PARALLAX_CORR':rowCopy.ra_parallax_corr,
            'DEC_PARALLAX_CORR':rowCopy.dec_parallax_corr,
            'RA_PMRA_CORR':rowCopy.ra_pmra_corr,
            'RA_PMDEC_CORR':rowCopy.ra_pmdec_corr,
            'DEC_PMRA_CORR':rowCopy.dec_pmra_corr,
            'DEC_PMDEC_CORR':rowCopy.dec_pmdec_corr,
            'PMRA_PMDEC_CORR':rowCopy.pmra_pmdec_corr,
            'PHOT_BP_MEAN_FLUX':rowCopy.phot_bp_mean_flux,
            'PHOT_RP_MEAN_FLUX':rowCopy.phot_rp_mean_flux,
            'PHOT_BP_MEAN_FLUX_ERROR':rowCopy.phot_bp_mean_flux_error,
            'PHOT_RP_MEAN_FLUX_ERROR':rowCopy.phot_rp_mean_flux_error,
                        
            'phot_g_mean_flux_over_error':rowCopy.phot_g_mean_flux_over_error,	
            #'phot_rp_mean_flux_over_error':rowCopy.phot_rp_mean_flux_over_error
            #'phot_bp_mean_flux_over_error':rowCopy.phot_bp_mean_flux_over_error
            'mass_flame':rowCopy.mass_flame,
            #'mass_flame_upper':rowCopy.mass_flame_upper
            #'mass_flame_lower':rowCopy.mass_flame_lower
            'age_flame':rowCopy.age_flame,
            #'age_flame_upper':rowCopy.age_flame_upper
            #'age_flame_lower':rowCopy.age_flame_lower
            'classprob_dsc_specmod_binarystar':rowCopy.classprob_dsc_specmod_binarystar
            }
        if not pd.isna(rowCopy.parallax):
            self.star_rows[idx]['PARALLAX']=rowCopy.parallax
        else:
            self.star_rows[idx]['PARALLAX']=0
            rowCopy.parallax=0
        if not pd.isna(rowCopy.parallax_error):
            self.star_rows[idx]['PARALLAX_ERROR']=rowCopy.parallax_error
        else:
            self.star_rows[idx]['PARALLAX_ERROR']=0
            rowCopy.parallax_error=0
        if not pd.isna(rowCopy.phot_g_mean_mag):
            self.star_rows[idx]['PHOT_G_MEAN_MAG']=rowCopy.phot_g_mean_mag
        else:
            self.star_rows[idx]['PHOT_G_MEAN_MAG']=0
            rowCopy.phot_g_mean_mag=0
        if not pd.isna(rowCopy.phot_g_mean_flux_over_error):
            self.star_rows[idx]['PHOT_G_MEAN_FLUX_OVER_ERROR']=rowCopy.phot_g_mean_flux_over_error
        else:
            self.star_rows[idx]['PHOT_G_MEAN_FLUX_OVER_ERROR']=0
            rowCopy.phot_g_mean_flux_over_error=0
        if not pd.isna(rowCopy.phot_bp_mean_flux_over_error):
            self.star_rows[idx]['PHOT_BP_MEAN_FLUX_OVER_ERROR']=rowCopy.phot_bp_mean_flux_over_error
        else:
            self.star_rows[idx]['PHOT_BP_MEAN_FLUX_OVER_ERROR']=0
            rowCopy.phot_bp_mean_flux_over_error=0
        if not pd.isna(rowCopy.phot_rp_mean_flux_over_error):
            self.star_rows[idx]['PHOT_RP_MEAN_FLUX_OVER_ERROR']=rowCopy.phot_rp_mean_flux_over_error
        else:
            self.star_rows[idx]['PHOT_RP_MEAN_FLUX_OVER_ERROR']=0
            rowCopy.phot_rp_mean_flux_over_error=0
        if not pd.isna(rowCopy.bp_rp):
            self.star_rows[idx]['BP_RP']=rowCopy.bp_rp
        else:
            self.star_rows[idx]['BP_RP']=0
            rowCopy.bp_rp=0            
        if not pd.isna(rowCopy.radial_velocity):
            self.star_rows[idx]['RADIAL_VELOCITY']=rowCopy.radial_velocity
        else:
            self.star_rows[idx]['RADIAL_VELOCITY']=0
            rowCopy.radial_velocity=0            
        if not pd.isna(rowCopy.mass_flame):
            self.star_rows[idx]['mass_flame']=rowCopy.mass_flame
        else:
            self.star_rows[idx]['mass_flame']=0
            rowCopy.mass_flame=0
        if not pd.isna(rowCopy.age_flame):
            self.star_rows[idx]['age_flame']=rowCopy.age_flame
        else:
            self.star_rows[idx]['age_flame']=0
            rowCopy.age_flame=0
        #self.star_rows[idx]['PHOT_G_MEAN_MAG']=rowCopy.phot_g_mean_mag,
        #self.star_rows[idx]['PHOT_G_MEAN_FLUX_OVER_ERROR']=rowCopy.phot_g_mean_flux_over_error
        #self.star_rows[idx]['PHOT_BP_MEAN_FLUX_OVER_ERROR']=rowCopy.phot_bp_mean_flux_over_error
        #self.star_rows[idx]['PHOT_RP_MEAN_FLUX_OVER_ERROR']=rowCopy.phot_rp_mean_flux_over_error
        #self.star_rows[idx]['BP_RP']=rowCopy.bp_rp
        #self.star_rows[idx]['RADIAL_VELOCITY']=rowCopy.radial_velocity
        #print('self.star_rows[idx]',  self.star_rows[idx])   
        label=''
        if str(ccdm) in self.binaryList.keys():
            binary=self.binaryList[str(ccdm)]
            #(R, V, Verr, M) =binary.binaryStarSystem(self.star_rows[idx], str(ccdm))
            (R, V, Verr, M) =binary.binaryStarSystem(rowCopy, str(ccdm))
            BIN=1
        else:
            BIN=0
            #unary = starSystem(self.star_rows[idx], rfactor=0)
            unary = starSystem(rowCopy, self.Mass_Correction, rfactor=0)
            self.binaryList[str(ccdm)]=unary
        
        return (ccdm, R, V, Verr, M, BIN)
        
    def getStar_rows(self):
        
        return self.star_rows

class starSystem():
    
    def __init__(self, row, mass_correction, rfactor=0):
        self.mass_correction=mass_correction
        self.primary=row
        self.selectedCount=0
        self.rfactor=rfactor
        
    def binaryStarSystem(self, row, ccdm):
        #This is only called when both binary stars are defined.
        try:
            if float(self.primary.phot_g_mean_mag)>float(row.phot_g_mean_mag):
                self.star2=self.primary
                self.primary=row
                #row.mass_calc=self.primary.mass_calc
            else:
                self.star2=row
                #row.mass_calc=self.star2.mass_calc
        except Exception:
            self.star2=row
            
        (self.primary.gal_l, self.primary.gal_b)=self.calcGal(self.primary.RA_, self.primary.DEC_)
        (self.star2.gal_l, self.star2.gal_b)=self.calcGal(self.star2.RA_, self.star2.DEC_)
        self.R=float(self.calcR())
        # V and Verr are 2 D vectors.
        (self.V,self.Verr)=self.calcV()
        (self.M)=self.calcM() # , self.mass_flame_1,self.mass_flame_2,self.mass_calc_1,self.mass_calc_2
        
        return (self.R, self.V, self.Verr, self.M)
    def calcGal(self, ra, dec):
        
        # Convert to Galactic Coords.
        sc = SkyCoord(ra=ra*u.deg,dec=dec*u.deg)
        gal_l=str(sc.galactic.l)
        try:
            deg, minutes, seconds, fraction  =  re.split('[dm.]', gal_l)
        except:
            #self.parent.StatusBarProcessing(f'Missing decimal point in gal_l={gal_l}')
            deg, minutes, seconds, fraction  =  re.split('[dms]', gal_l)
        gal_l=float(deg) + float(minutes)/60  + float(seconds)/3600
        gal_l=(gal_l+180) % 360 -180
        
        gal_b=str(sc.galactic.b)
        try:
            deg, minutes, seconds, fraction  =  re.split('[dm.]', gal_b)
        except:
            #self.parent.StatusBarProcessing(f'Missing decimal point in gal_b={gal_b}')
            deg, minutes, seconds, fraction  =  re.split('[dms]', gal_b)
        gal_b=float(deg) + float(minutes)/60 + float(seconds)/3600
        return (gal_l, gal_b)
        
    def calcM(self):
        #global gl_cfg, Mass_Correction
        #Solar mass = 1
        Mo=1
        #Mass_Correction=float(gl_cfg.getItem('mass-adjust','RETRIEVAL', '0.05'))  #  0.05 correction to allow for low mass dispersion
        
        #Calculate magnitudes and masses of primary stars.
        Mag1=float(self.primary.phot_g_mean_mag-5*math.log10(self.primary.DIST/10))
        Mass_Calc=10**(.0725*(4.76-Mag1))*Mo
        if Mass_Calc < 0.7:
            Mass_Calc=Mass_Calc+self.mass_correction  
            
        self.primary.mass_calc=Mass_Calc
        
        #If available use FLAME mass for primary star, otherwise use calculated mass
        if not pd.isnull(self.primary.mass_flame) and self.primary.mass_flame:
            Mass1=self.primary.mass_flame
        else:
            Mass1=Mass_Calc
        
        #Calculate magnitudes and masses of secondary stars.
        Mag2=float(self.star2.phot_g_mean_mag-5*math.log10(self.star2.DIST/10))
        Mass_Calc=10**(.0725*(4.76-Mag2))*Mo
        if Mass_Calc < 0.7:
            Mass_Calc=Mass_Calc+self.mass_correction  
        self.star2.mass_calc=Mass_Calc
        
        #If available use FLAME mass for secondary star, otherwise use calculated mass
        if not pd.isnull(self.star2.mass_flame) and self.star2.mass_flame:
            Mass2=self.star2.mass_flame
        else:
            Mass2=Mass_Calc
            
        #Return combined mass of binary
        return (Mass1+Mass2) #, self.primary.mass_flame, self.star2.mass_flame, self.primary.mass_calc, self.star2.mass_calc)
    
    def calcR(self):
        
        #Step 1 - Separation (R) 
        #Calculate Separation (R) of two binary stars. 
        #
        # 1.1) Calculate the cosine of the angle, theta, between the stars as seen from Earth.  Ie the very small angle between the distances d1 & d2 to the primary and secondary
        #   stars.  All angles are in radians. 
        #
        #   cos(theta) = sin (DEC1) sin (DEC2) + cos (DEC1) cos (DEC2) cos (RA1 - RA2) 
        #
        #   [NB Watch out for RA1 - RA2 wraps around and gives a large number.  In this case subtract 2pi.] 
        #
        #   1.2) Calculate R, the 2D distance between the stars. 
        #
        #   R^2 = (d1 + d2) ^2 (1 - cos(theta))/2 
        try:
            cosTheta=math.sin(self.star2.DEC_*2*math.pi/360)* math.sin(self.primary.DEC_*2*math.pi/360) + math.cos(self.star2.DEC_*2*math.pi/360) *math.cos(self.primary.DEC_*2*math.pi/360) *math.cos(self.star2.RA_*2*math.pi/360 - self.primary.RA_*2*math.pi/360)
        except Exception:
            return 0
        try:
            if 1:
                d1=self.primary.DIST*self.star2.DIST_ERR**2
                d2=self.star2.DIST*self.primary.DIST_ERR**2
                e1=self.primary.DIST_ERR**2
                e2=self.star2.DIST_ERR**2
        
                R=(d1+d2)*math.sqrt(2.0-2.0*cosTheta)/(e1+e2)
            else:
                R=math.sqrt(2)/2*(float(self.primary.DIST)+(self.star2.DIST))*math.sqrt(1.0-cosTheta)
        except Exception:
            return 0
        return R
    
    def calcV(self):
        const474=4.740470464
        #print(self.primary)
        #try:
            ## UVW Calculation (See WM Smart pp16-21) Gaia PMRA is already multiplied by cos(dec) by Gaia.
            #self.U1=-(const474*self.primary.pmra/self.primary.parallax)*math.sin((self.primary.RA_/360)*2*math.pi)-(const474*self.primary.pmdec/self.primary.parallax)*math.cos((self.primary.RA_/360)*2*math.pi)*math.sin((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.cos((self.primary.RA_/360)*2*math.pi)*math.cos((self.primary.DEC_/360)*2*math.pi)
            #self.V1=(const474*self.primary.pmra/self.primary.parallax)*math.cos((self.primary.RA_/360)*2*math.pi)-(const474*self.primary.pmdec/self.primary.parallax)*math.sin((self.primary.RA_/360)*2*math.pi)*math.sin((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.sin((self.primary.RA_/360)*2*math.pi)*math.cos((self.primary.DEC_/360)*2*math.pi)
            #self.W1=(const474*self.primary.pmdec/self.primary.parallax)*math.cos((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.sin((self.primary.DEC_/360)*2*math.pi)
            ##Sperical Correction
            #MuAlphaS=self.primary.pmra-(-self.U1*math.sin(self.star2.RA_*2*math.pi/360)+self.V1*math.cos(self.star2.RA_*2*math.pi/360))*self.star2.parallax/const474
            #MuDeltaS=self.primary.pmdec-(-self.U1*math.cos(self.star2.RA_*2*math.pi/360)*math.sin(self.star2.DEC_*2*math.pi/360)-self.V1*math.sin(self.star2.RA_*2*math.pi/360)*math.sin(self.star2.DEC_*2*math.pi/360)+self.W1*math.cos(self.star2.DEC_*2*math.pi/360))*self.star2.parallax/const474

            #if 1:
            #Calulate mean, inverse-variance-weighted parallax
        sigma_squared_px_1 = self.primary.parallax_error**2
        sigma_squared_px_2 = self.star2.parallax_error**2
        varpi_1=self.primary.parallax*sigma_squared_px_2
        varpi_2=self.star2.parallax*sigma_squared_px_1
        meanParallax=(varpi_1+varpi_2)/(sigma_squared_px_1+sigma_squared_px_2)
        v_alpha_1 = const474*self.primary.pmra/meanParallax
        v_alpha_2 = const474*self.star2.pmra/meanParallax
        v_delta_1 = const474*self.primary.pmdec/meanParallax
        v_delta_2 = const474*self.star2.pmdec/meanParallax
        
        # UVW Calculation (See WM Smart pp16-21) Gaia PMRA is already multiplied by cos(dec) by Gaia.
        self.U1=-(v_alpha_1)*math.sin((self.primary.RA_/360)*2*math.pi)-(v_delta_1)*math.cos((self.primary.RA_/360)*2*math.pi)*math.sin((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.cos((self.primary.RA_/360)*2*math.pi)*math.cos((self.primary.DEC_/360)*2*math.pi)
        self.V1=(v_alpha_1)*math.cos((self.primary.RA_/360)*2*math.pi)-(v_delta_1)*math.sin((self.primary.RA_/360)*2*math.pi)*math.sin((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.sin((self.primary.RA_/360)*2*math.pi)*math.cos((self.primary.DEC_/360)*2*math.pi)
        self.W1=(v_delta_1)*math.cos((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.sin((self.primary.DEC_/360)*2*math.pi)
                #Sperical Correction
        ## UVW Calculation (See WM Smart pp16-21) Gaia PMRA is already multiplied by cos(dec) by Gaia.
        #self.U1=-v_alpha_1*math.sin((self.primary.RA_/360)*2*math.pi)-v_delta_1*math.cos((self.primary.RA_/360)*2*math.pi)*math.sin((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.cos((self.primary.RA_/360)*2*math.pi)*math.cos((self.primary.DEC_/360)*2*math.pi)
        #self.V1=v_alpha_1*math.cos((self.primary.RA_/360)*2*math.pi)-v_delta_1*math.sin((self.primary.RA_/360)*2*math.pi)*math.sin((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.sin((self.primary.RA_/360)*2*math.pi)*math.cos((self.primary.DEC_/360)*2*math.pi)
        #self.W1=v_alpha_1*math.cos((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.sin((self.primary.DEC_/360)*2*math.pi)
        #Sperical Correction
        MuAlphaS=self.primary.pmra-(-self.U1*math.sin(self.star2.RA_*2*math.pi/360)+self.V1*math.cos(self.star2.RA_*2*math.pi/360))*meanParallax/const474
        MuDeltaS=self.primary.pmdec-(-self.U1*math.cos(self.star2.RA_*2*math.pi/360)*math.sin(self.star2.DEC_*2*math.pi/360)-self.V1*math.sin(self.star2.RA_*2*math.pi/360)*math.sin(self.star2.DEC_*2*math.pi/360)+self.W1*math.cos(self.star2.DEC_*2*math.pi/360))*meanParallax/const474
        
        VelRA=abs(float(const474*(self.star2.pmra-self.primary.pmra+MuAlphaS)/meanParallax))
        v_alpha=VelRA
        VelDec=abs(float(const474*(self.star2.pmdec-self.primary.pmdec+MuDeltaS)/meanParallax))
        v_delta_=VelDec
        
        # Velocity Error calculation (eq 9 and 10)
        varpi_prime_1 = sigma_squared_px_2/(sigma_squared_px_1+sigma_squared_px_2)
        varpi_prime_2 = sigma_squared_px_1/(sigma_squared_px_1+sigma_squared_px_2)

        sigma_px_1 = self.primary.parallax_error
        sigma_px_2 = self.star2.parallax_error
        sigma_mu_alpha_1 = self.primary.pmra_error
        sigma_mu_alpha_2 = self.star2.pmra_error
        sigma_mu_delta_1 = self.primary.pmdec_error
        sigma_mu_delta_2 = self.star2.pmdec_error

        sigma_squared_v_alpha = (v_alpha**2 * varpi_prime_1**2 * sigma_squared_px_1 - \
                                v_alpha * varpi_prime_1 * const474 * 2 * sigma_px_1 * sigma_mu_alpha_1 * self.primary.parallax_pmra_corr + \
                                const474 ** 2 * sigma_mu_alpha_1**2 + \
                                v_alpha**2 * varpi_prime_2**2 * sigma_squared_px_2 - \
                                v_alpha * varpi_prime_2 * const474 * 2 * sigma_px_2 * sigma_mu_alpha_2 * self.primary.parallax_pmra_corr+ \
                                const474 ** 2 * sigma_mu_alpha_2**2 )/meanParallax**2 
        sigma_squared_v_delta = (v_delta_**2 * varpi_prime_1**2 * sigma_squared_px_1 - \
                                v_delta_ * varpi_prime_1 * const474 * 2 * sigma_px_1 * sigma_mu_delta_1 * self.primary.parallax_pmra_corr + \
                                const474 ** 2 * sigma_mu_delta_1**2 + \
                                v_delta_**2 * varpi_prime_2**2 * sigma_squared_px_2 - \
                                v_delta_ * varpi_prime_2 * const474 * 2 * sigma_px_2 * sigma_mu_delta_2 * self.primary.parallax_pmra_corr + \
                                const474 ** 2 * sigma_mu_delta_2**2 )/meanParallax**2 

        VAlphaErr=float(math.sqrt(sigma_squared_v_alpha))
        VDeltaErr=float(math.sqrt(sigma_squared_v_delta))
                #VAlphaErr=float(const474*(math.sqrt(self.star2.pmra_error**2+self.primary.pmra_error**2+(self.star2.pmra-self.primary.pmra)**2 * (self.star2.parallax_error**2 +self.primary.parallax**2)/(4*meanParallax**2))/meanParallax))
                #VDeltaErr=float(const474*(math.sqrt(self.star2.pmdec_error**2+self.primary.pmdec_error**2+(self.star2.pmdec-self.primary.pmdec)**2 * (self.star2.parallax_error**2 +self.primary.parallax**2)/(4*meanParallax**2))/meanParallax))
                #VDeltaErr=float(const474*(math.sqrt(self.star2.pmdec_error**2+self.primary.pmdec_error**2+(self.star2.pmdec*self.star2.parallax_error/self.star2.parallax)**2+(self.primary.pmdec*self.primary.parallax_error/self.primary.parallax)**2))/meanParallax)
                #VAlphaErr=float(const474*(math.sqrt(self.star2.pmra_error**2+self.primary.pmra_error**2))/meanParallax)
                #VDeltaErr=float(const474*(math.sqrt(self.star2.pmdec_error**2+self.primary.pmdec_error**2))/meanParallax)
                #VAlphaErr=0.0
                #VDeltaErr=0.0
            #else:
            #    
            #    # UVW Calculation (See WM Smart pp16-21) Gaia PMRA is already multiplied by cos(dec) by Gaia.
            #    self.U1=-(const474*self.primary.pmra/self.primary.parallax)*math.sin((self.primary.RA_/360)*2*math.pi)-(const474*self.primary.pmdec/self.primary.parallax)*math.cos((self.primary.RA_/360)*2*math.pi)*math.sin((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.cos((self.primary.RA_/360)*2*math.pi)*math.cos((self.primary.DEC_/360)*2*math.pi)
            #    self.V1=(const474*self.primary.pmra/self.primary.parallax)*math.cos((self.primary.RA_/360)*2*math.pi)-(const474*self.primary.pmdec/self.primary.parallax)*math.sin((self.primary.RA_/360)*2*math.pi)*math.sin((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.sin((self.primary.RA_/360)*2*math.pi)*math.cos((self.primary.DEC_/360)*2*math.pi)
            #    self.W1=(const474*self.primary.pmdec/self.primary.parallax)*math.cos((self.primary.DEC_/360)*2*math.pi)+self.primary.radial_velocity*math.sin((self.primary.DEC_/360)*2*math.pi)
            #    #Sperical Correction
            #    MuAlphaS=self.primary.pmra-(-self.U1*math.sin(self.star2.RA_*2*math.pi/360)+self.V1*math.cos(self.star2.RA_*2*math.pi/360))*self.star2.parallax/const474
            #    MuDeltaS=self.primary.pmdec-(-self.U1*math.cos(self.star2.RA_*2*math.pi/360)*math.sin(self.star2.DEC_*2*math.pi/360)-self.V1*math.sin(self.star2.RA_*2*math.pi/360)*math.sin(self.star2.DEC_*2*math.pi/360)+self.W1*math.cos(self.star2.DEC_*2*math.pi/360))*self.star2.parallax/const474
            #    meanParallax=(self.star2.parallax+self.primary.parallax)/2
            #    
            #    VelRA=abs(float(const474*(self.star2.pmra/self.star2.parallax-self.primary.pmra/self.primary.parallax+MuAlphaS/meanParallax)))
            #    VelDec=abs(float(const474*(self.star2.pmdec/self.star2.parallax-self.primary.pmdec/self.primary.parallax+MuDeltaS/meanParallax)))
            #    # Velocity Error calculation
            #    VAlphaErr=float(const474*(self.star2.pmra_error/self.star2.parallax+self.primary.pmra_error/self.primary.parallax+abs(self.star2.pmra)*self.star2.parallax_error/self.star2.parallax**2+abs(self.primary.pmra)*self.primary.parallax_error/self.primary.parallax**2))
            #    VDeltaErr=float(const474*(self.star2.pmdec_error/self.star2.parallax+self.primary.pmdec_error/self.primary.parallax+abs(self.star2.pmdec)*self.star2.parallax_error/self.star2.parallax**2+abs(self.primary.pmdec)*self.primary.parallax_error/self.primary.parallax**2))
        #except Exception:
        #    VelRA=0
        #    VAlphaErr=0
        #    VelDec=0
        #    VDeltaErr=0
        #Return Velocity array and error array
        #print([VelRA,VelDec],[VAlphaErr,VDeltaErr])
        return ([VelRA,VelDec],[VAlphaErr,VDeltaErr])
    