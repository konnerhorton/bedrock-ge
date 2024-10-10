from pathlib import Path
from typing import Dict, Union

import pandas as pd


def write_gi_dfs_to_excel(
    gi_dfs: Dict[str, Union[str, int, pd.DataFrame]], excel_path: Union[str, Path]
) -> None:
    """
    Write a dictionary of DataFrames with Ground Investigation data to an Excel file.

    Each DataFrame will be saved in a separate sheet named after the keys of the dictionary.
    Function can be used on any dictionary of DataFrames, whether in AGS, Bedrock, or another format.

    Args:
        gi_dfs (dict): A dictionary where keys are GI table names and values are DataFrames with GI data.
        excel_path (str): The name of the output Excel file.

    Returns:
        None: This function does not return any value. It writes the DataFrames to an Excel file.
    """

    # Create an Excel writer object
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for sheet_name, df in gi_dfs.items():
            sanitized_sheet_name = sanitize_sheet_name(sheet_name)
            if isinstance(df, pd.DataFrame):
                df.to_excel(writer, sheet_name=sanitized_sheet_name, index=False)

    print(f"Ground Investigation data has been written to '{excel_path}'.")


def sanitize_sheet_name(sheet_name):
    """
    Replace invalid characters in Excel sheet names with an underscore.

    Args:
        sheet_name (str): The original sheet name.

    Returns:
        str: A sanitized sheet name with invalid characters replaced.
    """
    # Trim to a maximum length of 31 characters
    trimmed_name = sheet_name.strip()[:31]

    if trimmed_name != sheet_name:
        print(
            f"Excel sheet names cannot be longer than 31 characters. Replaced '{sheet_name}' with '{trimmed_name}'."
        )

    # Replace invalid characters with an underscore
    invalid_chars = [":", "/", "\\", "?", "*", "[", "]"]
    sanitized_name = trimmed_name
    for char in invalid_chars:
        sanitized_name = sanitized_name.replace(char, "_")

    if trimmed_name != sanitized_name:
        print(
            f"Excel sheet names cannot contain {invalid_chars}. Replaced '{sheet_name}' with '{sanitized_name}'"
        )

    return sanitized_name
