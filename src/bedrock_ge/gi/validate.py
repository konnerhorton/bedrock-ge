from typing import Dict, Union

import geopandas as gpd  # type: ignore
import pandas as pd

from bedrock_ge.gi.schemas import (
    BaseInSitu,
    BaseLocation,
    BaseSample,
    InSitu,
    Location,
    Project,
    Sample,
)


def check_brgi_database(brgi_db: Dict) -> bool:
    """Validates a Bedrock Geotechnical Engineering (BRGE) database against schema definitions.

    This function checks each table in the BRGE database to ensure it conforms to the
    expected schema and has valid foreign key relationships. It validates Project,
    Location, Sample, and InSitu tables, and provides feedback about Lab data tables
    which are not yet implemented.

    Args:
        brgi_db (Dict): A dictionary containing the BRGE database tables as DataFrames.

    Returns:
        bool: True if all tables pass validation.

    Raises:
        ValueError: If any table fails schema validation or has invalid foreign keys.
    """
    for table_name, table in brgi_db.items():
        if table_name == "Project":
            Project.validate(table)
            print("'Project' table aligns with Bedrock's 'Project' table schema.")
        elif table_name == "Location":
            Location.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
            print("'Location' table aligns with Bedrock's 'Location' table schema.")
        elif table_name == "Sample":
            Sample.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
            check_foreign_key("location_uid", brgi_db["Location"], table)
            print("'Sample' table aligns with Bedrock's 'Sample' table schema.")
        elif table_name == "InSitu":
            InSitu.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
            check_foreign_key("location_uid", brgi_db["Location"], table)
            print(
                f"'{table_name}' table aligns with Bedrock's table schema for In-Situ measurements."
            )
        elif table_name.startswith("Lab_"):
            print(
                "🚨 !NOT IMPLEMENTED! We haven't come across Lab data yet. !NOT IMPLEMENTED!"
            )

    return True


def check_no_gis_brgi_database(brgi_db: Dict) -> bool:
    """Validates a BRGE database without GIS geometry against schema definitions.

    Similar to check_brgi_database but validates tables without GIS geometry components.
    This is useful for validating data that doesn't include spatial information.

    Args:
        brgi_db (Dict): A dictionary containing the BRGE database tables as DataFrames.

    Returns:
        bool: True if all tables pass validation.

    Raises:
        ValueError: If any table fails schema validation or has invalid foreign keys.
    """
    for table_name, table in brgi_db.items():
        if table_name == "Project":
            Project.validate(table)
            print("'Project' table aligns with Bedrock's 'Project' table schema.")
        elif table_name == "Location":
            BaseLocation.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
            print(
                "'Location' table aligns with Bedrock's 'Location' table schema without GIS geometry."
            )
        elif table_name == "Sample":
            BaseSample.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
            check_foreign_key("location_uid", brgi_db["Location"], table)
            print(
                "'Sample' table aligns with Bedrock's 'Sample' table schema without GIS geometry."
            )
        elif table_name.startswith("InSitu_"):
            BaseInSitu.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
            check_foreign_key("location_uid", brgi_db["Location"], table)
            print(
                f"'{table_name}' table aligns with Bedrock's '{table_name}' table schema without GIS geometry."
            )
        elif table_name.startswith("Lab_"):
            print(
                "🚨 !NOT IMPLEMENTED! We haven't come across Lab data yet. !NOT IMPLEMENTED!"
            )

    return True


def check_foreign_key(
    foreign_key: str,
    parent_table: Union[pd.DataFrame, gpd.GeoDataFrame],
    table_with_foreign_key: Union[pd.DataFrame, gpd.GeoDataFrame],
) -> bool:
    """Validates foreign key relationships between tables.

    Ensures that all foreign key values in a child table exist in the parent table.
    This is crucial for maintaining referential integrity in the database.

    Args:
        foreign_key (str): The name of the foreign key column.
        parent_table (Union[pd.DataFrame, gpd.GeoDataFrame]): The parent table containing
            the primary keys.
        table_with_foreign_key (Union[pd.DataFrame, gpd.GeoDataFrame]): The child table
            containing the foreign keys.

    Returns:
        bool: True if all foreign keys are valid.

    Raises:
        ValueError: If any foreign key values in the child table don't exist in the
            parent table.
    """
    # Get the foreign keys that are missing in the parent group
    missing_foreign_keys = table_with_foreign_key[
        ~table_with_foreign_key[foreign_key].isin(parent_table[foreign_key])
    ]

    # Raise an error if there are missing foreign keys
    if len(missing_foreign_keys) > 0:
        raise ValueError(
            f"This table contains '{foreign_key}'s that don't occur in the parent table:\n{missing_foreign_keys}"
        )

    return True
