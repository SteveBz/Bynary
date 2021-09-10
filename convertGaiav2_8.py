#!/usr/bin/env python

 #pip install fastparquet
 #pip install pyarrow
 #pip install pandas 
import os
import time
import pandas as pd
import ashla.data_access as da
import sys, inspect, math

import datetime
from numpy import arange, sin, pi # pip3 install numpy
import numpy as np
import csv
import json

import SQLLib
import db              # For star/observing database.
dbiStro=db.db()
global iStro
iStro=dbiStro.conFbdb('Localhost:/home/image/x-Stronomy/binary.fdb', 'sysdba', 'masterkey')  # chmod +777 Binaries-DB-30.fdb 
global curiStro
curiStro=iStro.cursor()

query=[0]
#
    
Gaia50000Select="""-- Binary star selection ADQL from K el Badry paper.  Comments by S Cookson.
-- Pair distance is angular distance. Other fields removed for separate star data download.
-- It is expected that the star data is downloaded once - about 8 million stars - and the binaries are downloaded many times.
-- This separation of data speeds up the binary downloads.
SELECT g2.source_id as source_id2, t1.source_id, t1.dr2_radial_velocity as radial_velocity, g2.dr2_radial_velocity as radial_velocity2, distance(POINT('ICRS', t1.ra, t1.dec), POINT('ICRS', g2.ra, g2.dec)) AS pairdistance
"""
# Comments for CICLE parameter
#"""
#The physical separation of a pair is theta*d, where theta is the angular separation (in radians), and d is the distance. The distance in parsecs is d = 1000/parallax,
#where the Gaia parallaxes are in mas. Finally, the CIRCLE function wants an angular separation in degrees (not radians). So:
#
#theta [rad] * d [pc] < 0.24 
#theta [deg] * d [pc] < (0.24 * pi/180)
#theta [deg] * 1000/parallax [mas] < (0.24 * 180/pi)
#theta [deg]/parallax [mas] < (0.24 * 180/pi)/1000
#
#And (0.24 * 180/pi)/1000 = 1.4e-2
#
#So if you wanted e.g. 1 pc, you would replace 1.4e-2 with 0.0573. '
#"""
#"""
separation=0.50
pc=float(0.0573*separation)
print(pc)
nsigma=8
releaseIn='test'
releaseOut='test'
catalogue="testc"
HPS=[]
HPS.extend(range(0,2))
print (HPS)
#Count records only
countOnly=False
countMe=0
forceIt=False # Force download
step=1

