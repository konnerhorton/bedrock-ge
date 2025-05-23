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
    CRS(3855)
    return


app._unparsable_cell(
    r"""
    class BedrockProjectMapping(BaseModel):
        \"project_uid\": str
        \"horizontal_crs\": 
        \"vertical_crs\": CRS = Field(default=CRS(3855))
        \"compound_crs\": Optional[CRS] = None

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
