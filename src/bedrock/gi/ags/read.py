from typing import Dict, List, Optional

import pandas as pd

from bedrock.gi.ags.validate import check_ags_proj_group


def ags_to_dfs(ags_data: str) -> Dict[str, pd.DataFrame]:
    """
    Convert AGS 3 or AGS 4 data to a dictionary of pandas DataFrames.

    Args:
        ags_data (str): The AGS data as a string.

    Raises:
        ValueError: If the data does not match AGS 3 or AGS 4 format.

    Returns:
        Dict[str, pd.DataFrame]]: A dictionary where keys represent AGS group
        names with corresponding DataFrames for the corresponding group data.
    """
    # Process each line to find the AGS version and delegate parsing
    for line in ags_data.splitlines():
        stripped_line = line.strip()  # Remove leading/trailing whitespace
        if stripped_line:  # Skip empty lines at the start of the file
            if stripped_line.startswith('"**'):
                ags_version = 3
                ags_dfs = ags3_to_dfs(ags_data)
                break
            elif stripped_line.startswith('"GROUP"'):
                ags_version = 4
                ags_dfs = ags4_to_dfs(ags_data)
                break
            else:
                # If first non-empty line doesn't match AGS 3 or AGS 4 format
                raise ValueError("The data provided is not valid AGS 3 or AGS 4 data.")

    is_proj_group_correct = check_ags_proj_group(ags_dfs["PROJ"])
    if is_proj_group_correct:
        project_id = ags_dfs["PROJ"]["PROJ_ID"].iloc[0]
        print(f"AGS {ags_version} data was read for Project {project_id}")
        print("This Ground Investigation data contains groups:")
        print(list(ags_dfs.keys()), "\n")

    return ags_dfs


def ags3_to_dfs(ags3_data: str) -> Dict[str, pd.DataFrame]:
    """Convert AGS 3 data to a dictionary of pandas DataFrames.

    Args:
        ags_data (str): The AGS 3 data as a string.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary of pandas DataFrames, where each key represents a group name from AGS 3 data,
        and the corresponding value is a pandas DataFrame containing the data for that group.
    """

    # Initialize dictionary and variables used in the AGS 3 read loop
    ags3_dfs = {}
    group = ""
    headers: List[str] = ["", "", ""]
    group_data: List[List[Optional[str]]] = [[], [], []]

    for i, line in enumerate(ags3_data.splitlines()):
        # In AGS 3.1 group names are prefixed with **
        if line.startswith('"**'):
            if group:
                ags3_dfs[group] = pd.DataFrame(group_data, columns=headers)

            group = line.strip(' "*')
            group_data = []

        # In AGS 3 header names are prefixed with "*
        elif line.startswith('"*'):
            new_headers = line.split('","')
            new_headers = [h.strip(' "*') for h in new_headers]

            # Some groups have so many headers that they span multiple lines.
            # Therefore we need to check whether the new headers are a continuation of the previous headers.
            # new_headers[-2] (the second to last header) is used because:
            #   1. the first columns in AGS 3 tables are mostly foreign keys
            #   2. the last column in AGS table is often FILE_FSET
            if new_headers[-2].split("_")[0] == headers[-2].split("_")[0]:
                headers = headers + new_headers
            else:
                headers = new_headers

        # Skip lines where group units are defined, these are defined in the AGS 3 data dictionary.
        elif line.startswith('"<UNITS>"'):
            continue

        # The rest of the lines contain:
        # 1. GI data
        # 2. a continuation of the previous line. These lines contain "<CONT>" in the first column.
        # 3. are empty or contain worthless data
        else:
            data_row = line.split('","')
            if len("".join(data_row)) == 0:
                # print(f"Line {i} is empty. Last Group: {group}")
                continue
            elif len(data_row) != len(headers):
                print(
                    f"\nCAUTION: The number of columns on line {i} doesn't match the number of columns of group {group}!\n"
                )
                continue
            # Append continued lines (<CONT>) to the last data_row
            elif data_row[0] == '"<CONT>':
                last_data_row = group_data[-1]
                for j, data in enumerate(data_row):
                    data = data.strip(' "')
                    if data and data != "<CONT>":
                        # Last data row didn't contain data for this column
                        if last_data_row[j] is None:
                            last_data_row[j] = data
                        else:
                            last_data_row[j] = str(last_data_row[j]) + data
            # Lines that are assumed to contain valid data are added to the group data
            else:
                cleaned_data_row = []
                for data in data_row:
                    cleaned_data_row.append(data.strip(' "') or None)
                group_data.append(cleaned_data_row)

    # Also add the last group's df to the dictionary of AGS dfs
    ags3_dfs[group] = pd.DataFrame(group_data, columns=headers)

    if not group:
        print(
            'ERROR: The provided AGS 3 data does not contain any groups, i.e. lines starting with "**'
        )

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
