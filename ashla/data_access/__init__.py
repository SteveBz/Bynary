from astroquery.gaia import GaiaClass
from ashla import utils
import ashla.data_access.config as cnf
from ashla.data_access.binary_data import BinaryStarDataFrame


class GaiaDataAccess(GaiaClass):
    """

    Proxy for the Gaia Query (TAP) class. Uses a login class for login details, and contains easier to use functions
    to get data.

    """

    def __init__(self, login_config=None):
        super(GaiaDataAccess, self).__init__()
        self.login_config = login_config
        if self.login_config is None:
            # You can type in your details
            self.login(user='scookson', password='Esa.4142135')
        else:
            login_conf_inst = cnf.GaiaLoginConf(config_file=self.login_config)
            self.login(user=login_conf_inst.user, password=login_conf_inst.password)

    def get_gaia_job(self, query, asyncronous=True, **kwargs):
        if asyncronous:
            j1 = self.launch_job_async(query, **kwargs)
        else:
            j1 = self.launch_job(query, **kwargs)
        job = j1.get_results()
        return job

    def get_old_job_data(self, jobid, return_binary_inst=True, parquet_output_name=None):
        """

        Function to grab the data from an old asyncronous TAP job. Saves the time for running the job. Great for large
        amounts of data.

        Args:
            jobid (str): Job ID.
            return_binary_inst (bool): If True, returns BinaryStarDataFrame DataFrame proxy object, otherwise table obj.
            parquet_output_name (str): Optional, default None. If set, will save a Parquet file with this name (as a
            prefix).

        Returns:
            BinaryStarDataFrame: If return_binary_inst is True or Table. Contains the table data from the job.

        """
        j1 = self.load_async_job(jobid)
        job = j1.get_results()
        dta_pd = job.to_pandas()
        if parquet_output_name is not None:
            self.data_save_parquet(dta_pd, output_file_name=parquet_output_name)
        if return_binary_inst:
            return BinaryStarDataFrame(dta_pd)
        return job

    def gaia_query_to_pandas(self, query, parquet_output_name=None, **kwargs):
        """

        Args:
            query (str): Query to send to the Gaia Archive.
            parquet_output_name (str): Optional, default None. If set, will output a Parquet file of this name prefix.

        Kwargs:
            output_file (str): optional, default None
                file name where the results are saved if dumpToFile is True.
                If this parameter is not provided, the jobid is used instead
            output_format (str): optional, default 'votable'
                results format
            verbose (bool): optional, default 'False'
                flag to display information about the process
            dump_to_file (bool): optional, default 'False'
                if True, the results are saved in a file instead of using memory
            background (bool): optional, default 'False'
                when the job is executed in asynchronous mode, this flag specifies
                whether the execution will wait until results are available
            upload_resource (str): optional, default None
                resource to be uploaded to UPLOAD_SCHEMA
            upload_table_name (str): optional, default None
                resource temporary table name associated to the uploaded resource.
                This argument is required if upload_resource is provided.
            autorun (boolean): optional, default True
                if 'True', sets 'phase' parameter to 'RUN',
                so the framework can start the job.

        Returns:

        """
        job = self.get_gaia_job(query, **kwargs)
        gaia_data = job.to_pandas()
        if parquet_output_name is not None:
            self.data_save_parquet(gaia_data, output_file_name=parquet_output_name)
        return BinaryStarDataFrame(gaia_data)

    def data_save_parquet(self, data, output_file_name):
        data.to_parquet("{0}.parquet".format(output_file_name), compression=None)

    def data_save_json(self, data, output_file_name):
        data.to_json("{0}.json".format(output_file_name), compression=None)

    def data_load_json(self, data, input_file_name):
        data =data.read_json("{0}.json".format(input_file_name), orient='table', compression=None)
        return data

    def gaia_query_save_parquet_file(self, query, output_file_name):
        gaia_data = query_gaia_to_pandas(query)
        self.data_save_parquet(gaia_data, output_file_name)

    def gaia_get_dr2_initial_data(self, save_to_parquet=False, **kwargs):
        """

        Function to run a query showing the first wide binary pair in the paper.

        Args:
            save_to_parquet (bool): Save results to Parquet format.

        Kwargs:
            output_file (str): optional, default None
                file name where the results are saved if dumpToFile is True.
                If this parameter is not provided, the jobid is used instead
            output_format (str): optional, default 'votable'
                results format
            verbose (bool): optional, default 'False'
                flag to display information about the process
            dump_to_file (bool): optional, default 'False'
                if True, the results are saved in a file instead of using memory
            background (bool): optional, default 'False'
                when the job is executed in asynchronous mode, this flag specifies
                whether the execution will wait until results are available
            upload_resource (str): optional, default None
                resource to be uploaded to UPLOAD_SCHEMA
            upload_table_name (str): optional, default None
                resource temporary table name associated to the uploaded resource.
                This argument is required if upload_resource is provided.
            autorun (boolean): optional, default True
                if 'True', sets 'phase' parameter to 'RUN',
                so the framework can start the job.

        Returns:
            Pandas.DataFrame: Output of the query.

        """
        query = r"""SELECT TOP 500 gaia_source.source_id,gaia_source.ra,gaia_source.ra_error,gaia_source.dec,
                        gaia_source.dec_error,gaia_source.parallax,gaia_source.parallax_error,gaia_source.phot_g_mean_mag,
                        gaia_source.bp_rp,gaia_source.radial_velocity,gaia_source.radial_velocity_error,
                        gaia_source.phot_variable_flag,gaia_source.teff_val,gaia_source.a_g_val, 
                        gaia_source.pmra as proper_motion_ra, gaia_source.pmra_error as proper_motion_ra_error, 
                        gaia_source.pmdec as proper_motion_dec, gaia_source.pmdec_error as proper_motion_dec_error
                    FROM gaiadr2.gaia_source 
                    WHERE (gaiadr2.gaia_source.source_id=4722135642226356736 OR 
                        gaiadr2.gaia_source.source_id=4722111590409480064)"""

        output_df = self.gaia_query_to_pandas(query, **kwargs)
        if save_to_parquet:
            self.data_save_parquet(output_df, "initial_dr2_data")
        return output_df

    def gaia_get_pairs_of_close_stars(self, save_to_parquet=False, **kwargs):
        query = r"""SELECT * FROM (
SELECT g1.source_id as id1, g1.ra as ra1, g1.ra_error as ra1_err, g1.dec_error as dec1_err, g1.dec as dec1, 1000.0 / g1.parallax as d1, (g1.parallax_error / g1.parallax)*(1000.0 / g1.parallax) as d1_err, g1.parallax_error as plx1_err,
	g1.pmra as pmra1, g1.pmdec as pmdec1, g1.pmra_error as pmra1_err, g1.pmdec_error as pmdec1_err, g2.parallax_error as plx2_err, g1.dr2_radial_velocity as rad_vel1, g1.dr2_radial_velocity_error as rad_vel1_err, 
	g2.source_id as id2, g2.ra as ra2, g2.dec as dec2, g2.ra_error as ra2_err, g2.dec_error as dec2_err, 1000.0 / g2.parallax as d2,  (g2.parallax_error / g2.parallax)*(1000.0 / g2.parallax) as d2_err, 
	g2.pmra as pmra2, g2.pmdec as pmdec2, g2.pmra_error as pmra2_err, g2.pmdec_error as pmdec2_err,g2.dr2_radial_velocity as rad_vel2, g2.dr2_radial_velocity_error as rad_vel2_err,
	
	-- Distance between stars
  sqrt(ABS(power((1000.0 / g1.parallax + 1000.0 / g2.parallax), 2) * (1 - (sin(g1.dec * 2*pi()/360.0) * sin(g2.dec * 2*pi()/360.0) + (cos(g1.dec * 2*pi()/360.0) * cos(g2.dec * 2*pi()/360.0) * cos((g1.ra * 2*pi()/360.0) - (g2.ra * 2*pi()/360.0))))) / 2)) as dist
FROM gaiaedr3.gaia_source as g1, gaiaedr3.gaia_source as g2 
	-- avoids duplicates
	where g1.source_id < g2.source_id and
	g1.parallax is not null and g2.parallax is not null and g1.parallax_over_error > 5 and g2.parallax_over_error > 5 
	and g1.pmdec is not null and g1.pmra is not null and g1.dr2_radial_velocity is not null 
	and g2.pmra is not null and g2.pmdec is not null and g2.dr2_radial_velocity is not null
	-- only pick combinations of stars in plane of sight in sky so we use proper motions ( parallax's around the same, giving a 20% breathing space for errors)
	and ABS(g1.parallax - g2.parallax) <= SQRT(power(g1.parallax_error, 2) + power(g2.parallax_error,2))*1.2
  --and (g1.source_id=4722135642226356736 and g2.source_id=4722111590409480064) or (g2.source_id=4722135642226356736 and g1.source_id=4722111590409480064) 
	) main 

where main.dist <= 1.0
"""
        output_df = self.gaia_query_to_pandas(query, **kwargs)
        if save_to_parquet:
            self.data_save_parquet(output_df, "gaia_close_star_pairs")
        return output_df

    def gaia_get_hipp_binaries(self, save_to_parquet=False, only_show_stars_with_both_stars_in_data=True, **kwargs):
        """

        Function to run a query which joins Gaia DR2 and Hipparcos, and filters to stars known to be in a binary system.
            Additionally, there is a filter to only show stars where at least 2 stars in the binary system exists in
            both Hipparcos and Gaia DR2.

        Args:
            save_to_parquet (bool): Save results to Parquet format.
            only_show_stars_with_both_stars_in_data (bool): Only show stars where at least 2 stars in the binary system exists in
                both Hipparcos and Gaia DR2.

        Kwargs:
            output_file (str): optional, default None
                file name where the results are saved if dumpToFile is True.
                If this parameter is not provided, the jobid is used instead
            output_format (str): optional, default 'votable'
                results format
            verbose (bool): optional, default 'False'
                flag to display information about the process
            dump_to_file (bool): optional, default 'False'
                if True, the results are saved in a file instead of using memory
            background (bool): optional, default 'False'
                when the job is executed in asynchronous mode, this flag specifies
                whether the execution will wait until results are available
            upload_resource (str): optional, default None
                resource to be uploaded to UPLOAD_SCHEMA
            upload_table_name (str): optional, default None
                resource temporary table name associated to the uploaded resource.
                This argument is required if upload_resource is provided.
            autorun (boolean): optional, default True
                if 'True', sets 'phase' parameter to 'RUN',
                so the framework can start the job.

        Returns:
            Pandas.DataFrame: Output of the query.

        """
        filter_missing_data = " HAVING count(*) > 1 " if only_show_stars_with_both_stars_in_data else ""
        where_clause = " WHERE ABS(hipp2.plx - gaia2.parallax) <= (hipp2.e_plx + gaia2.parallax_error) and gaia2.parallax_over_error > 5" if only_show_stars_with_both_stars_in_data else ""
        query = r"""SELECT gaia_source.source_id,gaia_source.ra,gaia_source.ra_error,gaia_source.dec,
                        gaia_source.dec_error,gaia_source.parallax,gaia_source.parallax_error,hipp2.plx as hipp_parallax, hipp2.e_plx as hipp_error_parallax,
                        gaia_source.phot_g_mean_mag,gaia_source.parallax_over_error,
                        gaia_source.bp_rp,gaia_source.radial_velocity,gaia_source.radial_velocity_error,
                        gaia_source.phot_variable_flag,gaia_source.teff_val,gaia_source.a_g_val, 
                        gaia_source.pmra as proper_motion_ra, gaia_source.pmra_error as proper_motion_ra_error, 
                        gaia_source.pmdec as proper_motion_dec, gaia_source.pmdec_error as proper_motion_dec_error,
						hipp.ccdm, hipp.n_ccdm AS CCDM_History, 
						hipparcos2_best_neighbour.angular_distance AS angular_distance_between_hipp_gaia,
						num_binary.num_ccdm AS num_stars_in_binary_w_data_available

                    FROM gaiadr2.gaia_source
                        LEFT JOIN gaiadr2.hipparcos2_best_neighbour 
                            ON gaia_source.source_id = hipparcos2_best_neighbour.source_id
                            LEFT JOIN public.hipparcos_newreduction AS hipp2 
                                ON hipp2.hip = hipparcos2_best_neighbour.original_ext_source_id
                                LEFT JOIN public.hipparcos AS hipp ON hipp2.hip = hipp.hip
                                    INNER JOIN (SELECT hipp.ccdm, count(*) AS num_ccdm 
                                                    FROM public.hipparcos AS hipp 
                                                        INNER JOIN public.hipparcos_newreduction AS hipp2 on hipp.hip = hipp2.hip
                                                            INNER JOIN gaiadr2.hipparcos2_best_neighbour 
                                                                    ON hipp2.hip = hipparcos2_best_neighbour.original_ext_source_id
                                                                INNER JOIN gaiadr2.gaia_source AS gaia2 
                                                                    on hipparcos2_best_neighbour.source_id = gaia2.source_id 
                                                    {0} 
                                                    GROUP BY hipp.ccdm {1}
                                               ) AS num_binary ON num_binary.ccdm = hipp.ccdm
    
                                WHERE hipp.ccdm is not null and
                                hipp.nsys >=2 and
                                -- hipp.ncomp =1 and 
                                hipparcos2_best_neighbour.gaia_astrometric_params=5 
                                and ABS(hipp2.plx - gaia_source.parallax) <= (hipp2.e_plx + gaia_source.parallax_error)
                                and gaia_source.parallax_over_error > 5 
    
                                ORDER BY hipp.ccdm asc""".format(where_clause, filter_missing_data)
        output_df = self.gaia_query_to_pandas(query, **kwargs)
        if save_to_parquet:
            self.data_save_parquet(output_df, "hipp_binaries")
        return output_df


