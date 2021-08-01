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

selectFrom = """SELECT
    distinct gaia_source.source_id,
    gaia_source.ra,
    gaia_source.ra_error,
    gaia_source.dec,
    gaia_source.dec_error,
    gaia_source.parallax,
    gaia_source.parallax_error,
    gaia_source.phot_g_mean_mag,
    gaia_source.bp_rp,
    gaia_source.dr2_radial_velocity,
    gaia_source.dr2_radial_velocity_error,
    --gaia_source.phot_variable_flag,
    --gaia_source.teff_val,
    --gaia_source.a_g_val, 
    gaia_source.pmra,
    gaia_source.pmra_error, 
    gaia_source.pmdec,
    gaia_source.ruwe,
    gaia_source.pmdec_error

    FROM gaiaedr3.gaia_source
"""

count=0
step = 1
lowerRA=70
upperRA=360
forceIt=False
release='bDR3'
TotalCount=0
countOnly=1

TBL_GAIA_eDR3  = SQLLib.sql(iStro, "TBL_objects ")
#ALTER INDEX IDX_TBL_OBJECTS1 INACTIVE
#ALTER INDEX IDX_TBL_OBJECTS2 INACTIVE
#ALTER INDEX IDX_TBL_OBJECTS3 INACTIVE
#ALTER INDEX IDX_TBL_OBJECTS4 INACTIVE
bulkSQL="ALTER INDEX IDX_TBL_OBJECTS1 INACTIVE ;"
TBL_GAIA_eDR3 .executeIAD(bulkSQL)
bulkSQL = "ALTER INDEX IDX_TBL_OBJECTS2 INACTIVE ;"
TBL_GAIA_eDR3 .executeIAD(bulkSQL)
bulkSQL = "ALTER INDEX IDX_TBL_OBJECTS3 INACTIVE ;"
TBL_GAIA_eDR3 .executeIAD(bulkSQL)
bulkSQL = "ALTER INDEX IDX_TBL_OBJECTS4 INACTIVE ;"
TBL_GAIA_eDR3 .executeIAD(bulkSQL)
for i in range(lowerRA, upperRA, step):
    query[0] = selectFrom + f"""
    -- RA {i} to {i+step}
    WHERE gaia_source.ra >= {i} and gaia_source.ra < {i+step}
    --    source_id in (3242763706493692544, 3242763706493692288)
        and parallax >= 3.0
        and parallax < 1000
        and parallax_over_error > 5
        and phot_g_mean_flux_over_error > 50
        and phot_rp_mean_flux_over_error > 10
        and phot_bp_mean_flux_over_error > 10
    """
    
    #print( query[0] )
    print (f'i = {i}')
    now = datetime.datetime.utcnow() # current date and time
    date_time = now.strftime("%Y%m%d_%H%M%S")
    #filePrefix='iEquals0' + date_time
    print('start query', date_time)
    # output_data = gaia_cnxn.gaia_get_pairs_of_close_stars(save_to_pickle=True, dump_to_file=True, output_format='json')
    
    if not os.path.isdir(f'bindata/{release}'):
        os.mkdir (f'bindata/{release}')
    if not os.path.isdir(f'bindata/{release}/stars'):
        os.mkdir (f'bindata/{release}/stars')
        
    if (not forceIt) and os.path.isfile(f'bindata/{release}/stars/gaia_{release}_RA{i}'):
        data =pd.read_pickle(f'bindata/{release}/stars/gaia_{release}_RA{i}')
        print(f'Restore from local pickle file')
    else:
        gaia_cnxn = da.GaiaDataAccess()
        data = gaia_cnxn.gaia_query_to_pandas(query[0])
        print(f'Download from Gaia')
        data.to_pickle(f'bindata/{release}/stars/gaia_{release}_RA{i}')
        
    #gaia_cnxn = da.GaiaDataAccess()
    #data = gaia_cnxn.gaia_query_to_pandas(query[0])
    #data.set_option('display.max_colwidth', None)
    
    if countOnly:
        continue
    print(f'delete old records for RA {i} to {i+1} degrees')
    TBL_OBJECTS = SQLLib.sqlDelete(iStro, "TBL_OBJECTS")
    TBL_OBJECTS.setWhereValueLTFloat('RA_', i+1)
    TBL_OBJECTS.setWhereValueGEFloat('RA_', i)
    TBL_OBJECTS.setWhereValueString('RELEASE_', release)
    TBL_OBJECTS.deleteRecordSet()
    now = datetime.datetime.utcnow() # current date and time
    date_time = now.strftime("%Y%m%d_%H%M%S")
    #filePrefix='iEquals0' + date_time
    print(f'start processing {len(data)} records at {date_time}.' )
    bulkSQL='execute block as begin'
    source_id_array=[]
    data2=data.to_dict()
    #print(data)
    TotalCount=TotalCount+len(data)
    print(f'Number of stars: {len(data)} in {TotalCount}')
    
    #for record in data2:  #.iterrows():
    #for record in data2:  #.iterrows():
    for index in range(len(data)):
        count=count+1
        #if record.source_id in source_id_array:
        #    continue
        #else:
        #    source_id_array.append(int(record.source_id))
        #print('record = ', record)
        TBL_GAIA_eDR3  = SQLLib.sqlInsert(iStro, "TBL_objects ")
        #print(index)
        #print(data2['source_id'][index])
        TBL_GAIA_eDR3 .setAttributeInteger("source_id", data2['source_id'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("ra_", data2['ra'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("ra_error", data2['ra_error'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("dec_", data2['dec'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("dec_error", data2['dec_error'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("parallax", data2['parallax'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("parallax_error", data2['parallax_error'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("phot_g_mean_mag", data2['phot_g_mean_mag'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("bp_rp", data2['bp_rp'][index])
        if data2['dr2_radial_velocity'][index] and not math.isnan(data2['dr2_radial_velocity'][index]):
            TBL_GAIA_eDR3 .setAttributeFloat("radial_velocity", data2['dr2_radial_velocity'][index])
        if data2['dr2_radial_velocity_error'][index] and not math.isnan(data2['dr2_radial_velocity_error'][index]):
            TBL_GAIA_eDR3 .setAttributeFloat("radial_velocity_error", data2['dr2_radial_velocity_error'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("pmra", data2['pmra'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("pmra_error", data2['pmra_error'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("pmdec", data2['pmdec'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("pmdec_error", data2['pmdec_error'][index])
        TBL_GAIA_eDR3 .setAttributeFloat("ruwe", data2['ruwe'][index])
        TBL_GAIA_eDR3 .setAttributeString("release_", release)
        #print (count)
        #print (count % 20)
        if index % 20:
            bulkSQL = bulkSQL + """
            """ + TBL_GAIA_eDR3 .getInsertSQL() + " "
        else:
            bulkSQL = bulkSQL + """
            """ + TBL_GAIA_eDR3 .getInsertSQL() + """
            end"""
            #now = datetime.datetime.utcnow() # current date and time
            #date_time = now.strftime("%Y%m%d_%H%M%S")
            #print("1) SQL = ", bulkSQL)
            TBL_GAIA_eDR3 .executeIAD(bulkSQL)
            
            print (count)
            TBL_GAIA_eDR3  = SQLLib.sqlInsert(iStro, "TBL_objects ")
            bulkSQL='execute block as begin'
    
    if bulkSQL != 'execute block as begin':
        bulkSQL = bulkSQL + '  end'
        #print("2) SQL = ", bulkSQL)
        TBL_GAIA_eDR3 .executeIAD(bulkSQL)
    bulkSQL=''
    now = datetime.datetime.utcnow() # current date and time
    date_time = now.strftime("%Y%m%d_%H%M%S")
    #print("RA_ = ", data2['ra'][index], index, 'update', date_time)
    
TBL_GAIA_eDR3  = SQLLib.sql(iStro, "TBL_objects ")
#ALTER INDEX IDX_TBL_OBJECTS1 ACTIVE
#ALTER INDEX IDX_TBL_OBJECTS2 ACTIVE
#ALTER INDEX IDX_TBL_OBJECTS3 ACTIVE
#ALTER INDEX IDX_TBL_OBJECTS4 ACTIVE
bulkSQL="ALTER INDEX IDX_TBL_OBJECTS1 ACTIVE ;"
TBL_GAIA_eDR3 .executeIAD(bulkSQL)
bulkSQL = "ALTER INDEX IDX_TBL_OBJECTS2 ACTIVE ;"
TBL_GAIA_eDR3 .executeIAD(bulkSQL)
bulkSQL = "ALTER INDEX IDX_TBL_OBJECTS3 ACTIVE ;"
TBL_GAIA_eDR3 .executeIAD(bulkSQL)
bulkSQL = "ALTER INDEX IDX_TBL_OBJECTS4 ACTIVE ;"
TBL_GAIA_eDR3 .executeIAD(bulkSQL)
#now = datetime.datetime.utcnow() # current date and time
#date_time = now.strftime("%Y%m%d_%H%M%S")
#filePrefix=f'iEquals{i}Deg' + date_time
#print(filePrefix)
#gaia_cnxn.data_save_json(data, filePrefix)