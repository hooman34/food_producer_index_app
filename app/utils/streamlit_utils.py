from datetime import date
import datetime
import time
from fredapi import Fred
import streamlit as st
import numpy as np
from .log import get_logger
from app.utils.fetch_data import *
from app.utils.visualization import _plot_data
from app.utils.forecasting import create_prophet_df, forecast_by_Prophet

logger = get_logger(__name__)

@st.cache
class fred_processor:
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
        """
        Call the FRED api and collect the data

        Args:
            food_code_dict(dict):

        Returns:
            None
        """

        today = date.today().strftime("%Y-%m-%d")
        food_index_data = list()

        for k,v in food_code_dict.items():
            time.sleep(1)
            logger.info("Collecting selected index: {}".format(v['food_name']))

            df = fred_fred(v['series id'], observation_start='2000-01-01', observation_end=today)
            df.rename(columns={"v":v['food_name']}, inplace=True)

            data_feature_list = [df, 'date', v['food_name']]
            food_index_data.append(data_feature_list)

        return food_index_data

    def forecast(self, food_index_data, num_periods=1):
        """
        Predict the next month's price index.
        The data point used for forecasting will start from 2015-01-01
        The selected index will not go under prediction if the training dataset has more than 30% missing values

        Args:
            food_index_data(list): list of list of data

        Returns:
            forecast_results(dict): forecast values for each food index
        """
        forecast_results = dict()

        for data, date_col, val_col in food_index_data:
            # check if the data points are enough
            # only use data after 2015-01-01
            df = data.loc[data[date_col].dt.date > datetime.date(2015, 1, 1)].copy()
            # check the % of missing values
            num_recent_data_points = df.loc[:, val_col].shape[0]
            num_missing_data_points = df.loc[:, val_col].isna().sum()
            missing_perc = num_missing_data_points / num_recent_data_points

            # start forecasting
            if  missing_perc < 0.3:
                prophet_df = create_prophet_df(df, date_col, val_col)
                forecasts = forecast_by_Prophet(prophet_df, num_periods)
                forecast_results[val_col] = forecasts['yhat'].tolist()
            # pass
            else:
                st.info("{} not available due to insufficient data points.".format(val_col))

        return forecast_results

    def forecast_report(self, food_index_data, forecast_results):
        """
        Create simple insight reports informing about the prediction

        Args:
            forecast_results:

        Returns:

        """
        # fetch last date data
        for data, date_col, food_col in food_index_data:
            if food_col in forecast_results.keys():
                # price increase
                last_index = data.loc[data[date_col] == data[date_col].max(), food_col].values[0]
                future_index = forecast_results[food_col][0]
                increase_perc = np.round(100*(future_index - last_index)/last_index, 2)

                if increase_perc>0:
                    increase_perc = "+" + str(increase_perc)
                else:
                    increase_perc = str(increase_perc)
                st.info("Price for {} is expected to change this month by {}%".format(food_col, increase_perc))


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


