import sys

from scripts.etl.extract import extract
from scripts.etl.load import load
from scripts.etl.transform.transformation import (
    transform_business_outcomes,
    transform_employees,
    transform_monthly_performance,
    transform_role_kpis,
    transform_stores,
)
from scripts.etl.utils import write_staging

TRANSFORMERS = {
    "employees": transform_employees,
    "stores": transform_stores,
    "monthly_performance": transform_monthly_performance,
    "role_kpis": transform_role_kpis,
    "business_outcomes": transform_business_outcomes,
}


def run_etl_pipeline():
    """
    Execute ETL pipeline:
        Extract -> Transform -> Load
    """

    try:
        print("=" * 60)
        print("ETL PIPELINE STARTED")
        print("=" * 60)

        # ================= EXTRACT =================

        print("\n[1/3] Extract")

        datasets = extract()

        print(f"\nLoaded {len(datasets)} datasets.")

        # ================= TRANSFORM =================

        print("\n[2/3] Transform")

        for name, df in datasets.items():
            print(f"Transforming {name} ({len(df):,} rows)...")

            transformed = TRANSFORMERS[name](df)
            print(name, type(transformed))
            write_staging(transformed, name)

        print("Transformation completed.")

        # ================= LOAD =================

        print("\n[3/3] Load")

        load()

        print("\n" + "=" * 60)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        print(f"\nETL failed: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    run_etl_pipeline()