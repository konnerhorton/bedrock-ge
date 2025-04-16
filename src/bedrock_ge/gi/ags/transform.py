"""Transforms, i.e. maps, AGS data to Bedrock's schema"""

from typing import Dict

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame
from pyproj import CRS

from bedrock_ge.gi.ags.schemas import Ags3HOLE, Ags3SAMP, BaseSAMP
from bedrock_ge.gi.schemas import BaseInSitu, BaseLocation, BaseSample, Project
from bedrock_ge.gi.validate import check_foreign_key


def ags3_db_to_no_gis_brge_db(
    ags3_db: Dict[str, pd.DataFrame], crs: CRS
) -> Dict[str, pd.DataFrame]:
    # Make sure that the AGS 3 database is not changed outside this function.
    ags3_db = ags3_db.copy()

    print("Transforming AGS 3 groups to Bedrock tables...")

    # Instantiate Bedrock dictionary of pd.DataFrames
    brge_db = {}

    # Project
    print("Transforming AGS 3 group 'PROJ' to Bedrock GI 'Project' table...")
    brge_db["Project"] = ags_proj_to_brge_project(ags3_db["PROJ"], crs)
    project_uid = brge_db["Project"]["project_uid"].item()
    del ags3_db["PROJ"]

    # Locations
    if "HOLE" in ags3_db.keys():
        print("Transforming AGS 3 group 'HOLE' to Bedrock GI 'Location' table...")
        brge_db["Location"] = ags3_hole_to_brge_location(ags3_db["HOLE"], project_uid)  # type: ignore
        del ags3_db["HOLE"]
    else:
        print(
            "Your AGS 3 data doesn't contain a HOLE group, i.e. Ground Investigation locations."
        )

    # Samples
    if "SAMP" in ags3_db.keys():
        print("Transforming AGS 3 group 'SAMP' to Bedrock GI 'Sample' table...")
        check_foreign_key("HOLE_ID", brge_db["Location"], ags3_db["SAMP"])
        ags3_db["SAMP"] = generate_sample_ids_for_ags3(ags3_db["SAMP"])  # type: ignore
        brge_db["Sample"] = ags3_samp_to_brge_sample(ags3_db["SAMP"], project_uid)  # type: ignore
        del ags3_db["SAMP"]
    else:
        print("Your AGS 3 data doesn't contain a SAMP group, i.e. samples.")

    # The rest of the tables: 1. Lab Tests 2. In-Situ Measurements 3. Other tables
    for group, group_df in ags3_db.items():
        if "SAMP_REF" in ags3_db[group].columns:
            print(f"Project {project_uid} has lab test data: {group}.")
            brge_db[group] = group_df  # type: ignore
        elif "HOLE_ID" in ags3_db[group].columns:
            print(
                f"Transforming AGS 3 group '{group}' to Bedrock GI 'InSitu_{group}' table..."
            )
            check_foreign_key("HOLE_ID", brge_db["Location"], group_df)
            brge_db[f"InSitu_{group}"] = ags3_in_situ_to_brge_in_situ(  # type: ignore
                group, group_df, project_uid
            )
        else:
            brge_db[group] = ags3_db[group]  # type: ignore

    print(
        "Done",
        "The Bedrock database contains the following tables:",
        list(brge_db.keys()),
        sep="\n",
        end="\n\n",
    )
    return brge_db  # type: ignore


@pa.check_types(lazy=True)
def ags_proj_to_brge_project(ags_proj: pd.DataFrame, crs: CRS) -> DataFrame[Project]:
    ags_proj["crs_wkt"] = crs.to_wkt()
    ags_proj["project_uid"] = ags_proj["PROJ_ID"]

    return ags_proj  # type: ignore


