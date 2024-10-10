"""Transforms, i.e. maps, AGS data to Bedrock's schema"""

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame
from pyproj import CRS

from bedrock.gi.ags.schemas import Ags3HOLE, Ags3SAMP, BaseSAMP
from bedrock.gi.schemas import BaseLocation, BaseSample, Project


@pa.check_types(lazy=True)
def ags_proj_to_brgi_project(ags_proj: pd.DataFrame, crs: CRS) -> DataFrame[Project]:
    ags_proj["crs_wkt"] = crs.to_wkt()
    ags_proj["project_uid"] = ags_proj["PROJ_ID"]
    return ags_proj


@pa.check_types(lazy=True)
def ags3_hole_to_brgi_location(
    ags3_hole: DataFrame[Ags3HOLE], project_uid: str
) -> DataFrame[BaseLocation]:
    brgi_location = ags3_hole
    brgi_location["project_uid"] = project_uid
    brgi_location["location_source_id"] = ags3_hole["HOLE_ID"]
    brgi_location["location_uid"] = (
        ags3_hole["HOLE_ID"] + "_" + ags3_hole["project_uid"]
    )
    brgi_location["location_type"] = ags3_hole["HOLE_TYPE"]
    brgi_location["easting"] = ags3_hole["HOLE_NATE"]
    brgi_location["northing"] = ags3_hole["HOLE_NATN"]
    brgi_location["ground_level"] = ags3_hole["HOLE_GL"]
    brgi_location["depth_to_base"] = ags3_hole["HOLE_FDEP"]
    return ags3_hole


@pa.check_types(lazy=True)
def ags3_samp_to_brgi_sample(
    ags3_samp: DataFrame[Ags3SAMP],
    project_uid: str,
) -> DataFrame[BaseSample]:
    brgi_sample = ags3_samp
    brgi_sample["project_uid"] = project_uid
    brgi_sample["location_source_id"] = ags3_samp["HOLE_ID"]
    brgi_sample["location_uid"] = ags3_samp["HOLE_ID"] + "_" + ags3_samp["project_uid"]
    brgi_sample["sample_source_id"] = ags3_samp["sample_id"]
    brgi_sample["sample_uid"] = ags3_samp["sample_id"] + "_" + ags3_samp["project_uid"]
    brgi_sample["depth_to_top"] = ags3_samp["SAMP_TOP"]
    brgi_sample["depth_to_base"] = ags3_samp["SAMP_BASE"]
    return brgi_sample


@pa.check_types(lazy=True)
def generate_sample_ids_for_ags3(
    ags3_with_samp: DataFrame[BaseSAMP],
) -> DataFrame[Ags3SAMP]:
    ags3_with_samp["sample_id"] = (
        ags3_with_samp["SAMP_REF"].astype(str)
        + "_"
        + ags3_with_samp["SAMP_TYPE"].astype(str)
        + "_"
        + ags3_with_samp["SAMP_TOP"].astype(str)
        + "_"
        + ags3_with_samp["HOLE_ID"].astype(str)
    )
    # try:
    #     # SAMP_REF really should not be able to be null... Right?
    #     # Maybe SAMP_REF can be null when the
    #     Ags3SAMP_REF.validate(ags3_samp)
    #     print(
    #         "Generating unique sample IDs for AGS 3 data: 'sample_id'='{SAMP_REF}_{HOLE_ID}'"
    #     )
    #     ags3_samp["sample_id"] = (
    #         ags3_samp["SAMP_REF"].astype(str) + "_" + ags3_samp["HOLE_ID"].astype(str)
    #     )
    # except pa.errors.SchemaError as exc:
    #     print(f"CAUTION: The AGS 3 SAMP group contains rows without SAMP_REF:\n{exc}")

    #     if "non-nullable series 'SAMP_REF'" in str(exc):
    #         print(
    #             "\nTo ensure unique sample IDs: 'sample_id'='{SAMP_REF}_{SAMP_TOP}_{HOLE_ID}'\n"
    #         )
    #         ags3_samp["sample_id"] = (
    #             ags3_samp["SAMP_REF"].astype(str)
    #             + "_"
    #             + ags3_samp["SAMP_TOP"].astype(str)
    #             + "_"
    #             + ags3_samp["HOLE_ID"].astype(str)
    #         )

    return ags3_with_samp
