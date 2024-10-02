import warnings
from typing import Dict, Union

import pandas as pd


def ags_to_dfs(ags_data: str) -> Dict[str, Union[int, pd.DataFrame]]:
    """
    Convert AGS 3 or AGS 4 data to a dictionary of pandas DataFrames.

    Args:
        ags_data (str): The AGS data as a string.

    Raises:
        ValueError: If the data does not match AGS 3 or AGS 4 format.

    Returns:
        Dict[str, Union[int, pd.DataFrame]]: A dictionary where 'ags_version' indicates the version
        of AGS (3 or 4), and other keys represent group names with corresponding DataFrames.
    """
    # Process each line to find the AGS version and delegate parsing
    for line in ags_data.splitlines():
        stripped_line = line.strip()  # Remove leading/trailing whitespace
        if stripped_line:  # Skip empty lines at the start of the file
            if stripped_line.startswith("**"):
                # AGS version 3 data
                ags3_dfs = ags3_to_dfs(ags_data)
                return {"ags_version": 3, **ags3_dfs}
            elif stripped_line.startswith("GROUP"):
                # AGS version 4 data
                ags4_dfs = ags4_to_dfs(ags_data)
                return {"ags_version": 4, **ags4_dfs}
            else:
                # If first non-empty line doesn't match AGS 3 or AGS 4 format
                raise ValueError("The data provided is not valid AGS 3 or AGS 4 data.")

    raise ValueError(f"The string provided ({ags_data}) is empty.")


def ags3_to_dfs(ags3_data: str) -> Dict[str, pd.DataFrame]:
    """Convert AGS 3 data to a dictionary of pandas DataFrames.

    Args:
        ags_data (str): The AGS 3 data as a string.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary of pandas DataFrames, where each key represents a group name from AGS 3 data,
        and the corresponding value is a pandas DataFrame containing the data for that group.
    """

    ags3_dfs = {}
    group = ""
    headers = ["", "", ""]
    data_rows = [["", "", ""], ["", "", ""], ["", "", ""]]

    for i, line in enumerate(ags3_data.splitlines()):
        # In AGS 3.1 group names are prefixed with **
        if line.startswith('"**'):
            if group:
                ags3_dfs[group] = pd.DataFrame(data_rows, columns=headers)

            group = line.strip(' "*')
            data_rows = []

        # In AGS 3 header names are prefixed with "*
        elif line.startswith('"*'):
            new_headers = line.split('","')
            new_headers = [h.strip(' "*') for h in new_headers]

            # Some groups have so many headers that they span multiple lines.
            #
            # new_headers[-2] is used because:
            #   1. the first columns in AGS tables are mostly foreign keys
            #   2. the last column in AGS table is often FILE_FSET
            if new_headers[-2].split("_")[0] == headers[-2].split("_")[0]:
                headers = headers + new_headers
            else:
                headers = new_headers

        # Skip lines where group units are defined, these are defined in the AGS 3 data dictionary.
        elif line.startswith('"<UNITS>"'):
            continue

        # The rest of the lines contain data, "<CONT>" lines, or are worthless
        else:
            data_row = line.split('","')
            if len("".join(data_row)) == 0:
                print(f"No data was found on line {i}. Last Group: {group}")
                continue
            elif len(data_row) != len(headers):
                warnings.warn(
                    f"The number of columns on line {i} doesn't match the number of columns of group {group}"
                )
                continue
            # Append continued lines (<CONT>) to the last data_row
            elif data_row[0] == '"<CONT>':
                data_row = [d.strip(' "') for d in data_row]
                last_data_row = data_rows[-1]
                for j, datum in enumerate(data_row):
                    if datum and datum != "<CONT>":
                        last_data_row[j] += datum
            else:
                data_row = [d.strip(' "') for d in data_row]
                data_rows.append(data_row)

    # Also add the last group's df to the dictionary of AGS dfs
    ags3_dfs[group] = pd.DataFrame(data_rows, columns=headers)

    if not group:
        warnings.warn("The provided AGS 3 data does not contain any groups.")

    return ags3_dfs


def ags4_to_dfs(ags4_data: str) -> Dict[str, pd.DataFrame]:
    """Convert AGS 4 data to a dictionary of pandas DataFrames.

    Args:
        ags_data (str): The AGS 4 data as a string.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary of pandas DataFrames, where each key represents a group name from AGS 4 data,
        and the corresponding value is a pandas DataFrame containing the data for that group.
    """
    # ! THIS IS DUMMY CODE !
    # TODO: IMPLEMENT AGS 4
    ags4_dfs = {
        "PROJ": pd.DataFrame(),
        "LOCA": pd.DataFrame(),
        "SAMP": pd.DataFrame(),
    }

    return ags4_dfs
