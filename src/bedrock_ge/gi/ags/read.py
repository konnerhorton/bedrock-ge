import io
from typing import Any, Dict, List, Union

import pandas as pd
from python_ags4 import AGS4

from bedrock_ge.gi.ags.validate import check_ags_proj_group


def ags_to_dfs(ags_data: str) -> Dict[str, pd.DataFrame]:
    """Converts AGS 3 or AGS 4 data to a dictionary of pandas DataFrames.

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
        print(
            f"AGS {ags_version} data was read for Project {project_id}",
            "This Ground Investigation data contains groups:",
            list(ags_dfs.keys()),
            sep="\n",
            end="\n\n",
        )

    return ags_dfs


def ags3_to_dfs(ags3_data: str) -> Dict[str, pd.DataFrame]:
    """Converts AGS 3 data to a dictionary of pandas DataFrames.

    Args:
        ags3_data (str): The AGS 3 data as a string.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary of pandas DataFrames, where each key represents a group name from AGS 3 data,
        and the corresponding value is a pandas DataFrame containing the data for that group.
    """
    # Initialize dictionary and variables used in the AGS 3 read loop
    ags3_dfs = {}
    line_type = "line_0"
    group = ""
    headers: List[str] = ["", "", ""]
    group_data: List[List[Any]] = [[], [], []]

    for i, line in enumerate(ags3_data.splitlines()):
        last_line_type = line_type

        # In AGS 3.1 group names are prefixed with **
        if line.startswith('"**'):
            line_type = "group_name"
            if group:
                ags3_dfs[group] = pd.DataFrame(group_data, columns=headers)

            group = line.strip(' ,"*')
            group_data = []

        # In AGS 3 header names are prefixed with "*
        elif line.startswith('"*'):
            line_type = "headers"
            new_headers = line.split('","')
            new_headers = [h.strip(' ,"*') for h in new_headers]

            # Some groups have so many headers that they span multiple lines.
            # Therefore we need to check whether the new headers are
            # a continuation of the previous headers from the last line.
            if line_type == last_line_type:
                headers = headers + new_headers
            else:
                headers = new_headers

        # Skip lines where group units are defined, these are defined in the AGS 3 data dictionary.
        elif line.startswith('"<UNITS>"'):
            line_type = "units"
            continue

        # The rest of the lines contain:
        # 1. GI data
        # 2. a continuation of the previous line. These lines contain "<CONT>" in the first column.
        # 3. are empty or contain worthless data
        else:
            line_type = "data_row"
            data_row = line.split('","')
            if len("".join(data_row)) == 0:
                # print(f"Line {i} is empty. Last Group: {group}")
                continue
            elif len(data_row) != len(headers):
                print(
                    f"\n🚨 CAUTION: The number of columns on line {i + 1} ({len(data_row)}) doesn't match the number of columns of group {group} ({len(headers)})!",
                    f"{group} headers: {headers}",
                    f"Line {i + 1}:      {data_row}",
                    sep="\n",
                    end="\n\n",
                )
                continue
            # Append continued lines (<CONT>) to the last data_row
            elif data_row[0] == '"<CONT>':
                last_data_row = group_data[-1]
                for j, data in enumerate(data_row):
                    data = data.strip(' "')
                    if data and data != "<CONT>":
                        if last_data_row[j] is None:
                            # Last data row didn't contain data for this column
                            last_data_row[j] = coerce_string(data)
                        else:
                            # Last data row already contains data for this column
                            last_data_row[j] = str(last_data_row[j]) + data
            # Lines that are assumed to contain valid data are added to the group data
            else:
                cleaned_data_row = []
                for data in data_row:
                    cleaned_data_row.append(coerce_string(data.strip(' "')))
                group_data.append(cleaned_data_row)

    # Also add the last group's df to the dictionary of AGS dfs
    ags3_dfs[group] = pd.DataFrame(group_data, columns=headers).dropna(
        axis=1, how="all"
    )

    if not group:
        print(
            '🚨 ERROR: The provided AGS 3 data does not contain any groups, i.e. lines starting with "**'
        )

    return ags3_dfs


def ags4_to_dfs(ags4_data: str) -> Dict[str, pd.DataFrame]:
    """Converts AGS 4 data to a dictionary of pandas DataFrames.

    Args:
        ags4_data (str): The AGS 4 data as a string.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary of pandas DataFrames, where each key represents a group name from AGS 4 data,
        and the corresponding value is a pandas DataFrame containing the data for that group.
    """
    # AGS4.AGS4_to_dataframe accepts the file, not the data string
    ags4_file = io.StringIO(ags4_data)

    ags4_tups = AGS4.AGS4_to_dataframe(ags4_file)

    ags4_dfs = {}
    for group, df in ags4_tups[0].items():
        df = df.loc[2:].drop(columns=["HEADING"]).reset_index(drop=True)
        ags4_dfs[group] = df

    return ags4_dfs


def coerce_string(string: str) -> Union[None, bool, float, str]:
    if string.lower() in {"none", "null", ""}:
        return None
    elif string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        try:
            value = float(string)
            if value.is_integer():
                return int(value)
            else:
                return value
        except ValueError:
            return string
