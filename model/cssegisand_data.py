from functools import partial
from typing import Dict, List

import numpy as np
import pandas as pd

from .utils import country_map


def _get_daily_increase(df: pd.DataFrame, num_days: int = 1) -> pd.DataFrame:
    """Get the smoothed day-over-day increase."""
    return (df - df.shift(num_days, axis=1)) / num_days


def _get_growth_factor(df: pd.DataFrame, period: int = 1) -> pd.DataFrame:
    """Get the smoothed exponential growth factor"""
    daily_increase_df = df / df.shift(period, axis=1)
    daily_increase_df = daily_increase_df.fillna(1).replace(np.inf, 1)
    return daily_increase_df.rolling(period).mean()


def _random_index_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    # match country names of two dataframes, drop anything not in the intersection
    df["Country"] = df["Country/Region"].apply(lambda x: country_map.get(x, x))
    df = df.drop("Country/Region", axis=1)
    return df


def _get_time_series_data(data_source: str) -> Dict[str, pd.DataFrame]:
    """Given a URL pointing to a Covid-19 data source from Johns Hopkins University,
    return a processed pd.DataFrame of time series data, indexed by country."""
    df_master = pd.read_csv(data_source)

    # group time series data on country
    df_groupby_country = df_master.groupby("Country/Region").sum().reset_index()
    df_groupby_country = _random_index_cleanup(df_groupby_country)

    df_groupby_country.index = df_groupby_country["Country"]
    df_cumulative = df_groupby_country.drop(["Country", "Lat", "Long"], axis=1)
    df_cumulative.loc["World"] = df_cumulative.sum()

    df_daily_increase = _get_daily_increase(df_cumulative, 7)
    df_growth_factor = _get_growth_factor(df_daily_increase, 7)

    return {
        "cumulative": df_cumulative,
        "daily_increase": df_daily_increase,
        "growth": df_growth_factor,
    }


corona_country_data = {
    k: _get_time_series_data(v)
    for k, v in {
        "confirmed": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
        "deaths": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
        "recovered": "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv",
        # 'tested': None  # todo
    }.items()
}

corona_country_data["case_fatality"] = {}
corona_country_data["active_cases"] = {}
for _type in ["cumulative", "daily_increase", "growth"]:
    confirmed = corona_country_data["confirmed"][_type]
    deaths = corona_country_data["deaths"][_type]
    recovered = corona_country_data["recovered"][_type]
    corona_country_data["case_fatality"][_type] = deaths / confirmed * 100
    # corona_country_data["active_cases"][_type] = confirmed - (deaths + recovered)


def get_doubling_time_ts_df(
    countries: List[str], line_graph_view: str, data_source: str
) -> pd.DataFrame:
    """Logic to filter data for "Development since 100 cases" category, where day of 100 cases becomes day 0.
    For each row, shift daily data left for values greater than 100, and remove if less than 100.

    Args:
        countries: list of countries to filter data
        line_graph_view: filtering and viewing type of data
        data_source: source of raw data

    Returns:
         filtered dataframe
    """

    thresh = int(line_graph_view.split("_")[1])  # 10 or 100
    df = corona_country_data[data_source]["cumulative"].copy()

    for index, row in df.iterrows():
        days_greater_thresh = np.argmax(row > thresh)
        if days_greater_thresh == 0 and not df.loc[index][0] > thresh:
            # drop indices where no data exceeds the threshold
            df = df.drop(index, axis=0)
        else:
            # shift the values where > thresh to the left
            df.loc[index] = df.loc[index].shift(-days_greater_thresh)
    df.columns = list(range(len(df.columns)))

    def _double(t, doubling_time_days):
        """Return data for pure doubling time in "n" days"""
        return thresh * 2 ** (t / doubling_time_days)

    available_countries = set(countries).intersection(set(df.index))
    max_val = df.loc[available_countries].max().max()
    for d in [1, 2, 3, 7, 14]:
        double_arr = list(map(partial(_double, doubling_time_days=d), df.columns,))
        double_arr = [x if x < max_val else np.nan for x in double_arr]
        df.loc[f"double in {d} days"] = double_arr

    return df