count=0
Gaia50000Where=f"""
    WHERE
            -- The '!=' symbol makes sure they are not the same star.
            -- The '<' sign makes sure that only pair AB is included not BA.
            -- You can use either
            t1.source_id < g2.source_id
        AND
            -- Where star 2 is within a defined radius of star 1 (see note)
            1 = contains(POINT('ICRS', g2.ra, g2.dec), CIRCLE('ICRS', t1.ra, t1.dec,{pc}*t1.parallax))
        AND
            -- And radial separation minus ...
            abs(1/t1.parallax - 1/g2.parallax) -
            -- 2 * pi()/180 * 'in the plane separation'/parallax
            2*0.01745*distance(POINT('ICRS', t1.ra, t1.dec), POINT('ICRS', g2.ra, g2.dec))/t1.parallax
            < 3*sqrt(power(t1.parallax_error,2)/power(t1.parallax, 4) + power(g2.parallax_error, 2)/power(g2.parallax, 4))
    --    AND
    --        -- Relative velocity in the plane of the sky - Pythagoras. No spherical correction (pp 15-16 WM Smart).
    --	      -- Section removed because non-Newtonian movement deselected.
    --        sqrt(power((t1.pmra - g2.pmra), 2) + power((t1.pmdec - g2.pmdec), 2))
    --        -- Newtonian line (eq4 in the paper)
    --        - (7.42e-3 * power(t1.parallax, 1.5) * power(distance(POINT('ICRS', t1.ra, t1.dec), POINT('ICRS', g2.ra, g2.dec)), -0.5))
    --            <
    --        -- < 8 sigma (changed from 3 to 8)
    --        {nsigma}*sqrt(
    --            ((power((t1.pmra_error), 2) + power((g2.pmra_error), 2)) *  power((t1.pmra - g2.pmra), 2) +
    --            (power((t1.pmdec_error), 2) + power((g2.pmdec_error), 2)) * power((t1.pmdec - g2.pmdec), 2))
    --                /(power((t1.pmra - g2.pmra), 2) + power((t1.pmdec - g2.pmdec), 2)))
        AND
            -- sigma < 1.5 (noise/signal < 1.5)
            sqrt(
                ((power((t1.pmra_error), 2) + power((g2.pmra_error), 2)) * power((t1.pmra - g2.pmra), 2) +
                (power((t1.pmdec_error), 2) + power((g2.pmdec_error), 2)) * power((t1.pmdec - g2.pmdec), 2))
                    /(power((t1.pmra - g2.pmra), 2) + power((t1.pmdec - g2.pmdec), 2)))
                        < 1.5
"""
def stars_DRx(record):
    TBL_GAIA_DRx  = SQLLib.sqlInsert(iStro, "TBL_OBJECTS ");
    #print
    if record.source_id :
        TBL_GAIA_DRx .setAttributeInteger("source_id", record.source_id)
    if record.ra:
        TBL_GAIA_DRx .setAttributeFloat("ra_", record.ra)
    if record.ra_error:
        TBL_GAIA_DRx .setAttributeFloat("ra_error", record.ra_error)
    if record.dec:
        TBL_GAIA_DRx .setAttributeFloat("dec_", record.dec)
    if record.dec_error:
        TBL_GAIA_DRx .setAttributeFloat("dec_error", record.dec_error)
    if record.parallax:
        TBL_GAIA_DRx .setAttributeFloat("parallax", record.parallax)
    if record.parallax_error:
        TBL_GAIA_DRx .setAttributeFloat("parallax_error", record.parallax_error)
    if record.phot_g_mean_mag:
        TBL_GAIA_DRx .setAttributeFloat("phot_g_mean_mag", record.phot_g_mean_mag)
    if record.bp_rp and not math.isnan(record.bp_rp):
        TBL_GAIA_DRx .setAttributeFloat("bp_rp", record.bp_rp)
    if record.radial_velocity and not math.isnan(record.radial_velocity):
        TBL_GAIA_DRx .setAttributeFloat("radial_velocity", record.radial_velocity)
    if record.radial_velocity_error and not math.isnan(record.radial_velocity_error):
        TBL_GAIA_DRx .setAttributeFloat("radial_velocity_error", record.radial_velocity_error)
    if record.phot_variable_flag:
        TBL_GAIA_DRx .setAttributeFloat("phot_variable_flag", record.phot_variable_flag)
    if record.teff_val and not math.isnan(record.teff_val):
        TBL_GAIA_DRx .setAttributeFloat("teff_val", record.teff_val)
    if record.a_g_val and not math.isnan(record.a_g_val):
        TBL_GAIA_DRx .setAttributeFloat("a_g_val", record.a_g_val)
    if record.pmra:
        TBL_GAIA_DRx .setAttributeFloat("pmra", record.pmra)
    if record.pmra_error:
        TBL_GAIA_DRx .setAttributeFloat("pmra_error", record.pmra_error)
    if record.pmdec:
        TBL_GAIA_DRx .setAttributeFloat("pmdec", record.pmdec)
    if record.pmdec_error:
        TBL_GAIA_DRx .setAttributeFloat("pmdec_error", record.pmdec_error)
    global releaseOut
    TBL_GAIA_DRx .setAttributeString("release_", releaseOut)
    return TBL_GAIA_DRx .getInsertSQL()
    
