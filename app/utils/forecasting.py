from .log import get_logger
from prophet import Prophet
import pandas as pd

logger = get_logger(__name__)


def create_prophet_df(data, date_col, val_col):

    logger.info("Creating timeseries data for {}".format(val_col))

    df = data.copy()

    df.rename(columns={date_col: "ds", val_col: "y"}, inplace=True)
    df.loc[:, 'ds'] = pd.to_datetime(df['ds'])
    df = df.loc[:, ['ds', 'y']]

    # Spline imputation
    df['y'] = df['y'].interpolate(option='spline')

    return df

def forecast_by_Prophet(train, num_periods=1):

    logger.info("Forecasting the next {} periods".format(num_periods))

    m = Prophet()
    m.fit(train)

    future = m.make_future_dataframe(periods=num_periods)
    forecast = m.predict(future)
    forecast= forecast[['ds', 'yhat']]
    forecast= forecast[-num_periods:]
    return forecast


