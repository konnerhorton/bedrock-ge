import marimo

__generated_with = "0.13.11"
app = marimo.App(width="medium")


@app.cell
def _():
    from typing import Optional

    import marimo as mo
    import pandas as pd
    from pydantic import BaseModel
    from pyproj import CRS
    return CRS, pd


@app.cell
def _(CRS):
    vert_crs_3855 = CRS(3855)
    crs_7415 = CRS(7415)
    crs_9518 = CRS(9518)
    crs_components = extract_crs_components(crs_7415)
    crs_components
    return


@app.function
def extract_crs_components(compound_crs):
    """Extract horizontal and vertical CRS from a compound CRS"""
    if not compound_crs.is_compound:
        return compound_crs, None
    
    horizontal_crs = None
    vertical_crs = None
    
    for sub_crs in compound_crs.sub_crs_list:
        if sub_crs.is_projected or sub_crs.is_geographic:
            print(f"Horizontal CRS {sub_crs.name} is a {sub_crs.type_name} and has EPSG:{sub_crs.to_epsg()}.")
            horizontal_crs = sub_crs
        elif sub_crs.is_vertical:
            print(f"Vertical CRS {sub_crs.name} has EPSG:{sub_crs.to_epsg()}.")
            vertical_crs = sub_crs
        else:
            print(f"This CRS is not horizontal (projected or geographic) nor vertical: {sub_crs.type_name}")
    
    return horizontal_crs, vertical_crs


app._unparsable_cell(
    r"""
    class BedrockProjectMapping(BaseModel):
        \"data\": dict | pd.Dataframe | None,
        \"project_uid\": str
        \"horizontal_crs\": CRS
        \"vertical_crs\": CRS = Field(default=CRS(3855))
        # \"compound_crs\": Optional[CRS] = None # In case a

    class brdb_mapping_model(BaseModel):
        \"\"
    """,
    name="_"
)


@app.cell
def _(pd):
    # The list of dictionaries that contains all the data to append one 
    # Is this the input model or what is this?
    ags4_brdb_model = [
        {
            "Project": {
                "data": pd.Dataframe,
                "project_uid_column": "PROJ_ID",
                "crs": 7415
            },
            "Location": {
                "data": pd.Dataframe,
                "location_id_column": "LOCA_ID",
                "easting_column": "LOCA_NATE",
                "northing_column": "LOCA_NATN",
                "ground_level_elevation_column": "LOCA_GL",
                "depth_to_base_column": "LOCA_FDEP"

            },
            "Sample": {
                "data": pd.Dataframe,
                "sample_id_column": ["SAMP_ID", "SAMP_REF", "SAMP_TYPE", "SAMP_TOP"]
            },
            "InSitu_XXXX": {

            },
            "Lab_XXXX": {
                "project_id": "x",
                "location_id": "loc",
            }
        }
    ]
    return


@app.cell
def _(pd):
    ags3_brdb_model = [
        {
            "Project": {
                "data": pd.Dataframe,
                "project_uid_column": "PROJ_ID",
                "crs": 7415
            },
            "Location": {
                "data": pd.Dataframe,
                "location_id_column": "HOLE_ID",
                "easting_column": "HOLE_NATE",
                "northing_column": "HOLE_NATN",
                "ground_level_elevation_column": "HOLE_GL",
                "depth_to_base_column": "HOLE_FDEP"
            },
            "Sample": {
                "data": pd.Dataframe,
                "sample_id_column": ["SAMP_ID", "SAMP_REF", "SAMP_TYPE", "SAMP_TOP"]
            },
            "InSitu_XXXX": {

            },
            "Lab_XXXX": {
                "project_id": "x",
                "location_id": "loc",
            }
        }
    ]
    return


@app.cell
def _(pd):
    wekahills_brdb_mapping = [
        {
            "Project": {
                "data": pd.Dataframe,
                "project_uid_column": "PROJ_ID", # hier nog over nadenken?!?!
                "crs": 7415
            },
            "Location": {
                "data": pd.Dataframe,
                "location_id_column": "LocationID",
                "easting_column": "Easting",
                "northing_column": "Northing",
                "ground_level_elevation_column": "GroundLevel",
                "depth_to_base_column": "FinalDepth"
            },
            "Sample": {
                "data": pd.Dataframe,
                "sample_id_column": ["SAMP_ID", "SAMP_REF", "SAMP_TYPE", "SAMP_TOP"]
            },
            "InSitu_XXXX": {
                "data": pd.Dataframe,
                "location_id_column": "LocationID",

            },
            "Lab_XXXX": {
                "project_id": "x",
                "location_id": "loc",
            }
        }
    ]
    return


if __name__ == "__main__":
    app.run()
