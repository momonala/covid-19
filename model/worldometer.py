import logging
import os
import re
import sys
from glob import glob
from typing import List

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dateutil import parser

from model.utils import country_map

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)


class WorldOMeterDataFetcher:
    def __init__(self, use_cache=True):
        self.use_cache = use_cache
        self._data_dicts = {
            "corona": {
                "url": "https://www.worldometers.info/coronavirus/#countries",
                "columns": [
                    "idx",
                    "Country",
                    "Total Cases",
                    "New Cases",
                    "Total Deaths",
                    "New Deaths",
                    "Total Recovered",
                    "Active Cases",
                    "Serious/Critical",
                    "Cases/1M pop",
                    "Deaths/1M pop",
                    "Total Tests",
                    "Tests/1M pop",
                    "Population",
                    "Continent",
                ],
            },
            "population": {
                "url": "https://www.worldometers.info/world-population/population-by-country/",
                "columns": [
                    "Index",
                    "Country",
                    "Population",
                    "Yearly Change",
                    "Net Change",
                    "Density P/Km2",
                    "Land Area Km2",
                    "Migrants",
                    "Fertility Rate",
                    "Median Age",
                    "Urban Population %",
                    "World Share",
                ],
            },
        }

    @staticmethod
    def _read_from_cache():
        """Read the latest csv file from the cache."""
        try:
            cached_file = sorted(glob("model/*.csv"))[0]
        except IndexError as e:
            logger.error(
                "Cache is empty."
                " Please run `python -m model.worldometer` to update the cache before starting the app."
            )
            sys.exit(1)

        logger.info(f"Using cached worldometer {cached_file}")
        return pd.read_csv(cached_file)

    def get_worldometer_data(self) -> pd.DataFrame:
        if self.use_cache:
            return self._read_from_cache()

        corona_df = self._get_worldometer_data_single_source("corona")
        corona_df = corona_df.drop(["Continent", "idx", "Population"], axis=1)
        corona_df["Case Fatality Ratio"] = np.round(
            corona_df["Total Deaths"] / corona_df["Total Cases"] * 100, 2
        )
        population_df = self._get_worldometer_data_single_source("population")

        def _normalize_population_names(
            p: pd.DataFrame, c: pd.DataFrame
        ) -> pd.DataFrame:
            logger.info("Processing corona and population dataframes")

            # match country names of two dataframes, drop anything not in the intersection
            p["Country"] = p["Country"].apply(lambda x: country_map.get(x, x))
            c["Country"] = c["Country"].apply(lambda x: country_map.get(x, x))
            df = pd.merge(c, p, on="Country")
            diff = list(set(c.Country) - set(df.Country))
            # diff += list(set(p.Country) - set(df.Country))
            logger.warning(f"Lost corona data for {diff}")

            df = df.drop(
                [
                    "Index",
                    "Yearly Change",
                    "Net Change",
                    "Migrants",
                    "Fertility Rate",
                    "World Share",
                ],
                axis=1,
            )

            # add world total
            df.loc[len(df)] = [
                "World",
                np.sum(df["Total Cases"]),
                np.sum(df["New Cases"]),
                np.sum(df["Total Deaths"]),
                np.sum(df["New Deaths"]),
                np.sum(df["Total Recovered"]),
                np.sum(df["Active Cases"]),
                np.sum(df["Serious/Critical"]),
                int(np.sum(df["Total Cases"]) / np.sum(df["Population"]) * 1e6),
                int(np.sum(df["Total Deaths"]) / np.sum(df["Population"]) * 1e6),
                np.sum(df["Total Tests"]),
                int(np.sum(df["Total Tests"]) / np.sum(df["Population"]) * 1e6),
                int(np.sum(df["Total Deaths"]) / np.sum(df["Total Cases"]) * 100),
                np.sum(df["Population"]),
                int(np.mean(df["Density P/Km2"])),
                np.sum(df["Land Area Km2"]),
                int(np.mean(df["Median Age"])),
                int(np.mean(df["Urban Population %"])),
            ]

            df = df.sort_values("Total Cases", ascending=False)

            return df

        data = _normalize_population_names(population_df, corona_df)

        _last_updated = self._data_dicts["corona"]["last_updated"]
        _save_path = os.path.join("model", f"worldometer_{_last_updated}.csv")
        data.to_csv(_save_path, index=False)
        logger.info(f"saved cached worldometer csv to {_save_path}")

        return data

    def _get_worldometer_data_single_source(self, data_type: str) -> pd.DataFrame:
        """Return a dataframe from worldometer.info.

        Args:
            data_type: either 'corona' or 'population'
        """
        data_dict = self._data_dicts[data_type]
        logger.info(f"fetching worldometer data for {data_dict['url']}")
        latest_data = self._get_html(data_dict["url"])
        data = self._get_worldometer_table_data(latest_data, data_dict["columns"])
        self._data_dicts[data_type]["last_updated"] = self._parse_last_updated(
            latest_data
        )

        return data

    def _get_worldometer_table_data(
        self, raw_data: str, columns: List[str]
    ) -> pd.DataFrame:
        """
        Parses the raw HTML response from Worldometer and returns a DataFrame from it

        Args:
            raw_data (string): request.text html from Worldometer

        """
        soup = BeautifulSoup(raw_data, features="html.parser")
        countries_data = soup.find("table").find("tbody").findAll("tr")
        parsed_data = [
            [data.get_text() for data in country.findAll("td")]
            for country in countries_data
        ]
        data = pd.DataFrame(parsed_data, columns=columns)

        for col in data.columns:
            if col != "Country":
                data[col] = data[col].apply(self._cleanup)
        return data

    @staticmethod
    def _cleanup(s: str):
        try:
            return float(s.replace("+", "").replace(",", "").replace("%", ""))
        except Exception:
            return np.nan

    @staticmethod
    def _parse_last_updated(raw_data: str) -> str:
        """
        Parses the raw HTML response from Worldometer and returns the lastest update time from the webpage

        Args:
            raw_data (string): request.text from Worldometer

        Returns:
            Last updated time (string) in format `year_month_day_hour_minute`
        """
        soup = BeautifulSoup(raw_data, features="html.parser")
        last_updated = soup(text=re.compile("Last updated: "))  # returns List[str]
        if last_updated:
            last_updated_str = last_updated[0].string.replace("Last updated: ", "")
            return parser.parse(last_updated_str).strftime("%Y_%m_%d_%H_%M")

    @staticmethod
    def _get_html(url: str) -> str:
        """Gets raw HTML from worldometers/coronavirus"""
        try:
            logging.info(f"Scraping data from {url}")
            res = requests.get(url, timeout=15)
            logging.info(f"Scraped data. 200")
        except requests.Timeout:
            raise GatewayError(
                "Timeout received whilst retrieving data from WorldOMeter"
            )
        except requests.RequestException:
            raise GatewayError(
                "Some Error Ocurred whils fetching data from WorldOMeter({str(requests.RequestException)})"
            )

        if res.status_code != 200:
            raise GatewayError("Website returned a Non-200 status code")

        return res.text


class GatewayError(Exception):
    pass


if __name__ == "__main__":
    data_parser = WorldOMeterDataFetcher(use_cache=False)
    data_parser.get_worldometer_data()
