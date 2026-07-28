import pandas as pd
from pathlib import Path
from scripts.etl.utils import normalize_columns

FILES= {
    'employees.csv': 'employees',
    'stores.csv': 'stores',
    'monthly_performance.csv': 'monthly_performance',
    'role_kpis.csv': 'role_kpis',
    'business_outcomes.csv': 'business_outcomes',
}

BASE_PATH = Path.cwd()
RAW_DATA_PATH = BASE_PATH / 'data' / 'raw'

def extract() -> dict:
    """
    Extract raw data from CSV files and normalize column names.
    Returns:
        dict: Dictionary with dataset names as keys and DataFrames as values
    """
    datasets = {}
    print("[Extract Phase] Loading raw data...")
    for file, name in FILES.items():
        file_path = RAW_DATA_PATH / file
        if not file_path.exists():
            raise FileNotFoundError(f"Raw data file not found: {file_path}")
        df = pd.read_csv(file_path, decimal = ",")
        df = normalize_columns(df)
        datasets[name] = df
        print(f"Extracted {name}: {len(df):,} rows, {len(df.columns)} columns")
    return datasets
