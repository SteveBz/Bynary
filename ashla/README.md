# ASHLA #

Package to deal with Wide Binary stuff.

# Installation #

Firstly, clone the repository onto your local machine. Say the clone lives in
 C:/git/ashla
 
    cd C:/git/ashla
    pip install .
Or, if you would like to edit the code, or have the package automatically update on a pull 
of the git repo, use:

    pip install -e .

# Usage #

#### ashla.data_access (Gaia Access)

This sub-package provides tools for accessing the Gaia database.


For logging in, you can use the ESA login and password. Either don't supply a GaiaLoginConf object and you will be promted to enter 
a login and password in the terminal. Else make a copy of the ashla/data_access/login_config.ini 
file, and enter username and password there. Then add a link to this config file as the 
login_conf variable. 

For example:

> We make a copy of login_conf.ini in C:\configs, containing:

    [login]
    user = my_username
    password = my_password
    
This is all the inputs we need. 

We can then create a Gaia Connection object using the file path of this config. 
This will allow you to run Gaia Queries.

    gaia_cnxn = da.GaiaDataAccess(r'C:\configs\login_config.ini')
    
You can use this connection object to run a query and get a pandas DataFrame output.
    
    data = gaia_cnxn.query_gaia_to_pandas(query)

The data will now be in a Pandas DataFrame format. You can additionally query
and save as a Parquet file named gaia_data.parquet.gzip using the parquet_output_name option:

    data = gaia_cnxn.query_gaia_to_pandas(query, parquet_output_name='gaia_data')
    
You can additionally pass any arguments which get passed to the Astroquery Gaia launch_job_async or launch_job 
function. For example, you can get an output Votable table using:

    data = gaia_cnxn.query_gaia_to_pandas(query, dump_to_file=True, output_format='votable')

You can additionally use output_format= ‘votable_plain’, ‘fits’, ‘csv’ or ‘json

The package additionally contains some build in queries for certain tasks. For example:

    data = gaia_cnxn.gaia_get_hipp_binaries(dump_to_file=True, output_format='csv')

This will give you information about stars known to be binary pairs, which are in both Gaia and Hipparcos catalogues.