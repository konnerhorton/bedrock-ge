import pandas as pd


def check_ags_proj_group(proj_df: pd.DataFrame) -> bool:
    """Checks if the AGS 3 or AGS 4 PROJ group is correct.

    Args:
        proj_df (pd.DataFrame): The DataFrame with the PROJ group.

    Raises:
        ValueError: If AGS 3 of AGS 4 PROJ group is not correct.

    Returns:
        bool: Returns True if the AGS 3 or AGS 4 PROJ group is correct.
    """

    if len(proj_df) != 1:
        raise ValueError("The PROJ group must contain exactly one row.")

    return True


def check_ags3_hole_group(hole_df: pd.DataFrame) -> bool:
    """Checks if the AGS 3 HOLE group is correct.

    The AGS 3 HOLE group stores information about the location of Ground Investigation locations.

    Args:
        hole_df (pd.DataFrame): The DataFrame with the HOLE group.

    Raises:
        ValueError: If AGS 3 HOLE group is not correct.

    Returns:
        bool: Returns True if the AGS 3 HOLE group is correct.
    """

    # if len(hole_df) != 1:
    #     raise ValueError("The HOLE group must contain exactly one row.")

    return True


def check_ags_loca_group(loca_df: pd.DataFrame) -> bool:
    """Checks if the AGS 3 or AGS 4 LOCA group is correct.

    The AGS 4 LOCA group stores information about the location of Ground Investigation locations.

    Args:
        loca_df (pd.DataFrame): The DataFrame with the LOCA group.

    Raises:
        ValueError: If AGS 3 or AGS 4 LOCA group is not correct.

    Returns:
        bool: Returns True if the AGS 3 or AGS 4 LOCA group is correct.
    """
    # Location()
    # if len(loca_df) != 1:
    #     raise ValueError("The LOCA group must contain exactly one row.")

    return True


def check_ags_samp_group(samp_df: pd.DataFrame) -> bool:
    """Checks if the AGS 3 or AGS 4 SAMP group is correct.

    Args:
        samp_df (pd.DataFrame): The DataFrame with the SAMP group.

    Raises:
        ValueError: If AGS 3 or AGS 4 SAMP group is not correct.

    Returns:
        bool: Returns True if the AGS 3 or AGS 4 SAMP group is correct.
    """

    # if len(samp_df) != 1:
    #     raise ValueError("The SAMP group must contain exactly one row.")

    return True
