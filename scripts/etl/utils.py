import pandas as pd
from pathlib import Path 

BASE_PATH = Path.cwd()

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r"[^\w]+", "_", regex=True)
          .str.strip("_")
    )
    return df

def format_dmy(series: pd.Series):
    return pd.to_datetime(series, format='%d/%m/%Y', errors='coerce')

def format_ym(series: pd.Series):
    return pd.to_datetime(series, format='%Y-%m', errors='coerce')

def write_staging(df: pd.DataFrame, name: str):
    df.to_parquet(BASE_PATH / 'data' / 'processed' / f'{name}.parquet', index=False)
    df.to_csv(BASE_PATH / 'data' / 'processed' / f'{name}.csv', index=False)
    print(f"  [loading] {name}: {len(df):,} rows -> dataset/data/processed/{name}.*")


