# For data manipulation
import pandas as pd
from fredapi import Fred
import json
from pathlib import Path
import requests
import streamlit as st
from .log import get_logger

# auth
basepath = Path(__file__).parent.parent

logger = get_logger(__name__)

# with open(str(basepath) + '/keys/keys.json', 'r') as key_file:
#     keys = json.load(key_file)

fred = Fred(api_key=st.secrets["fred"]["key"])

def convert_date_format(d, format):
    """"
    input format for date should be 'YYYY-MM-DD'
    format: fred, DMY
    """
    y, m, d = d.split('-')

    if format == 'Fred':
        return m + '/' + d + '/' + y
    elif format == 'YMD':
        return y + '-' + m + '-' + d
    elif format == 'DMY':
        return d + '/' + m + '/' + y


def fred_fred(code, observation_start=None, observation_end=None):
    """
    date: yyyy-mm--dd
    """
    logger.info("Fetching data from fred: {}, from {} to {}.".format(code, observation_start, observation_end))

    observation_start = convert_date_format(observation_start, 'Fred')
    observation_end = convert_date_format(observation_end, 'Fred')

    df = fred.get_series(code, observation_start=observation_start, observation_end=observation_end)
    df = pd.DataFrame(df).reset_index()
    df.columns = ['date', 'v']
    df.loc[:, 'code'] = code

    df.loc[:, 'p_key'] = df['date'].astype(str).str.replace("-", "_") + "_" + df['code']
    return df

