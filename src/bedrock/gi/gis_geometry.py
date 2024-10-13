from typing import Dict, Tuple, Union

import geopandas as gpd
import numpy as np
import pandas as pd
from pyproj import Transformer
from pyproj.crs import CRS
from shapely.geometry import LineString, Point


def calculate_gis_geometry(
    no_gis_brgi_db: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]],
) -> Dict[str, gpd.GeoDataFrame]:
    # Make sure that the Bedrock database is not changed outside this function.
    brgi_db = no_gis_brgi_db.copy()

    print(
        "Calculating GIS geometry for the Bedrock 'Location', 'Sample', 'InSitu_' and 'Lab_' database tables..."
    )

    # Check if all projects have the same CRS
    if not brgi_db["Project"]["crs_wkt"].nunique() == 1:
        raise ValueError(
            "All projects must have the same CRS (Coordinate Reference System).\n"
            "Raise an issue on GitHub in case you need to be able to combine GI data that was acquired in multiple different CRS's."
        )

    crs = CRS.from_wkt(brgi_db["Project"]["crs_wkt"].iloc[0])

    brgi_db["Location"] = calculate_location_gis_geometry(brgi_db["Location"], crs)
    print("'Location' GIS geometry was calculated successfully.")

    brgi_db["LonLatHeight"] = gpd.GeoDataFrame(
        brgi_db["Location"][
            [
                "project_uid",
                "location_uid",
            ]
        ],
        geometry=brgi_db["Location"].apply(
            lambda row: Point(
                row["longitude"], row["latitude"], row["wgs84_ground_level_height"]
            ),
            axis=1,
        ),
        crs=4326,
    )
    print("'LonLatHeight' table with GI location points was created successfully.")
    print(
        "    Points have WGS84 (Longitude, Latitude, Ground Level Ellipsoidal Height) coordinates."
    )

    location_child = brgi_db["Sample"].copy()
    location_child = pd.merge(
        location_child,
        brgi_db["Location"][
            ["location_uid", "easting", "northing", "ground_level_elevation"]
        ],
        on="location_uid",
        how="left",
    )
    location_child["elevation_at_top"] = (
        location_child["ground_level_elevation"] - location_child["depth_to_top"]
    )
    brgi_db["Sample"]["elevation_at_top"] = location_child["elevation_at_top"]
    location_child["elevation_at_base"] = (
        location_child["ground_level_elevation"] - location_child["depth_to_base"]
    )
    brgi_db["Sample"]["elevation_at_base"] = location_child["elevation_at_base"]
    brgi_db["Sample"] = gpd.GeoDataFrame(
        brgi_db["Sample"],
        geometry=location_child.apply(
            lambda row: LineString(
                [
                    (row["easting"], row["northing"], row["ground_level_elevation"]),
                    (row["easting"], row["northing"], row["elevation_at_base"]),
                ]
            )
            if not np.isnan(row["elevation_at_base"])
            else Point(
                (row["easting"], row["northing"], row["ground_level_elevation"])
            ),
            axis=1,
        ),
        crs=crs,
    )
    print("'Sample' GIS geometry was calculated successfully.")

    return brgi_db


def calculate_location_gis_geometry(
    brgi_location: Union[pd.DataFrame, gpd.GeoDataFrame], crs: CRS
) -> gpd.GeoDataFrame:
    """
    Calculate GIS geometry for a set of Ground Investigation locations.

    Args:
        brgi_location (Union[pd.DataFrame, gpd.GeoDataFrame]): The GI locations to calculate GIS geometry for.
        crs (pyproj.CRS): The Coordinate Reference System (CRS) to use for the GIS geometry.

    Returns:
        gpd.GeoDataFrame: The GIS geometry for the given GI locations, with *additional* columns:
            longitude: The longitude of the location in the WGS84 CRS.
            latitude: The latitude of the location in the WGS84 CRS.
            wgs84_ground_level_height: The height of the ground level of the location in the WGS84 CRS.
            elevation_at_base: The elevation at the base of the location.
            geometry: The GIS geometry of the location.
    """
    # Calculate Elevation at base of GI location
    brgi_location["elevation_at_base"] = (
        brgi_location["ground_level_elevation"] - brgi_location["depth_to_base"]
    )

    # Make a gpd.GeoDataFrame from the pd.DataFrame by creating GIS geometry
    brgi_location = gpd.GeoDataFrame(
        brgi_location,
        geometry=brgi_location.apply(
            lambda row: LineString(
                [
                    (row["easting"], row["northing"], row["ground_level_elevation"]),
                    (row["easting"], row["northing"], row["elevation_at_base"]),
                ]
            ),
            axis=1,
        ),
        crs=crs,
    )

    # Calculate WGS84 geodetic coordinates
    brgi_location[["longitude", "latitude", "wgs84_ground_level_height"]] = (
        brgi_location.apply(
            lambda row: calculate_wgs84_location(
                from_crs=crs,
                easting=row["easting"],
                northing=row["northing"],
                elevation=row["ground_level_elevation"],
            ),
            axis=1,
            result_type="expand",
        )
    )

    return brgi_location


def calculate_wgs84_location(
    from_crs: CRS, easting: float, northing: float, elevation: Union[float, None] = None
) -> Tuple:
    """Transform coordinates from an arbitrary Coordinate Reference System (CRS) to
    the WGS84 CRS, which is the standard for geodetic coordinates.

    Args:
        from_crs (pyproj.CRS): The pyproj.CRS object of the CRS to transform from.
        easting (float): The easting coordinate of the point to transform.
        northing (float): The northing coordinate of the point to transform.
        elevation (float or None, optional): The elevation of the point to
            transform. Defaults to None.

    Returns:
        tuple: A tuple containing the longitude, latitude and WGS84 height of the
            transformed point, in that order. The height is None if no elevation was
            given, or if the provided CRS doesn't have a proper datum defined.
    """
    transformer = Transformer.from_crs(from_crs, 4326, always_xy=True)
    if elevation:
        lon, lat, wgs84_height = transformer.transform(easting, northing, elevation)
    else:
        lon, lat = transformer.transform(easting, northing)
        wgs84_height = None

    return lon, lat, wgs84_height
