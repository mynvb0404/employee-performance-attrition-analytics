import pandas as pd
from pathlib import Path

from scripts.etl.transform.data_modelling import (
    build_dim_employee,
    build_dim_store,
    build_dim_date,
    build_fact_employee_monthly,
    build_fact_business_outcomes,
)

from scripts.etl.config_sql import (
    get_engine,
    save_to_sql,
    load_from_sql,
    clear_table,
    map_keys
)

BASE_PATH = Path.cwd()
PROCESSED_DATA_PATH = BASE_PATH / "data" / "processed"


def load_staging_data() -> dict[str, pd.DataFrame]:
    """
    Load transformed data from processed parquet files.
    """

    files = {
        "employees": "employees.parquet",
        "stores": "stores.parquet",
        "monthly_performance": "monthly_performance.parquet",
        "business_outcomes": "business_outcomes.parquet",
    }

    datasets = {}

    for name, filename in files.items():
        path = PROCESSED_DATA_PATH / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing staging file: {path}")

        datasets[name] = pd.read_parquet(path)
        print(f"Loaded {name}: {len(datasets[name]):,} rows")

    return datasets

def load():

    engine = get_engine()

    staging = load_staging_data()

    # ================= CLEAR TABLES =================

    clear_table("fact_business_outcomes", engine)
    clear_table("fact_employee_monthly", engine)

    clear_table("dim_date", engine)
    clear_table("dim_employee", engine)
    clear_table("dim_store", engine)

    # ================= DIMENSIONS =================

    dim_store = build_dim_store(staging["stores"])
    dim_employee = build_dim_employee(staging["employees"])
    dim_date = build_dim_date(staging["monthly_performance"])

    save_to_sql(dim_store, "dim_store", engine)
    save_to_sql(dim_employee, "dim_employee", engine)
    save_to_sql(dim_date, "dim_date", engine)

    dim_store = load_from_sql("dim_store", engine)
    dim_employee = load_from_sql("dim_employee", engine)
    dim_date = load_from_sql("dim_date", engine)

    # ================= FACT EMPLOYEE MONTHLY =================

    fact_monthly = build_fact_employee_monthly(
        staging["monthly_performance"],
        staging["employees"],
    )

    fact_monthly = map_keys(
        fact_monthly,
        dim_employee,
        dim_store,
        dim_date,
    )

    fact_monthly = fact_monthly[
        [
            "employee_sk",
            "store_sk",
            "date_key",
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
    ]

    save_to_sql(
        fact_monthly,
        "fact_employee_monthly",
        engine,
    )

    # ================= FACT BUSINESS OUTCOMES =================

    fact_business = build_fact_business_outcomes(
        staging["business_outcomes"],
    )

    fact_business["year_month"] = (
    pd.to_datetime(fact_business["year_month"])
    .dt.strftime("%Y-%m")
)

    dim_date["year_month"] = (
        pd.to_datetime(dim_date["year_month"])
        .dt.strftime("%Y-%m")
    )

    fact_business = fact_business.merge(
            dim_store[["store_sk", "store_id"]],
            on="store_id",
            how="left",
        )

    fact_business = fact_business.merge(
        dim_date[["date_key", "year_month"]],
        on="year_month",
        how="left",
    )

    fact_business = fact_business[
        [
            "store_sk",
            "date_key",
            "sales_target",
            "sales_actual",
            "sales_achievement_pct",
            "customer_satisfaction",
            "nps_score",
            "waste_percentage",
            "on_time_delivery",
        ]
    ]

    save_to_sql(
        fact_business,
        "fact_business_outcomes",
        engine,
    )

    print("\nLoad completed successfully.")
