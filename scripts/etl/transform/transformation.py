import pandas as pd
import numpy as np
from scripts.etl.utils import format_dmy, format_ym
import scripts.etl.transform.config as config
'''===================EMPLOYEES=================='''
def transform_employees(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['hire_date'] = format_dmy(df['hire_date'])
    df['exit_date'] = format_dmy(df['exit_date'])

    today = pd.Timestamp.today().normalize()
    df['is_active'] = df['exit_date'].isna()
    df['tenure_days'] = (df["exit_date"].fillna(today) - df["hire_date"]).dt.days
    
    start_dt = df['hire_date']
    end_dt = df['exit_date'].fillna(today)
    tenure_months = (end_dt.dt.year - start_dt.dt.year) * 12 + (end_dt.dt.month - start_dt.dt.month)
    df['tenure_months'] = np.where(end_dt.dt.day < start_dt.dt.day, tenure_months - 1, tenure_months)
    df['tenure_band'] = pd.cut(
        df['tenure_months'],
        bins= config.TENURE_BINS,
        labels= config.TENURE_LABELS,
        right=False,
        include_lowest=True
    ).astype(str)

    df["age_band"] = pd.cut(
        df['age'],
        bins= config.AGE_BINS,
        labels= config.AGE_LABELS,
        right=False,
    ).astype(str)
    return df

'''===================STORES=================='''
def transform_stores(df):
    df = df.copy()
    df['opening_date'] = format_dmy(df['opening_date'])
    return df

'''===================MONTHLY PERFORMANCE=================='''
def transform_monthly_performance(df):
    df = df.copy()
    df['year_month'] = format_ym(df['year_month'])
    df['year'] = df['year_month'].dt.year
    df['month'] = df['year_month'].dt.month
    df['promotion_flag'] = df['promotion_flag'].astype(bool)
    df['salary_increase_flag'] = df['salary_increase_flag'].astype(bool)
    return df

'''===================ROLE KPIS=================='''
def transform_role_kpis(df):
    df = df.copy()
    df['year_month'] = format_ym(df['year_month'])
    df['year'] = df['year_month'].dt.year
    df['month'] = df['year_month'].dt.month
    return df

'''===================BUSINESS OUTCOMES=================='''
def transform_business_outcomes(df):
    df = df.copy()
    df['year_month'] = format_ym(df['year_month'])
    df['year'] = df['year_month'].dt.year
    df['month'] = df['year_month'].dt.month
    
    df['sales_actual'] = pd.to_numeric(df['sales_actual'].astype(str).str.replace(',', '.'), errors='coerce')
    df['sales_target'] = pd.to_numeric(df['sales_target'].astype(str).str.replace(',', '.'), errors='coerce')
    df["sales_achievement_pct"] = (df["sales_actual"] / df["sales_target"] * 100).round(2)
    return df
