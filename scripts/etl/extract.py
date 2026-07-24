import pandas as pd
from pathlib import Path
from scripts.etl.utils import normalize_columns

FILE_NAME = {
    'employees.csv': 'employees',
    'stores.csv': 'stores',
    'monthly_performance.csv': 'monthly_performance',
    'role_kpis.csv': 'role_kpis',
    'business_outcomes.csv': 'business_outcomes',
}

BASE_PATH = Path.cwd()


def extract():
    datasets = {}
    for file, name in FILE_NAME.items():
        file_path = BASE_PATH / 'data' / 'raw' / file
        df = pd.read_csv(file_path)
        df = normalize_columns(df)
        datasets[name] = df
    return datasets
