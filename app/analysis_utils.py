import pandas as pd

def sum_column(df: pd.DataFrame, column: str):
    if column not in df.columns:
        raise KeyError(f"Column {column} not found")
    return df[column].sum()

def mean_column(df: pd.DataFrame, column: str):
    if column not in df.columns:
        raise KeyError(f"Column {column} not found")
    return df[column].mean()
