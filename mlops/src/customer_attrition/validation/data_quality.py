import pandas as pd

from customer_attrition.common.logging import setup_logging
from customer_attrition.validation.expectations import validate_values
from customer_attrition.validation.schema import validate_schema


def run_validation(df: pd.DataFrame) -> bool:
    logger = setup_logging()

    schema_ok, schema_errors = validate_schema(df)
    if not schema_ok:
        for err in schema_errors:
            logger.error(f"Schema validation failed: {err}")
        raise ValueError("Schema validation failed")

    values_ok, value_errors = validate_values(df)
    if not values_ok:
        for err in value_errors:
            logger.error(f"Value validation failed: {err}")
        raise ValueError("Value validation failed")

    logger.info("Data validation passed")
    return True
