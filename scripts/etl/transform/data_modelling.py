import pandas as pd
from pathlib import Path

BASE_PATH = Path.cwd()
DATA_PATH = BASE_PATH / "data" / "processed"

# ============================ DIMENSION TABLES ============================
def build_dim_employee(employees: pd.DataFrame) -> pd.DataFrame:
    """
    Build employee dimension table.
    """

    dim = (
        employees[
            [
                "employee_id",
                "full_name",
                "education_level",
                "hire_date",
                "exit_date",
                "manager_id",
                "department",
                "job_role",
                "job_level",
                "employment_type",
            ]
        ]
        .drop_duplicates(subset="employee_id")
        .reset_index(drop=True)
    )

    return dim

def build_dim_store(stores: pd.DataFrame) -> pd.DataFrame:
    """
    Build store dimension table.
    Args:
        stores: Store DataFrame from staging
    Returns:
        Store dimension
    """
    dim = (
        stores[
            [
                "store_id",
                "store_name",
                "city",
                "city_latitude",
                "city_longitude",
                "store_type",
                "opening_date",
            ]
        ]
        .drop_duplicates(subset="store_id")
        .reset_index(drop=True)
    )

    return dim


def build_dim_date(monthly_performance: pd.DataFrame) -> pd.DataFrame:
    """
    Create date dimension from monthly dates.
    """

    months = (
        monthly_performance["year_month"]
        .drop_duplicates()
        .sort_values()
    )

    dim = pd.DataFrame({"year_month": months})

    dim["date_key"] = dim["year_month"].dt.strftime("%Y%m").astype(int)
    dim["year"] = dim["year_month"].dt.year
    dim["month"] = dim["year_month"].dt.month
    dim["month_name"] = dim["year_month"].dt.strftime("%B")
    dim["quarter"] = dim["year_month"].dt.quarter
    dim["year_month_label"] = dim["year_month"].dt.strftime("%Y-%m")

    return dim[
        [
            "date_key",
            "year_month",
            "year",
            "month",
            "month_name",
            "quarter",
            "year_month_label",
        ]
    ].reset_index(drop=True)

# ============================ FACT TABLE ============================

def build_fact_employee_monthly(
    monthly_performance: pd.DataFrame,
    employees: pd.DataFrame,
) -> pd.DataFrame:
    """
    Grain:
        employee × month
    """

    employee_cols = [
        "employee_id",
        "store_id",
        "base_salary_annual",
        "tenure_months",
        "is_active",
        "age"
    ]

    fact = monthly_performance.merge(
        employees[employee_cols],
        on="employee_id",
        how="left",
    )

    return fact[
        [
            "employee_id",
            "store_id",
            "year_month",
            "base_salary_annual",
            "tenure_months",
            "age",
            "is_active",
            "performance_rating",
            "training_hours",
            "overtime_hours",
            "absenteeism_days",
            "promotion_flag",
            "salary_increase_flag",
            "monthly_bonus",
            "benefits_cost",
            "employee_satisfaction",
            "engagement_index",
            "manager_evaluation",
        ]
    ].reset_index(drop=True)


def build_fact_business_outcomes(
    business_outcomes: pd.DataFrame,
) -> pd.DataFrame:
    """
    Grain:
        store × month
    """

    return (
        business_outcomes[
            [
                "store_id",
                "year_month",
                "sales_target",
                "sales_actual",
                "sales_achievement_pct",
                "customer_satisfaction",
                "nps_score",
                "waste_percentage",
                "on_time_delivery",
            ]
        ]
        .reset_index(drop=True)
    )