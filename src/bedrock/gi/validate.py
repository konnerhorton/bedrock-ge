from typing import Dict, Union

import geopandas as gpd
import pandas as pd

from bedrock.gi.schemas import (
    BaseInSitu,
    BaseLocation,
    BaseSample,
    InSitu,
    Location,
    Project,
    Sample,
)


def check_brgi_database(brgi_db: Dict):
    for table_name, table in brgi_db.items():
        if table_name == "Project":
            Project.validate(table)
        elif table_name == "Location":
            Location.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
        elif table_name == "Sample":
            Sample.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
            check_foreign_key("location_uid", brgi_db["Location"], table)
        elif table_name == "InSitu":
            InSitu.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
            check_foreign_key("location_uid", brgi_db["Location"], table)

    return True


def check_brgi_base_database(brgi_db: Dict):
    for table_name, table in brgi_db.items():
        if table_name == "Project":
            Project.validate(table)
        elif table_name == "Location":
            BaseLocation.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
        elif table_name == "Sample":
            BaseSample.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
            check_foreign_key("location_uid", brgi_db["Location"], table)
        elif table_name == "InSitu":
            BaseInSitu.validate(table)
            check_foreign_key("project_uid", brgi_db["Project"], table)
            check_foreign_key("location_uid", brgi_db["Location"], table)

    return True


def check_foreign_key(
    foreign_key: str,
    parent_table: Union[pd.DataFrame, gpd.GeoDataFrame],
    table_with_foreign_key: Union[pd.DataFrame, gpd.GeoDataFrame],
) -> bool:
    """
    Checks if a foreign key in a table exists in the parent table.

    Foreign keys describe the relationship between tables in a relational database.
    For example, all GI Locations belong to a project.
    All GI Locations are related to a project with the project_uid (Project Unique IDentifier).
    The project_uid is the foreign key in the Location table.
    This implies that the project_uid in the foreign key in the Location table must exist in the Project parent table.
    That is what this function checks.

    Args:
        foreign_key (str): The name of the column of the foreign key.
        parent_table (Union[pd.DataFrame, gpd.GeoDataFrame]): The parent table.
        table_with_foreign_key (Union[pd.DataFrame, gpd.GeoDataFrame]): The table with the foreign key.

    Raises:
        ValueError: If the table with the foreign key contains foreign keys that don't occur in the parent table.

    Returns:
        bool: True if the foreign keys all exist in the parent table.
    """
    # Get the foreign keys that are missing in the parent group
    missing_foreign_keys = table_with_foreign_key[
        ~table_with_foreign_key[foreign_key].isin(parent_table[foreign_key])
    ]

    # Raise an error if there are missing foreign keys
    if len(missing_foreign_keys) > 0:
        raise ValueError(
            f"The table with the foreign key contains foreign keys that don't occur in the parent table:\n{missing_foreign_keys}"
        )

    return True
