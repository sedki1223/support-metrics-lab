import pandas as pd

from src.metrics import (
    prepare_metrics,
    total_tickets,
    open_tickets,
    resolved_tickets,
    average_first_response_minutes,
    average_resolution_hours,
    average_customer_satisfaction,
    sla_compliance_rate,
    tickets_by_priority,
    resolution_by_priority,
)


def make_test_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ticket_id": ["T1", "T2", "T3"],
            "created_at": pd.to_datetime(
                [
                    "2026-09-01 08:00",
                    "2026-09-01 09:00",
                    "2026-09-01 10:00",
                ]
            ),
            "first_response_at": pd.to_datetime(
                [
                    "2026-09-01 08:20",
                    "2026-09-01 09:45",
                    "2026-09-01 10:10",
                ]
            ),
            "resolved_at": pd.to_datetime(
                [
                    "2026-09-01 10:00",
                    "2026-09-01 13:00",
                    None,
                ]
            ),
            "agent": ["Alice", "Bob", "Charlie"],
            "priority": ["High", "Medium", "Low"],
            "category": ["Login", "Billing", "General"],
            "status": ["Resolved", "Resolved", "Open"],
            "customer_satisfaction": [5.0, 4.0, None],
        }
    )


def test_prepare_metrics_calculates_response_and_resolution_times():
    df = prepare_metrics(make_test_data())

    assert df.loc[0, "first_response_minutes"] == 20
    assert df.loc[1, "first_response_minutes"] == 45

    assert df.loc[0, "resolution_hours"] == 2
    assert df.loc[1, "resolution_hours"] == 4

    assert pd.isna(df.loc[2, "resolution_hours"])


def test_ticket_counts():
    df = prepare_metrics(make_test_data())

    assert total_tickets(df) == 3
    assert open_tickets(df) == 1
    assert resolved_tickets(df) == 2


def test_average_metrics():
    df = prepare_metrics(make_test_data())

    assert average_first_response_minutes(df) == 25
    assert average_resolution_hours(df) == 3
    assert average_customer_satisfaction(df) == 4.5


def test_sla_compliance():
    df = prepare_metrics(make_test_data())

    assert sla_compliance_rate(df, target_minutes=30) == 66.66666666666666


def test_ticket_grouping():
    df = prepare_metrics(make_test_data())

    priority_counts = tickets_by_priority(df)

    assert priority_counts["High"] == 1
    assert priority_counts["Medium"] == 1
    assert priority_counts["Low"] == 1


def test_resolution_grouping_excludes_open_tickets():
    df = prepare_metrics(make_test_data())

    result = resolution_by_priority(df)

    assert result.loc["High", "tickets"] == 1
    assert result.loc["Medium", "tickets"] == 1
    assert pd.isna(result.loc["Low", "avg_resolution_hours"])