"""Transforms, i.e. maps AGS data to Bedrock's schema"""

import pandas as pd
import pandera as pa
from pandera.typing import DataFrame, Series
from pyproj import CRS

from bedrock.gi.ags.schemas import Ags3SAMP, BaseSAMP
from bedrock.gi.schemas import Project


@pa.check_types(lazy=True)
def ags_proj_to_brgi_project(ags_proj_df: pd.DataFrame, crs: CRS) -> DataFrame[Project]:
    ags_proj_df["crs_wkt"] = crs.to_wkt()
    ags_proj_df["project_uid"] = ags_proj_df["PROJ_ID"]
    return ags_proj_df


class Ags3SAMP_REF(BaseSAMP):
    SAMP_REF: Series[str]


@pa.check_types(lazy=True)
def generate_sample_ids_for_ags3(
    ags3_samp_df: DataFrame[BaseSAMP],
) -> DataFrame[Ags3SAMP]:
    try:
        # SAMP_REF really should not be able to be null...
        Ags3SAMP_REF.validate(ags3_samp_df)
        print(
            "Generating unique sample IDs for AGS 3 data: 'sample_id'='{SAMP_REF}_{HOLE_ID}'"
        )
        ags3_samp_df["sample_id"] = (
            ags3_samp_df["SAMP_REF"].astype(str)
            + "_"
            + ags3_samp_df["HOLE_ID"].astype(str)
        )
    except pa.errors.SchemaError as exc:
        print(f"CAUTION: The AGS 3 SAMP group contains rows without SAMP_REF:\n{exc}")

        if "non-nullable series 'SAMP_REF'" in str(exc):
            print(
                "\nTo ensure unique sample IDs: 'sample_id'='{SAMP_REF}_{SAMP_TOP}_{HOLE_ID}'\n"
            )
            ags3_samp_df["sample_id"] = (
                ags3_samp_df["SAMP_REF"].astype(str)
                + "_"
                + ags3_samp_df["SAMP_TOP"].astype(str)
                + "_"
                + ags3_samp_df["HOLE_ID"].astype(str)
            )

    return ags3_samp_df
