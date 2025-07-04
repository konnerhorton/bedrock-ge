from pathlib import Path
from typing import IO

import pandas as pd
from pyproj import CRS
from python_ags4 import AGS4

from bedrock_ge.gi.ags_schemas import Ags4LOCA, Ags4SAMP, check_ags_proj_group
from bedrock_ge.gi.mapping_models import (
    BedrockGIMapping,
    InSituTestTableMapping,
    LabTestTableMapping,
    LocationTableMapping,
    OtherTable,
    ProjectTableMapping,
    SampleTableMapping,
)


def ags4_to_dfs(
    source: str | Path | IO[str] | IO[bytes] | bytes,
) -> dict[str, pd.DataFrame]:
    """Converts AGS 4 data to a dictionary of pandas DataFrames.

    Args:
        source (str | Path | IO[str] | IO[bytes] | bytes): The AGS4 file (str or Path)
            or a file-like object that represents and AGS4 file.

    Returns:
        dict[str, pd.DataFrame]: A dictionary of pandas DataFrames, where each key
            represents a group name from AGS 4 data, and the corresponding value is a
            pandas DataFrame containing the data for that group.
    """
    ags4_tups = AGS4.AGS4_to_dataframe(source)

    ags4_dfs = {}
    for group, df in ags4_tups[0].items():
        df = df.loc[2:].drop(columns=["HEADING"]).reset_index(drop=True)
        ags4_dfs[group] = df

    return ags4_dfs


def ags4_to_brgi_db_mapping(
    source: str | Path | IO[str] | IO[bytes] | bytes,
    projected_crs: CRS,
    vertical_crs: CRS,
    # encoding: str,
) -> BedrockGIMapping:
    """Map AGS 4 data to the Bedrock GI data model.

    Args:
        source (str | Path | IO[str] | IO[bytes] | bytes): The AGS4 file (str or Path)
            or a file-like object that represents and AGS4 file.
        projected_crs (CRS): Projected coordinate reference system (CRS).
            vertical_crs (CRS, optional): Vertical CRS. Defaults to EGM2008 height,
            EPSG:3855 which measures the orthometric height w.r.t. the Earth Gravitational
            Model 2008.
        encoding (str): Encoding of the text file or bytes stream.

    Returns:
        BedrockGIDatabaseMapping: Object that maps AGS 4 data to Bedrock GI data model.
    """
    # TODO: consider removing after resolving issue #57, also might remove encoding parameter
    ags4_dfs = ags4_to_dfs(source)
    import numpy as np

    # Handle empty strings
    ags4_dfs = {group: df.where(df != "", np.nan) for group, df in ags4_dfs.items()}

    # TODO: this maybe should run a full check to make sure the AGS standard is followed
    # or run this check outside of this function (would depend on resolution to issue #57)
    check_ags_proj_group(ags4_dfs["PROJ"])
    ags4_project = ProjectTableMapping(
        data=ags4_dfs["PROJ"].to_dict(orient="records")[0],
        project_id=ags4_dfs["PROJ"].at[0, "PROJ_ID"],
        horizontal_crs=projected_crs,
        vertical_crs=vertical_crs,
    )
    del ags4_dfs["PROJ"]

    Ags4LOCA.validate(ags4_dfs["LOCA"])
    ags4_location = LocationTableMapping(
        data=ags4_dfs["LOCA"],
        location_id_column="LOCA_ID",
        easting_column="LOCA_NATE",
        northing_column="LOCA_NATN",
        ground_level_elevation_column="LOCA_GL",
        depth_to_base_column="LOCA_FDEP",
    )
    del ags4_dfs["LOCA"]

    if "SAMP" in ags4_dfs.keys():
        Ags4SAMP.validate(ags4_dfs["SAMP"])
        samp_df = ags4_dfs["SAMP"]
        samp_df = _add_sample_source_id(samp_df)
        ags4_sample = SampleTableMapping(
            data=samp_df,
            location_id_column="LOCA_ID",
            sample_id_column="sample_source_id",
            depth_to_top_column="SAMP_TOP",
        )
        del ags4_dfs["SAMP"]
    else:
        ags4_sample = None

    ags4_lab_tests = []
    ags4_insitu_tests = []
    ags4_other_tables = []

    for group, df in ags4_dfs.items():
        # Non-standard group names contain the "?" prefix.
        # => checking that "SAMP_TOP" / "LOCA_ID" is in the columns is too restrictive.
        if "SAMP_TOP" in df.columns:
            df = _add_sample_source_id(df)
            ags4_lab_tests.append(
                LabTestTableMapping(
                    table_name=group,
                    data=df,
                    location_id_column="LOCA_ID",
                    sample_id_column="sample_source_id",
                )
            )
        elif "LOCA_ID" in df.columns:
            top_depth, base_depth = _get_depth_columns(group, list(df.columns))
            if not top_depth:
                continue
            ags4_insitu_tests.append(
                InSituTestTableMapping(
                    table_name=group,
                    data=df,
                    location_id_column="LOCA_ID",
                    depth_to_top_column=top_depth,
                    depth_to_base_column=base_depth,
                )
            )
        else:
            ags4_other_tables.append(OtherTable(table_name=group, data=df))

    brgi_db_mapping = BedrockGIMapping(
        Project=ags4_project,
        Location=ags4_location,
        InSitu=ags4_insitu_tests,
        Sample=ags4_sample,
        Lab=ags4_lab_tests,
        Other=ags4_other_tables,
    )
    return brgi_db_mapping


