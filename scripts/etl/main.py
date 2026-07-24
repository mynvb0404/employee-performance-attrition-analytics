from scripts.etl.extract import extract
from scripts.etl.transform.transformation import(
    transform_employees,
    transform_stores,
    transform_monthly_performance,
    transform_role_kpis,
    transform_business_outcomes
)
from scripts.etl.utils import write_staging
from scripts.etl.load import extract

TRANSFORMERS = {
    "employees": transform_employees,
    "stores": transform_stores,
    "monthly_performance": transform_monthly_performance,
    "role_kpis": transform_role_kpis,
    "business_outcomes": transform_business_outcomes,
}
if __name__ == '__main__':
    datasets = extract()

    transformed = {}

    for name, df in datasets.items():
        print(name)
        print(df.columns.tolist())
        transformed[name] = TRANSFORMERS[name](df)
        write_staging(transformed[name], name)
        