def binaries(record, i ):
    TBL_BINARIES  = SQLLib.sqlInsert(iStro, "TBL_BINARIES ");
    #print(record.source_id, record.source_id2)
    TBL_BINARIES .setAttributeIntBig("SOURCE_ID_PRIMARY", record.source_id)

    TBL_BINARIES .setAttributeIntBig("SOURCE_ID_SECONDARY", record.source_id2)

    global releaseOut, catalogue
    TBL_BINARIES .setAttributeString("release_", releaseOut)
    TBL_BINARIES .setAttributeString("CATALOG", catalogue)
    TBL_BINARIES .setAttributeBool("NOT_GROUPED", True)
    if is_number(record.radial_velocity) and is_number(record.radial_velocity2):
        TBL_BINARIES .setAttributeBool("HAS_RADIAL_VELOCITY", True)
        TBL_BINARIES.setAttributeString("STATUS", "")
    else:
        TBL_BINARIES .setAttributeBool("HAS_RADIAL_VELOCITY", False)
        TBL_BINARIES.setAttributeString("STATUS", "rv=0")
    TBL_BINARIES .setAttributeFloat("SEPARATION", record.pairdistance)
    TBL_BINARIES .setAttributeInteger("HEALPIX", i)
    return TBL_BINARIES .getInsertSQL()
def is_number(s):
    
    try:
        float(s)
        return True
    except Exception:
        return False
for i in HPS:
    
    healpixA=2**35*4**(12-2)*i
    healpixB=2**35*4**(12-2)*(i+step) 

    fromHealpixClause=f"""
    -- index file: {i}
    source_id >= {healpixA} and source_id < {healpixB} and
    """
    print (i, healpixA)
    
    Gaia50000From=f"""
    FROM
    -- outer product of candidates for primary star with candidates for secondary star
    -- t1 is primary
    (select * from gaiaedr3.gaia_source
    where
        {fromHealpixClause}
        -- outside solar system and within 333 pcs
        parallax between 5 and 1000 and
        parallax_over_error > 20 and
        -- Many dim stars don't have photometric data on Gaia
        -- so deselecting on this basis introduces 'hidden' or unidentified multiple star systems.
        phot_g_mean_flux_over_error > 50 and
        phot_rp_mean_flux_over_error > 20 and
        phot_bp_mean_flux_over_error > 20)
        as t1,
    (select * from gaiaedr3.gaia_source
    where 
        {fromHealpixClause}
        bp_rp is not null and
        -- outside solar system and within 333 pcs
        parallax between 3 and 1000 and
        parallax_over_error > 5 and
        -- Many dim stars don't have photometric data on Gaia
        -- so deselecting on this basis introduces 'hidden' or unidentified multiple star systems.
        phot_g_mean_flux_over_error > 50 and
        phot_rp_mean_flux_over_error > 10 and
        phot_bp_mean_flux_over_error > 10)
        as g2
    """

    query[0]=Gaia50000Select+" "+Gaia50000From+" "+Gaia50000Where
    
    now = datetime.datetime.utcnow() # current date and time
    date_time = now.strftime("%Y%m%d_%H%M%S")
    print('start query', date_time)
    if not os.path.isdir(f'bindata/{releaseOut}'):
        os.mkdir (f'bindata/{releaseOut}')
    if not os.path.isdir(f'bindata/{releaseOut}/{catalogue}'):
        os.mkdir (f'bindata/{releaseOut}/{catalogue}')
        
    if (not forceIt) and os.path.isfile(f'bindata/{releaseIn}/{catalogue}/gaia_{releaseIn}_HP{i}'):
        data =pd.read_pickle(f'bindata/{releaseIn}/{catalogue}/gaia_{releaseIn}_HP{i}')
        print('Local copy restored')
    else:
        print(query[0])
        gaia_cnxn = da.GaiaDataAccess()
        data = gaia_cnxn.gaia_query_to_pandas(query[0])
        print(data)
        data.to_pickle(f'bindata/{releaseOut}/{catalogue}/gaia_{releaseOut}_HP{i}')
    
    now = datetime.datetime.utcnow() # current date and time
    date_time = now.strftime("%Y%m%d_%H%M%S")
    
    dataLen=len(data)
    countMe=countMe+dataLen
    print(f'Running total countMe={countMe:,}')
    if countOnly:
        continue
    print(f'delete old records for healix {i}')
    TBL_BINARIES = SQLLib.sqlDelete(iStro, "TBL_BINARIES");
    TBL_BINARIES.setWhereValueInt('HEALPIX', i)
    TBL_BINARIES.setWhereValueString('CATALOG', catalogue)
    TBL_BINARIES.setWhereValueString('RELEASE_', releaseOut)
    TBL_BINARIES.deleteRecordSet()
    print('start processing record', date_time)
    bulkSQL='execute block as begin'
    print(f'length of data = {len(data):,}')
    source_id_array=[]
    data=data.convert_dtypes()
    dataLen=len(data)
    for index, record in data.iterrows():
        count=count+1
        if [record.source_id,record.source_id2] in source_id_array:
            continue
        else:
            source_id_array.append([record.source_id,record.source_id2])
        sql=binaries(record,i)
        if index % 20:
            bulkSQL = bulkSQL + """
            """ + sql + " "
        else:
            bulkSQL = bulkSQL + """
            """ + sql + """
            end"""
            TBL_BINARIES  = SQLLib.sqlInsert(iStro, "TBL_BINARIES ")
            TBL_BINARIES .executeIAD(bulkSQL)
            
            bulkSQL='execute block as begin'
    if bulkSQL != 'execute block as begin':
        bulkSQL = bulkSQL + '  end'
        TBL_BINARIES  = SQLLib.sqlInsert(iStro, "TBL_BINARIES ")
        TBL_BINARIES .executeIAD(bulkSQL)
    bulkSQL=''
    now = datetime.datetime.utcnow() # current date and time
    date_time = now.strftime("%Y%m%d_%H%M%S")
    print('update', date_time)
    