@pa.check_types(lazy=True)
def ags3_hole_to_brge_location(
    ags3_hole: DataFrame[Ags3HOLE], project_uid: str
) -> DataFrame[BaseLocation]:
    brge_location = ags3_hole
    brge_location["project_uid"] = project_uid
    brge_location["location_source_id"] = ags3_hole["HOLE_ID"]
    brge_location["location_uid"] = (
        ags3_hole["HOLE_ID"] + "_" + ags3_hole["project_uid"]
    )
    brge_location["location_type"] = ags3_hole["HOLE_TYPE"]
    brge_location["easting"] = ags3_hole["HOLE_NATE"]
    brge_location["northing"] = ags3_hole["HOLE_NATN"]
    brge_location["ground_level_elevation"] = ags3_hole["HOLE_GL"]
    brge_location["depth_to_base"] = ags3_hole["HOLE_FDEP"]

    return ags3_hole  # type: ignore


@pa.check_types(lazy=True)
def ags3_samp_to_brge_sample(
    ags3_samp: DataFrame[Ags3SAMP],
    project_uid: str,
) -> DataFrame[BaseSample]:
    brge_sample = ags3_samp
    brge_sample["project_uid"] = project_uid
    brge_sample["location_source_id"] = ags3_samp["HOLE_ID"]
    brge_sample["location_uid"] = ags3_samp["HOLE_ID"] + "_" + ags3_samp["project_uid"]
    brge_sample["sample_source_id"] = ags3_samp["sample_id"]
    brge_sample["sample_uid"] = ags3_samp["sample_id"] + "_" + ags3_samp["project_uid"]
    brge_sample["depth_to_top"] = ags3_samp["SAMP_TOP"]
    brge_sample["depth_to_base"] = ags3_samp["SAMP_BASE"]

    return brge_sample  # type: ignore


@pa.check_types(lazy=True)
def ags3_in_situ_to_brge_in_situ(
    group_name: str, ags3_in_situ: pd.DataFrame, project_uid: str
) -> DataFrame[BaseInSitu]:
    """Transform, i.e. map, AGS 3 in-situ measurement data to Bedrock's in-situ data schema.

    Args:
        group_name (str): The AGS 3 group name.
        ags3_data (pd.DataFrame): The AGS 3 data.
        project_uid (str): The project uid.

    Returns:
        DataFrame[BaseInSitu]: The Bedrock in-situ data.
    """
    brge_in_situ = ags3_in_situ
    brge_in_situ["project_uid"] = project_uid
    brge_in_situ["location_uid"] = ags3_in_situ["HOLE_ID"] + "_" + project_uid

    top_depth = f"{group_name}_TOP"
    base_depth = f"{group_name}_BASE"

    if group_name == "CDIA":
        top_depth = "CDIA_CDEP"
    elif group_name == "FLSH":
        top_depth = "FLSH_FROM"
        base_depth = "FLSH_TO"
    elif group_name == "CORE":
        base_depth = "CORE_BOT"
    elif group_name == "HDIA":
        top_depth = "HDIA_HDEP"
    elif group_name == "PTIM":
        top_depth = "PTIM_DEP"
    elif group_name == "IVAN":
        top_depth = "IVAN_DPTH"
    elif group_name == "STCN":
        top_depth = "STCN_DPTH"
    elif group_name == "POBS" or group_name == "PREF":
        top_depth = "PREF_TDEP"
    elif group_name == "DREM":
        top_depth = "DREM_DPTH"
    elif group_name == "PRTD" or group_name == "PRTG" or group_name == "PRTL":
        top_depth = "PRTD_DPTH"
    elif group_name == "IPRM":
        if top_depth not in ags3_in_situ.columns:
            print(
                "\n🚨 CAUTION: The IPRM group in this AGS 3 file does not contain a 'IPRM_TOP' heading!",
                "🚨 CAUTION: Making the 'IPRM_BASE' heading the 'depth_to_top'...",
                sep="\n",
                end="\n\n",
            )
            top_depth = "IPRM_BASE"
            base_depth = "None"

    brge_in_situ["depth_to_top"] = ags3_in_situ[top_depth]
    brge_in_situ["depth_to_base"] = ags3_in_situ.get(base_depth)

    return brge_in_situ  # type: ignore


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
    #     print(f"🚨 CAUTION: The AGS 3 SAMP group contains rows without SAMP_REF:\n{exc}")

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

    return ags3_with_samp  # type: ignore
