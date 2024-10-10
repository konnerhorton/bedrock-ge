import pandas as pd


def check_ags_proj_group(ags_proj: pd.DataFrame) -> bool:
    """Checks if the AGS 3 or AGS 4 PROJ group is correct.

    Args:
        proj_df (pd.DataFrame): The DataFrame with the PROJ group.

    Raises:
        ValueError: If AGS 3 of AGS 4 PROJ group is not correct.

    Returns:
        bool: Returns True if the AGS 3 or AGS 4 PROJ group is correct.
    """

    if len(ags_proj) != 1:
        raise ValueError("The PROJ group must contain exactly one row.")

    project_id = ags_proj["PROJ_ID"].iloc[0]
    if not project_id:
        raise ValueError(
            'The project ID ("PROJ_ID" in the "PROJ" group) is missing from the AGS data.'
        )

    return True


def check_ags3_hole_ids_exist(
    ags3_hole: pd.DataFrame, ags3_group_with_hole_id: pd.DataFrame
) -> bool:
    """
    Checks if the HOLE_IDs in an AGS 3 group exist in the AGS 3 HOLE group.

    Args:
        ags3_hole (pd.DataFrame): The DataFrame with the AGS 3 HOLE group.
        ags3_group_with_hole_id (pd.DataFrame): The DataFrame with the group containing HOLE_IDs.

    Raises:
        ValueError: If the group contains HOLE_IDs that don't occur in the AGS 3 HOLE group.

    Returns:
        bool: Returns True if the HOLE_IDs in the group exist in the AGS 3 HOLE group.
    """

    # Get the name of the group
    group = ags3_group_with_hole_id.columns[-2].split("_")[0]

    # Get the HOLE_IDs that are missing in the HOLE group
    missing_hole_ids = ags3_group_with_hole_id[
        ~ags3_group_with_hole_id["HOLE_ID"].isin(ags3_hole["HOLE_ID"])
    ]

    # Raise an error if there are missing HOLE_IDs
    if len(missing_hole_ids) > 0:
        raise ValueError(
            f"Group '{group}' contains HOLE_IDs that don't occur in the AGS 3 HOLE group:\n{missing_hole_ids}"
        )

    return True


def check_ags3_sample_ids_exists(
    ags3_sample: pd.DataFrame, ags3_group_with_sample_id: pd.DataFrame
) -> bool:
    """
    Checks if the sample_id in an AGS 3 group exists in the AGS 3 SAMP group.

    Args:
        ags3_sample (pd.DataFrame): The DataFrame with the AGS 3 SAMP group.
        ags3_group_with_sample_id (pd.DataFrame): The DataFrame with the group containing sample_id.

    Raises:
        ValueError: If the group contains sample_id that don't occur in the AGS 3 SAMP group.

    Returns:
        bool: Returns True if the sample_id in the group exist in the AGS 3 SAMP group.
    """
    # Get the name of the group
    group = ags3_group_with_sample_id.columns[-2].split("_")[0]

    # Get the sample_id that are missing in the SAMP group
    missing_sample_ids = ags3_group_with_sample_id[
        ~ags3_group_with_sample_id["sample_id"].isin(ags3_sample["sample_id"])
    ]

    # Raise an error if there are missing sample_id
    if len(missing_sample_ids) > 0:
        raise ValueError(
            f"Group '{group}' contains samples that don't occur in the AGS 3 SAMP group:\n{missing_sample_ids}"
        )

    return True
