import pandas as pd


def prepare_metrics(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    response_delta = result["first_response_at"] - result["created_at"]
    resolution_delta = result["resolved_at"] - result["created_at"]

    result["first_response_minutes"] = (
        response_delta.dt.total_seconds() / 60
    )

    result["resolution_hours"] = (
        resolution_delta.dt.total_seconds() / 3600
    )

    return result


def total_tickets(df: pd.DataFrame) -> int:
    return len(df)


def open_tickets(df: pd.DataFrame) -> int:
    return int((df["status"] == "Open").sum())


def resolved_tickets(df: pd.DataFrame) -> int:
    return int((df["status"] == "Resolved").sum())


def average_first_response_minutes(df: pd.DataFrame) -> float:
    return float(df["first_response_minutes"].mean())


def average_resolution_hours(df: pd.DataFrame) -> float:
    return float(df["resolution_hours"].mean())


def average_customer_satisfaction(df: pd.DataFrame) -> float:
    return float(df["customer_satisfaction"].mean())


def tickets_by_priority(df: pd.DataFrame) -> pd.Series:
    return df["priority"].value_counts()


def tickets_by_category(df: pd.DataFrame) -> pd.Series:
    return df["category"].value_counts()


def tickets_by_agent(df: pd.DataFrame) -> pd.Series:
    return df["agent"].value_counts()

def daily_ticket_volume(df: pd.DataFrame) -> pd.Series:
    return (
        df.set_index("created_at")
        .resample("D")["ticket_id"]
        .count()
    )

def prepare_metrics(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    response_delta = result["first_response_at"] - result["created_at"]
    resolution_delta = result["resolved_at"] - result["created_at"]

    result["first_response_minutes"] = (
        response_delta.dt.total_seconds() / 60
    )

    result["resolution_hours"] = (
        resolution_delta.dt.total_seconds() / 3600
    )

    invalid_response = result["first_response_minutes"] < 0
    result.loc[invalid_response, "first_response_minutes"] = float("nan")

    invalid_resolution = result["resolution_hours"] < 0
    result.loc[invalid_resolution, "resolution_hours"] = float("nan")

    result.loc[
        result["status"] != "Resolved",
        "resolution_hours",
    ] = float("nan")

    return result

def data_quality_summary(df: pd.DataFrame) -> dict[str, int]:
    resolved = df["status"].eq("Resolved")

    invalid_response = (
        df["first_response_at"].notna()
        & df["created_at"].notna()
        & (df["first_response_at"] < df["created_at"])
    )

    invalid_resolution = (
        resolved
        & df["resolved_at"].notna()
        & df["created_at"].notna()
        & (df["resolved_at"] < df["created_at"])
    )

    return {
        "missing_first_response": int(df["first_response_at"].isna().sum()),
        "resolved_missing_resolution": int(
            (resolved & df["resolved_at"].isna()).sum()
        ),
        "resolved_missing_satisfaction": int(
            (resolved & df["customer_satisfaction"].isna()).sum()
        ),
        "invalid_response_times": int(invalid_response.sum()),
        "invalid_resolution_times": int(invalid_resolution.sum()),
    }

def sla_compliance_rate(
    df: pd.DataFrame,
    target_minutes: int = 30,
) -> float:
    response_times = df["first_response_minutes"].dropna()

    if response_times.empty:
        return 0.0

    return float(
        (response_times <= target_minutes).mean() * 100
    )

def sla_by_agent(
    df: pd.DataFrame,
    target_minutes: int = 30,
) -> pd.Series:
    response_df = df.dropna(subset=["first_response_minutes"])

    if response_df.empty:
        return pd.Series(dtype="float64")

    return (
        response_df.groupby("agent")["first_response_minutes"]
        .apply(lambda values: (values <= target_minutes).mean() * 100)
        .round(1)
        .sort_values(ascending=False)
    )

def resolution_by_priority(df: pd.DataFrame) -> pd.DataFrame:
    resolved = df.dropna(subset=["resolution_hours"])

    if resolved.empty:
        return pd.DataFrame(
            columns=["tickets", "avg_resolution_hours"]
        )

    return (
        resolved.groupby("priority")
        .agg(
            tickets=("ticket_id", "count"),
            avg_resolution_hours=("resolution_hours", "mean"),
        )
        .round(2)
        .reindex(["High", "Medium", "Low"])
    )


def resolution_by_category(df: pd.DataFrame) -> pd.DataFrame:
    resolved = df.dropna(subset=["resolution_hours"])

    if resolved.empty:
        return pd.DataFrame(
            columns=["tickets", "avg_resolution_hours"]
        )

    return (
        resolved.groupby("category")
        .agg(
            tickets=("ticket_id", "count"),
            avg_resolution_hours=("resolution_hours", "mean"),
        )
        .round(2)
        .sort_values("avg_resolution_hours", ascending=False)
    )