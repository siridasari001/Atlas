import pandas as pd

from app.models.metadata import ColumnProfile, DatasetProfile


def profile_dataset(df: pd.DataFrame) -> DatasetProfile:
    """
    Generate structured metadata about a dataset.

    Args:
        df: Pandas DataFrame to profile.

    Returns:
        A validated DatasetProfile object.
    """

    columns = []

    for column in df.columns:
        column_profile = ColumnProfile(
            name=column,
            data_type=str(df[column].dtype),
            missing_count=int(df[column].isna().sum()),
            unique_count=int(df[column].nunique()),
        )

        columns.append(column_profile)

    return DatasetProfile(
        row_count=len(df),
        column_count=len(df.columns),
        columns=columns,
    )