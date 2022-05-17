from datetime import date
import datetime
import time
from app.utils.fetch_data import *
from fredapi import Fred
import streamlit as st
from .log import get_logger
from app.utils.visualization import _plot_data

logger = get_logger(__name__)

@st.cache
class fred:
    def __init__(self):
        self.fred = self._fred_auth()
        self.food_options = self.collect_food_options()

    def _fred_auth(self):
        logger.info("Authenticating to FRED api ...")
        fred = Fred(api_key=st.secrets["fred"]["key"])
        return fred

    def collect_food_options(self):
        """
        Collect options of indexes
        """
        logger.info("Collecting food options ...")

        # search for products
        options = self.fred.search('Producer Price Index by Commodity: Farm Products').reset_index()
        options['food_name'] = options['title'].str.split(": ").str[-1]
        options['observation_start_year'] = options['observation_start'].dt.year
        options['word_length'] = options['food_name'].str.split(" ").str.len()
        # filter out unwanted indexes:
        options = options.loc[~options['food_name'].str.contains('DISCONTINUED')]
        options = options.loc[options['word_length']<=2]
        options = options.loc[options['frequency_short']=='M']
        options = options.loc[options['seasonal_adjustment_short']=='NSA']
        # filter on data start year. choose oldest index if same food name
        latest = options.groupby('food_name').agg({"observation_start_year": "min"}).reset_index()
        latest = latest.merge(options, on=['food_name', 'observation_start_year'], how='left')
        # filter on popularity for same food names
        popular = latest.groupby('food_name').agg({"popularity": "max"}).reset_index()
        popular = popular.merge(latest, on=['food_name', 'popularity'], how='left')
        # drop if there are still duplicates
        final = popular.drop_duplicates(subset=['food_name'])

        return final

    def retrieve_code_from_food_name(self, food_list):
        food_code_dict = self.food_options.loc[self.food_options['food_name'].isin(food_list), ['food_name', 'series id']].T.to_dict()
        return food_code_dict

    def collect_food_index(self, food_code_dict):

        today = date.today().strftime("%Y-%m-%d")
        food_index_data = list()

        for k,v in food_code_dict.items():
            time.sleep(1)
            df = fred_fred(v['series id'], observation_start='2000-01-01', observation_end=today)
            df.rename(columns={"v":v['food_name']}, inplace=True)

            # check the % of missing values
            num_recent_data_points = df.loc[df['date'].dt.date > datetime.date(2015, 1, 1), v['food_name']].shape[0]
            num_missing_data_points = df.loc[df['date'].dt.date > datetime.date(2015, 1, 1), v['food_name']].isna().sum()
            missing_perc = num_missing_data_points / num_recent_data_points

            if  missing_perc < 0.3:
                data_feature_list = [df, 'date', v['food_name']]
                food_index_data.append(data_feature_list)
            else:
                st.info("{} not available due to insufficient data points.".format(v['food_name']))

        return food_index_data


def create_plots(food_code_list):
    """
    Create plot based on user input.

    Args:
        plot_type:
        plot_settings:

    Returns:

    """
    fig = _plot_data('line', food_code_list)

    return fig


