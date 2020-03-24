from .cssegisand_data import corona_country_data, get_doubling_time_ts_df
from .worldometer import WorldOMeterDataFetcher

# processed data
worldometer_fetcher = WorldOMeterDataFetcher(use_cache=True)
corona_table_data = worldometer_fetcher.get_worldometer_data()
