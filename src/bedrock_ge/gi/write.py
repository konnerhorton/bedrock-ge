from pathlib import Path
from typing import Dict, Union

import geopandas as gpd
import pandas as pd


def write_gi_db_to_gpkg(
    brgi_db: Dict[str, gpd.GeoDataFrame],
    gpkg_path: Union[str, Path],
) -> None:
    """Writes a database with Bedrock Ground Investigation data to a GeoPackage file.

    Writes a dictionary of DataFrames containing Bedrock Ground Investigation data to a
    [GeoPackage file](https://www.geopackage.org/). Each DataFrame will be saved in a
    separate table named by the keys of the dictionary.

    Args:
        brgi_db (dict): A dictionary where keys are brgi table names and values are DataFrames
            with brgi data.
        gpkg_path (str): The name of the output GeoPackage file.

    Returns:
        None
    """
    # Create a GeoDataFrame from the dictionary of DataFrames
    for sheet_name, brgi_table in brgi_db.items():
        sanitized_table_name = sanitize_table_name(sheet_name)

        if isinstance(brgi_table, pd.DataFrame):
            brgi_table = gpd.GeoDataFrame(brgi_table)

        if isinstance(brgi_table, gpd.GeoDataFrame):
            brgi_table.to_file(
                gpkg_path, driver="GPKG", layer=sanitized_table_name, overwrite=True
            )

    print(f"Ground Investigation data has been written to '{gpkg_path}'.")


def write_gi_db_to_excel(
    gi_db: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]],
    excel_path: Union[str, Path],
) -> None:
    """Writes a database with Ground Investigation data to an Excel file.

    Each DataFrame in the database dictionary will be saved in a separate Excel sheet named
    after the dictionary keys. This function can be used on any GI database, whether in
    AGS, Bedrock, or another format.

    Args:
        gi_dfs (dict): A dictionary where keys are GI table names and values are DataFrames with GI data.
        excel_path (str): The name of the output Excel file.

    Returns:
        None
    """
    # Create an Excel writer object
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        for sheet_name, df in gi_db.items():
            sanitized_sheet_name = sanitize_table_name(sheet_name)
            if isinstance(df, pd.DataFrame) or isinstance(df, gpd.GeoDataFrame):
                df.to_excel(writer, sheet_name=sanitized_sheet_name, index=False)

    print(f"Ground Investigation data has been written to '{excel_path}'.")


# TODO: Make the 31 character table name length truncation a separate function. Only necessary for Excel.
def sanitize_table_name(sheet_name):
    """Replaces invalid characters and spaces in GI table names with underscores and truncates to 31 characters.

    Makes table names consistent with SQL, GeoPackage and Excel naming conventions by
    replacing invalid characters and spaces with underscores.

    Args:
        sheet_name (str): The original sheet name.

    Returns:
        sanitized_name: A sanitized sheet name with invalid characters and spaces replaced.
    """
    # Trim to a maximum length of 31 characters
    trimmed_name = sheet_name.strip()[:31]

    # Define invalid characters and replace with underscores
    invalid_chars = [":", "/", "\\", "?", "*", "[", "]"]
    sanitized_name = trimmed_name
    for char in invalid_chars:
        sanitized_name = sanitized_name.replace(char, "_")

    # Replace spaces with underscores
    sanitized_name = sanitized_name.replace(" ", "_")

    # Collapse multiple underscores to one
    sanitized_name = "_".join(filter(None, sanitized_name.split("_")))

    if trimmed_name != sanitized_name:
        print(
            f"Table names shouldn't contain {invalid_chars} or spaces and shouldn't be longer than 31 characters.\n",
            f"Replaced '{sheet_name}' with '{sanitized_name}'.",
        )

    # Ensure name isn't empty after sanitization
    # ! "Table1" doesn't make a lot of sense?!? It could be that there are more than 1 table without a name...
    if not sanitized_name:
        sanitized_name = "Table1"
        print("The table name was completely invalid or empty. Replaced with 'Table1'.")

    return sanitized_name