def _add_sample_source_id(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: handle empty strings and null values better (skipped or replaced?)
    df["sample_source_id"] = (
        df["SAMP_REF"].astype(str)
        + "-"
        + df["SAMP_TYPE"].astype(str)
        + "-"
        + df["SAMP_TOP"].astype(str)
        + "-"
        + df["LOCA_ID"].astype(str)
    )
    return df


def _get_depth_columns(group: str, headers: list[str]) -> tuple[str | None, str | None]:
    top_depth: str | None = f"{group}_TOP"
    base_depth: str | None = f"{group}_BASE"

    # TODO: consider turning this into something more generalized (dictionary map or similar) so it is cleaner
    match group:
        case "CDIA":
            top_depth = "CDIA_DPTH"
        case "CORE":
            base_depth = "CORE_BOT"
        case "HDIA":
            top_depth = "HDIA_DPTH"
        case "PTIM":
            top_depth = "PTIM_DPTH"
        case "IVAN":
            top_depth = "IVAN_DPTH"
        case "STCN":
            top_depth = "STCN_DPTH"
        case "POBS" | "PREF":
            top_depth = "PREF_TDEP"
        case "DREM":
            top_depth = "DREM_DPTH"
        case "PRTD" | "PRTG" | "PRTL":
            top_depth = "PRTD_DPTH"
        case "CDIA":
            top_depth = "CDIA_DPTH"
        case "CHIS":
            top_depth = "CHIS_FROM"
            base_depth = "CHIS_TO"
        case "DCPG" | "DCPT":
            top_depth = "DCPG_DPTH"
        case "DPRB":
            top_depth = "DPRB_DPTH"
        case "DREM":
            top_depth = "DREM_REM"
        case "FGHG":
            top_depth = "FGHG_PRWL"
        case "FRAC":
            top_depth = "FRAC_FROM"
            base_depth = "FRAC_TO"
        case "HDIA":
            base_depth = "HDIA_DPTH"
        case "ICBR":
            top_depth = "ICBR_DPTH"
        case "IDEN":
            top_depth = "IDEN_DPTH"
        case "IFID":
            top_depth = "IFID_DPTH"
        case "IPEN":
            top_depth = "IPEN_DPTH"
        case "IPID":
            top_depth = "IPID_DPTH"
        case "IPRT":
            top_depth = "IPRG_TOP"
            base_depth = "IPRG_BASE"
        case "IRDX":
            top_depth = "IRDX_DPTH"
        case "IRES":
            top_depth = "IRES_DPTH"
        case "IVAN":
            top_depth = "IVAN_DPTH"
        case "PLTG" | "PLTT":
            top_depth = "PLTG_DPTH"
        case "PMTD" | "PMTG" | "PMTL":
            top_depth = "PMTG_DPTH"
        case "PUMT":
            top_depth = "PUMT_DPTH"
        case "SCDG" | "SCDT":
            top_depth = "SCDG_DPTH"
        case "SCPT":
            top_depth = "SCPT_DPTH"
        case "WGPG":
            top_depth = "WGPG_START"
            base_depth = "WGPG_STOP"
        case "WGPT":
            top_depth = "WGPT_DPTH"
        case "WSTD" | "WSTG":
            top_depth = "WSTG_DPTH"
    # Some groups do not have relevant depth values for various reasons
    depth_value_exceptions = ["MOND", "MONG", "DPRG", "TREM"]

    if top_depth not in headers:
        top_depth = None
    if base_depth not in headers:
        base_depth = None
    if not top_depth and not base_depth and group not in depth_value_exceptions:
        raise ValueError(
            f'The in-situ test group "{group}" group in this AGS 4 file does not contain a top or base depth heading!'
        )

    return top_depth, base_depth