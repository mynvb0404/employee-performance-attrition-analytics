import pandas as pd
from pathlib import Path 

BASE_PATH = Path.cwd()
PROCESSED_DATA_PATH = BASE_PATH / 'data' / 'processed'

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names: lowercase, remove spaces, strip underscores.
    """
    df = df.copy()
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r"[^\w]+", "_", regex=True)
          .str.strip("_")
    )
    return df

def format_dmy(series: pd.Series) -> pd.Series:
    """
    Convert series from DD/MM/YYYY to datetime.
    """
    return pd.to_datetime(series, format='%d/%m/%Y', errors='coerce')

def format_ym(series: pd.Series) -> pd.Series:
    """
    Convert series from YYYY-MM to datetime.
    """
    return pd.to_datetime(series, format='%Y-%m', errors='coerce')

def write_staging(df: pd.DataFrame, name: str) -> None:
    """
    Write transformed data to staging area (data/processed) to csv and parquet.
    Args:
        df: DataFrame to write
        name: Dataset name (used in file naming)
    """
    # Create directory if it doesn't exist
    PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)
    
    # Save to parquet and CSV
    parquet_path = PROCESSED_DATA_PATH / f'{name}.parquet'
    csv_path = PROCESSED_DATA_PATH / f'{name}.csv'
    
    df.to_parquet(parquet_path, index=False)
    df.to_csv(csv_path, index=False)
    
    print(f"Staged {name}: {len(df):,} rows -> data/processed/{name}.*")