SQL="""
SELECT 
g2.source_id as source_id2,
t1.source_id, 
distance(POINT('ICRS', t1.ra, t1.dec), POINT('ICRS', g2.ra, g2.dec)) AS pairdistance
FROM (select * from gaiaedr3.gaia_source 
	  where source_id >= 9871890383196127232 and source_id < 9907919180215091200 and 
parallax between 5 and 1000 and
parallax_over_error > 20 and
phot_g_mean_flux_over_error > 50 and
phot_rp_mean_flux_over_error > 20 and
phot_bp_mean_flux_over_error > 20) as t1,
(select * from gaiaedr3.gaia_source
where source_id >= 9871890383196127232 and source_id < 9907919180215091200 and
 bp_rp is not null and
parallax > 3 and
parallax_over_error > 5 and
phot_g_mean_flux_over_error > 50 and
phot_rp_mean_flux_over_error > 10 and
phot_bp_mean_flux_over_error > 10) as g2
WHERE 1 = contains(POINT('ICRS', g2.ra, g2.dec),
CIRCLE('ICRS', t1.ra, t1.dec,
1.4e-2*t1.parallax))
AND t1.source_id != g2.source_id
AND abs(1/t1.parallax - 1/g2.parallax) -
2*0.01745*distance(POINT('ICRS', t1.ra,
t1.dec), POINT('ICRS', g2.ra, g2.dec))/
t1.parallax < 3*sqrt(power(t1.parallax_error,
2)/power(t1.parallax, 4) + power(
g2.parallax_error, 2)/power(g2.parallax, 4))
AND sqrt(power((t1.pmra - g2.pmra), 2) +
power((t1.pmdec - g2.pmdec), 2)) -
(7.42e-3 * power(t1.parallax, 1.5) *
power(distance(POINT('ICRS', t1.ra, t1.dec),
POINT('ICRS', g2.ra, g2.dec)), -0.5)) <
3*sqrt(((power((t1.pmra_error), 2) + power(
(g2.pmra_error), 2)) * power((t1.pmra -
g2.pmra), 2) + (power((t1.pmdec_error), 2) +
power((g2.pmdec_error), 2)) * power(
(t1.pmdec - g2.pmdec), 2))/(power(
(t1.pmra - g2.pmra), 2) + power(
(t1.pmdec - g2.pmdec), 2)))
AND sqrt(((power((t1.pmra_error), 2) +
		   power((g2.pmra_error), 2)) * power(
(t1.pmra - g2.pmra), 2) + (power(
(t1.pmdec_error), 2) + power(
(g2.pmdec_error), 2)) * power((t1.pmdec -
g2.pmdec), 2))/(power((t1.pmra - g2.pmra),
2) + power((t1.pmdec - g2.pmdec), 2))) < 1.5
"""
