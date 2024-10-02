from typing import Dict

from pyproj.crs import CRS

from bedrock.gi.ags.read import ags_to_dfs

# from bedrock.gi.ags.validate import validate_ags
# from bedrock.gi.ags.convert import ags_to_bedrock_dfs


def ags_to_bedrock(ags_data: str, crs: CRS) -> Dict:
    ags_dfs = ags_to_dfs(ags_data)

    # Convert AGS pandas DataFrames to Bedrock pandas DataFrames
    bedrock_dfs = ags_dfs

    # Calculate the GIS geometry for all Bedrock tables,
    # in order to convert Bedrock pandas DataFrames to geopandas GeoDataFrames
    bedrock_gdfs = bedrock_dfs

    return bedrock_gdfs