def query_random_selection(num_results):
    top_line = "TOP {0}".format(num_results) if num_results is not None else ""
    query = r"""SELECT {0} gaia_source.source_id,gaia_source.ra,gaia_source.dec,gaia_source.parallax,
            gaia_source.parallax_error,gaia_source.parallax_over_error,gaia_source.phot_g_mean_mag,
            gaia_source.phot_g_mean_flux, gaia_source.bp_rp,gaia_source.dr2_radial_velocity,
            gaia_source.dr2_radial_velocity_error, gaia_source.pseudocolour, gaia_source.dr2_rv_template_teff, 
            pmra, pmdec, l, b, ecl_lon, ecl_lat, bp_g
        FROM gaiaedr3.gaia_source 
        where gaia_source.dr2_radial_velocity is not null 
        and gaia_source.parallax is not null 
        and gaia_source.phot_g_mean_mag is not null 
        --and gaia_source.bp_rp is not null 
        and gaia_source.phot_g_mean_flux is not null 
        and gaia_source.dr2_rv_template_teff is not null 
        --and gaia_source.pseudocolour is not null 
        --and pmra is not null and pmdec is not null 0
        --and l is not null and b is not null 
        --and ecl_lon is not null and ecl_lat is not null 
        and bp_g is not null and
        gaia_source.parallax_over_error > 30 and gaia_source.dr2_radial_velocity_error < 10 order by gaia_source.random_index asc""".format(
        top_line)
    return query


def run_gaia_query(query, login_config=None):
    gaia_cls = GaiaDataAccess(login_config=login_config)
    job = gaia_cls.get_gaia_job(query)
    return job


def query_gaia_to_pandas(query, login_cnf=None):
    job = run_gaia_query(query, login_cnf)
    gaia_data = job.to_pandas()
    return gaia_data


def gaia_query_to_parquet(query, output_file_name, login_cnf=None):
    gaia_data = query_gaia_to_pandas(query, login_cnf=login_cnf)
    gaia_data.to_parquet("{0}.parquet.gzip".format(output_file_name), compression='gzip')
