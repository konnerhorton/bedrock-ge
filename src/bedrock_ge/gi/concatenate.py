from typing import Dict, Union

import geopandas as gpd
import pandas as pd


def concatenate_databases(
    db1: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]],
    db2: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]],
) -> Dict[str, pd.DataFrame]:
    """Concatenate two dictionaries of pandas dataframes into one dict of dfs.

    The function concatenates the pandas dataframes of the second dict of dfs to the first dict of df for the keys that they have in common.
    Keys that don't occur in either of the dict of dfs need to end up in the final dict of dfs.

    Args:
        db1 (Dict[str, pd.DataFrame]): A dictionary of pandas DataFrames, i.e. a database.
        db2 (Dict[str, pd.DataFrame]): A dictionary of pandas DataFrames, i.e. a database.

    Returns:
        dict: A dictionary of concatenated pandas DataFrames.
    """
    # Create a new dict to store the concatenated dataframes
    concatenated_dict = {key: df.dropna(axis=1, how="all") for key, df in db1.items()}

    # Iterate over the keys in the second dict
    for key, df in db2.items():
        df = df.dropna(axis=1, how="all")
        # If the key is also in the first dict, concatenate the dataframes
        if key in db1:
            concatenated_dict[key] = pd.concat([db1[key], df], ignore_index=True)
        # If the key is not in the first dict, just add it to the new dict
        else:
            concatenated_dict[key] = df

    return concatenated_dict
