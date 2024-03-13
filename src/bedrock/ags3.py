from typing import Dict
import pandas as pd


def ags3_to_dfs(ags_data: str) -> Dict[str, pd.DataFrame]:
    """Convert AGS 3 data to a dictionary of pandas DataFrames.

    Args:
        ags_data (str): The AGS 3 data as a string.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary of pandas DataFrames, where each key represents a group name from AGS 3 data,
        and the corresponding value is a DataFrame containing the data for that group.
    """
    ags_dfs = {}
    group = None
    headers = ["", "", ""]
    data_rows = [["", "", ""], ["", "", ""], ["", "", ""]]

    for i, line in enumerate(ags_data.split("\n")):
        # In AGS 3.1 group names are prefixed with **
        if line.startswith('"**'):
            if group:
                ags_dfs[group] = pd.DataFrame(data_rows, columns=headers)

            group = line.strip(' "*')
            data_rows = []

        # In AGS 3.1 header names are prefixed with *
        elif line.startswith('"*'):
            new_headers = line.split('","')
            new_headers = [h.strip(' "*') for h in new_headers]

            # Some groups have headers that span multiple lines
            # new_headers[-2] is used because:
            #   1. the first columns in AGS tables are mostly foreign keys
            #   2. the last column in AGS table is often FILE_FSET
            if new_headers[-2].split("_")[0] == headers[-2].split("_")[0]:
                headers = headers + new_headers
            else:
                headers = new_headers

        # Skip lines where group units are defined, these are defined in the AGS 3.1 data dictionary
        elif line.startswith('"<UNITS>"'):
            continue

        # The rest of the lines contain data, "<CONT>" lines, or are worthless
        else:
            data_row = line.split('","')
            if len("".join(data_row)) == 0:
                print(f"No data was found on line {i}. Last Group: {group}")
                continue
            elif len(data_row) != len(headers):
                # TODO: This should be a warning
                print(
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
    ags_dfs[group] = pd.DataFrame(data_rows, columns=headers)

    return ags_dfs
