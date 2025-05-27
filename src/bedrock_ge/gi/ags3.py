from bedrock_ge.gi.brgi_db_mapping import BedrockGIDatabaseMapping


def ags3_to_dfs(ags3_data: str) -> BedrockGIDatabaseMapping:
    """Converts AGS 3 data to a dictionary of pandas DataFrames.

    Args:
        ags3_data (str): The AGS 3 data as a string.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary of pandas DataFrames, where each key
            represents a group name from AGS 3 data, and the corresponding value is a
            pandas DataFrame containing the data for that group.
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
