import pandas as pd


def check_non_null(df: pd.DataFrame, column: str) -> bool:
    """Checks if any null values exist in the specified column.

    Args:
        df (pd.DataFrame): DataFrame to check.
        column (str): The name of the column to check.

    Raises:
        ValueError: If null values are found in the column.

    Returns:
        bool: Returns True if no null values are found.
    """

    if df[column].isnull().any():
        raise ValueError(f"All rows in column {column} must have a value.")

    return True


def check_unique_values(df: pd.DataFrame, column: str) -> bool:
    """Checks if all values are unique in the specified column.

    Args:
        df (pd.DataFrame): DataFrame to check.
        column (str): The name of the column to check for uniqueness.

    Raises:
        ValueError: If non-unique (duplicate) values are found in the column.

    Returns:
        bool: Returns True if all values are unique.
    """

    if df[column].duplicated().any():
        # Get the count of duplicates for debugging
        duplicate_count = df[column].duplicated().sum()
        raise ValueError(
            f'Column "{column}" contains {duplicate_count} duplicate values.'
        )

    return True
