import math
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from tqdm import tqdm


def get_engine():
    connection_url = URL.create(
        "mssql+pyodbc",
        host=".",
        database="HR_Analytics",
        query={
            "driver": "ODBC Driver 17 for SQL Server",
            "trusted_connection": "yes",
        },
    )

    return create_engine(connection_url)

def save_to_sql(
    df: pd.DataFrame,
    table_name: str,
    engine,
    chunk_size: int = 1000,
    if_exists: str = "append"
) -> None:
    """
    Save DataFrame to SQL Server in chunks with progress bar.
    
    Args:
        df: DataFrame to save
        table_name: Target table name in database
        engine: SQLAlchemy engine
        chunk_size: Number of rows per chunk (default: 1000)
        if_exists: How to behave if table exists ('replace', 'append')
    """
    if len(df) == 0:
        print(f"  [WARNING] {table_name}: No data to save")
        return
    
    total_chunks = math.ceil(len(df) / chunk_size)
    
    for i in tqdm(range(total_chunks), desc=f"  Loading {table_name}"):
        chunk = df.iloc[i * chunk_size:(i + 1) * chunk_size]
        
        chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists if i == 0 else "append",
            index=False,
        )
    
    print(f"  ✓ {table_name}: Saved {len(df):,} records")


def load_from_sql(table_name: str, engine) -> pd.DataFrame:
    """
    Load data from SQL Server table.
    
    Args:
        table_name: Table name to query
        engine: SQLAlchemy engine
    
    Returns:
        DataFrame with table data
    """
    query = f"SELECT * FROM {table_name}"
    return pd.read_sql(query, engine)

def clear_table(table_name, engine):
    with engine.begin() as conn:
        conn.execute(
            text(f"DELETE FROM {table_name}")
        )

def map_keys(
    fact: pd.DataFrame,
    dim_employee: pd.DataFrame,
    dim_store: pd.DataFrame,
    dim_date: pd.DataFrame,
) -> pd.DataFrame:
    """
    Map business keys to surrogate keys in fact table.
    
    Merges fact table with dimension tables to get surrogate keys:
    - employee_id → employee_sk (if available, else keep employee_id)
    - store_id → store_sk (if available, else keep store_id)
    - year_month → date_key
    
    Args:
        fact: Fact table with business keys
        dim_employee: Employee dimension
        dim_store: Store dimension
        dim_date: Date dimension
    
    Returns:
        Fact table with surrogate/natural keys
    """
    # Merge with dim_store (store_id → store_sk or keep store_id)
    store_cols = ["store_id"]
    if "store_sk" in dim_store.columns:
        store_cols.append("store_sk")
    
    fact = fact.merge(
        dim_store[store_cols],
        on="store_id",
        how="left"
    )
    
    # Merge with dim_employee (employee_id → employee_sk or keep employee_id)
    employee_cols = ["employee_id"]
    if "employee_sk" in dim_employee.columns:
        employee_cols.append("employee_sk")
    
    fact = fact.merge(
        dim_employee[employee_cols],
        on="employee_id",
        how="left"
    )
    
    # Merge with dim_date (year_month → date_key)
    fact["year_month"] = fact["year_month"].astype(str)
    dim_date["year_month"] = dim_date["year_month"].astype(str)

    fact = fact.merge(
        dim_date[["year_month", "date_key"]],
        on="year_month",
        how="left"
    )
    
    return fact