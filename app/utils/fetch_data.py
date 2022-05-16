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



#
# def _plot_two_data(plot_type1, data1, x1, y1, plot_type2, data2, x2, y2):
#     trace1 = _create_trace(plot_typd1, data1, x1, y1)
#     trace2 = _create_trace(plot_typd2, data2, x2, y2)
#
#     fig = make_subplots(specs=[[{"secondary_y": True}]])
#     fig.add_trace(trace1)
#     fig.add_trace(trace2, secondary_y=True)
#
#     fig.update_layout(legend=dict(
#         orientation="h",
#         yanchor="bottom",
#         y=1.02,
#         xanchor="right",
#         x=1
#     ))
#
#     return fig
#
#
# def _create_trace(plot_type, data, x, y):
#     """
#     create trace
#     """
#     if plot_type == 'bar':
#         trace = go.Bar(x=data[x],
#                        y=data[y],
#                        name=y)
#     if plot_type == 'line':
#         trace = go.Scatter(x=data[x],
#                            y=data[y],
#                            name=y)
#     return trace
