from app.utils.fetch_data import *
from fredapi import Fred
import streamlit as st
from .log import get_logger

logger = get_logger(__name__)

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
        # filter out unwanted indexes
        options = options.loc[~options['food_name'].str.contains('DISCONTINUED')]
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