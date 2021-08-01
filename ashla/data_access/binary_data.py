import pandas as pd
import dask
import dask.dataframe as dd
from ashla import utils
import os


class BinaryStarDataFrame(pd.DataFrame):
    """

    Proxy of a Pandas DataFrame class, with added functionality for Wide Binary Star searching.

    """

    def __init__(self, data):
        if isinstance(data, pd.DataFrame):
            if 'parallax' in data.columns and 'dist_pc' not in data.columns:
                data['dist_pc'] = 1000.0 / data['parallax']
                if 'parallax_error' in data.columns and 'dist_err_pc' not in data.columns:
                    data['dist_err_pc'] = (data['parallax_error'] / data['parallax']) * data['dist_pc']

            super().__init__(data)
            self.drop_duplicates()
        else:
            raise TypeError("You did not pass a DataFrame! Boooooo!")

    def to_df(self):
        """

        Function to convert back to Pandas DataFrame.

        Returns:
            pd.DataFrame: our instance as a DataFrame.

        """
        return pd.DataFrame(self)

    def add_cartesian_coords_cols(self):
        self['cart_x'], self['cart_y'], self['cart_z'] = utils.ra_dec_dist_to_cartesian(self['ra'],
                                                                                        self['dec'],
                                                                                        self['dist_pc'])
        return self

    def add_plotting_data_cols(self):

        self['rgb_colour'] = "rgb" + self['bp_g'].apply(utils.bv2rgb).astype(str)
        self['dot_size'] = utils.dot_size_from_mag(self['phot_g_mean_mag'])
        return self

    def add_binary_sys_id_column(self, column_name=None, ignore_hipp_col=False):
        """

        if column_name is not None, this column overrides any hipparcos data or data from the paper.
            Otherwise, if the Hipparcos CCDM column exists (and ignore_hipp_col is False), it uses the
            Hipparcos CCDM column only.

        Args:
            column_name:

        Returns:8

        """
        # Uses custom binary ID column
        if column_name is not None:
            self.rename(columns={column_name: 'binary_id'})
        # Uses the Hipparcos CCDM (binary ID) column
        elif not ignore_hipp_col and 'ccdm' in self.columns:
            self.rename(columns={'ccdm': 'binary_id'})
        else:
            current_dir = os.path.dirname(os.path.realpath(__file__))
            known_binaries = pd.read_json(r'{0}\known_binaries.json'.format(current_dir), usecols=['binary_id', 'GDR2'])
            known_binaries['binary_id'] = known_binaries['binary_id'].astype(dtype=int)
            self = BinaryStarDataFrame(
                self.merge(right=known_binaries, how='left', left_on='source_id', right_on='GDR2'))
        return self


class BinarySystemDataFrame(BinaryStarDataFrame):
    """

    Proxy of a Pandas DataFrame class, with added functionality for Wide Binary Star searching.

    Warning:
        This is not yet working properly. Just a test / play.

    """

    def __init__(self, data, known_binaries=True):
        super().__init__(data)
        if known_binaries:
            if 'binary_id' not in self.columns:
                self = self.add_binary_sys_id_column(ignore_hipp_col=True)

            def reset_index_prox(df):
                return df.reset_index(drop=True)

            self = self.loc[self['binary_id'].notnull()]
            self = self.groupby(by='binary_id').apply(reset_index_prox)
            # maybe do a multi index for binary id and source id? Then play with stack unstack?

            self.pivot(index='binary_id', columns='pivot_col')

    def to_df(self):
        """

        Function to convert back to Pandas DataFrame.

        Returns:
            pd.DataFrame: our instance as a DataFrame.

        """
        return pd.DataFrame(self)


if __name__ == '__main__':
    import ashla.data_access as da

    gaia_cnxn = da.GaiaDataAccess(r'C:\Users\zacha\Documents\ashla\ashla\data_access\login_conf_zplummer.ini')
    output_data = gaia_cnxn.gaia_get_hipp_binaries(save_to_parquet=False, only_show_stars_with_both_stars_in_data=True)
    # output_data = gaia_cnxn.load_async_job('1616446549863O')
    # data_bin = BinaryData(output_data)
    output_binarysys = BinarySystemDataFrame(output_data)
    print(output_data)
