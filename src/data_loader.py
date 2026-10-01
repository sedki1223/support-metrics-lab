from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tickets.csv"

REQUIRED_COLUMNS = {
    "ticket_id",
    "created_at",
    "first_response_at",
    "resolved_at",
    "agent",
    "priority",
    "category",
    "status",
    "customer_satisfaction",
}


def load_tickets() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    datetime_columns = [
        "created_at",
        "first_response_at",
        "resolved_at",
    ]

    for column in datetime_columns:
        df[column] = pd.to_datetime(df[column], errors="coerce")

    text_columns = [
        "agent",
        "priority",
        "category",
        "status",
    ]

    for column in text_columns:
        df[column] = df[column].astype("string").str.strip()

    df["status"] = df["status"].str.title()

    df["customer_satisfaction"] = pd.to_numeric(
        df["customer_satisfaction"],
        errors="coerce",
    )

    invalid_satisfaction = ~df["customer_satisfaction"].between(1, 5)
    df.loc[invalid_satisfaction, "customer_satisfaction"] = float("nan")

    return df