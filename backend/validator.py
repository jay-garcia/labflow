import pandas as pd


REQUIRED_COLUMNS = [
    "experiment_id",
    "sample_id",
    "compound_name",
    "concentration_mg_ml",
    "result",
    "run_date",
    "scientist",
]

ALLOWED_RESULTS = {"Positive", "Negative"}


def validate_experiment_csv(dataframe: pd.DataFrame) -> list[str]:
    errors: list[str] = []

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing_columns:
        errors.append(
            "Missing required columns: " + ", ".join(missing_columns)
        )
        return errors

    concentration_values = pd.to_numeric(
        dataframe["concentration_mg_ml"], errors="coerce"
    )
    if concentration_values.isna().any():
        errors.append("concentration_mg_ml must contain only numeric values.")

    invalid_results = ~dataframe["result"].isin(ALLOWED_RESULTS)
    if invalid_results.any():
        errors.append('result must contain only "Positive" or "Negative".')

    duplicate_sample_ids = dataframe["sample_id"].duplicated()
    if duplicate_sample_ids.any():
        errors.append("sample_id must not contain duplicate values.")

    return errors
