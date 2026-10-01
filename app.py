import pandas as pd
import streamlit as st

from src.data_loader import load_tickets
from src.metrics import (
    prepare_metrics,
    daily_ticket_volume,
    data_quality_summary,
    sla_compliance_rate,
    sla_by_agent,
    resolution_by_priority,
    resolution_by_category,
)


st.set_page_config(
    page_title="Support Metrics Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------------
# Global visual styling
# -------------------------

st.html(
    """
    <style>
        .main-title {
            font-size: 3.2rem;
            line-height: 1;
            font-weight: 750;
            letter-spacing: -0.05em;
            margin-bottom: 0.7rem;
        }

        .hero {
            padding: 1.8rem 2rem;
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 22px;
            background:
                linear-gradient(
                    135deg,
                    rgba(199,243,107,0.10),
                    rgba(255,255,255,0.025)
                );
            margin-bottom: 1.4rem;
        }

        .hero-kicker {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            opacity: 0.65;
            margin-bottom: 0.6rem;
        }

        .hero-title {
            font-size: 2.8rem;
            line-height: 1;
            font-weight: 800;
            letter-spacing: -0.045em;
            margin-bottom: 0.7rem;
        }

        .hero-copy {
            font-size: 1rem;
            opacity: 0.68;
            max-width: 720px;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .hero-status {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: rgba(199,243,107,0.12);
            border: 1px solid rgba(199,243,107,0.25);
            color: #C7F36B;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.05em;
        }

        .section-kicker {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            opacity: 0.5;
            margin-top: 0.2rem;
            margin-bottom: 0.25rem;
        }

        .section-title {
            font-size: 1.55rem;
            font-weight: 750;
            letter-spacing: -0.025em;
            margin-bottom: 0.9rem;
        }

        .st-key-kpi_total,
        .st-key-kpi_open,
        .st-key-kpi_resolved,
        .st-key-kpi_response,
        .st-key-kpi_sla,
        .st-key-kpi_satisfaction {
            border-radius: 18px;
            border-color: rgba(255,255,255,0.08);
            background: rgba(255,255,255,0.025);
            padding: 0.25rem 0.15rem;
            min-height: 118px;
        }

        .st-key-kpi_total:hover,
        .st-key-kpi_open:hover,
        .st-key-kpi_resolved:hover,
        .st-key-kpi_response:hover,
        .st-key-kpi_sla:hover,
        .st-key-kpi_satisfaction:hover {
            border-color: rgba(199,243,107,0.25);
        }

        [data-testid="stMetricLabel"] {
            font-size: 0.78rem;
            opacity: 0.62;
        }

        [data-testid="stMetricValue"] {
            font-weight: 750;
            letter-spacing: -0.04em;
        }

        .scope-note {
            opacity: 0.55;
            font-size: 0.78rem;
        }
    </style>
    """
)


# -------------------------
# Data
# -------------------------

@st.cache_data
def get_data() -> pd.DataFrame:
    return prepare_metrics(load_tickets())


df = get_data()
quality = data_quality_summary(df)


# -------------------------
# Hero
# -------------------------

st.html(
    """
    <div class="hero">
        <div class="hero-kicker">Support Operations / Analytics</div>
        <div class="hero-title">Support Metrics Lab</div>
        <div class="hero-copy">
            Monitor ticket volume, response performance, SLA compliance,
            resolution behavior, and customer satisfaction from one operational view.
        </div>
        <span class="hero-status">● DATASET ONLINE</span>
    </div>
    """
)


# -------------------------
# Sidebar filters
# -------------------------

with st.sidebar:
    st.markdown("## Filters")
    st.caption("Refine the operational view.")

    selected_agents = st.multiselect(
        "Agent",
        options=sorted(df["agent"].dropna().unique()),
        default=sorted(df["agent"].dropna().unique()),
    )

    selected_priorities = st.multiselect(
        "Priority",
        options=sorted(df["priority"].dropna().unique()),
        default=sorted(df["priority"].dropna().unique()),
    )

    selected_categories = st.multiselect(
        "Category",
        options=sorted(df["category"].dropna().unique()),
        default=sorted(df["category"].dropna().unique()),
    )

    min_date = df["created_at"].min().date()
    max_date = df["created_at"].max().date()

    selected_dates = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.divider()

    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
        st.markdown(
            f"**View:** {start_date.strftime('%d %b %Y')} → "
            f"{end_date.strftime('%d %b %Y')}"
        )


# -------------------------
# Filtering
# -------------------------

base_filter = (
    df["agent"].isin(selected_agents)
    & df["priority"].isin(selected_priorities)
    & df["category"].isin(selected_categories)
)

if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    base_filter = (
        base_filter
        & df["created_at"].dt.date.between(start_date, end_date)
    )


filtered_df = df[base_filter]


st.markdown(
    f'<div class="scope-note">'
    f'Showing {len(filtered_df)} of {len(df)} tickets'
    f'</div>',
    unsafe_allow_html=True,
)


# -------------------------
# KPI calculations
# -------------------------

total = len(filtered_df)
open_count = int((filtered_df["status"] == "Open").sum())
resolved_count = int((filtered_df["status"] == "Resolved").sum())

avg_response = filtered_df["first_response_minutes"].mean()
avg_satisfaction = filtered_df["customer_satisfaction"].mean()
sla_rate = sla_compliance_rate(filtered_df)


# -------------------------
# KPI section
# -------------------------

st.markdown(
    '<div class="section-kicker">Snapshot</div>'
    '<div class="section-title">Operational health</div>',
    unsafe_allow_html=True,
)

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    with st.container(border=True, key="kpi_total"):
        st.metric("Total Tickets", total)

with kpi2:
    with st.container(border=True, key="kpi_open"):
        st.metric("Open Tickets", open_count)

with kpi3:
    with st.container(border=True, key="kpi_resolved"):
        st.metric("Resolved Tickets", resolved_count)


kpi4, kpi5, kpi6 = st.columns(3)

with kpi4:
    with st.container(border=True, key="kpi_response"):
        st.metric(
            "Avg First Response",
            f"{avg_response:.1f} min"
            if pd.notna(avg_response)
            else "—",
        )

with kpi5:
    with st.container(border=True, key="kpi_sla"):
        st.metric(
            "SLA Compliance",
            f"{sla_rate:.1f}%",
            help="First-response SLA target: 30 minutes.",
        )

with kpi6:
    with st.container(border=True, key="kpi_satisfaction"):
        st.metric(
            "Customer Satisfaction",
            f"{avg_satisfaction:.2f}/5"
            if pd.notna(avg_satisfaction)
            else "—",
        )


st.divider()


# -------------------------
# Overview charts
# -------------------------

st.markdown(
    '<div class="section-kicker">Overview</div>'
    '<div class="section-title">Ticket distribution</div>',
    unsafe_allow_html=True,
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Priority")

    priority_counts = (
        filtered_df["priority"]
        .value_counts()
        .reindex(["High", "Medium", "Low"], fill_value=0)
    )

    st.bar_chart(priority_counts)


with chart_col2:
    st.subheader("Category")

    category_counts = (
        filtered_df["category"]
        .value_counts()
        .sort_values(ascending=False)
    )

    st.bar_chart(category_counts)


chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("Agent")

    agent_counts = (
        filtered_df["agent"]
        .value_counts()
        .sort_values(ascending=False)
    )

    st.bar_chart(agent_counts)


with chart_col4:
    st.subheader("Status")

    status_counts = filtered_df["status"].value_counts()

    st.bar_chart(status_counts)


st.divider()


# -------------------------
# Trend
# -------------------------

st.markdown(
    '<div class="section-kicker">Trend</div>'
    '<div class="section-title">Ticket volume over time</div>',
    unsafe_allow_html=True,
)

daily_volume = daily_ticket_volume(filtered_df)

st.line_chart(daily_volume)


st.divider()


# -------------------------
# Detailed sections
# -------------------------

tab_performance, tab_investigate, tab_data = st.tabs(
    [
        "Performance",
        "Ticket Investigation",
        "Data & Export",
    ]
)


# -------------------------
# Performance tab
# -------------------------

with tab_performance:
    st.markdown(
        '<div class="section-kicker">Performance</div>'
        '<div class="section-title">Service performance</div>',
        unsafe_allow_html=True,
    )

    perf_col1, perf_col2 = st.columns(2)

    with perf_col1:
        st.subheader("SLA Compliance by Agent")

        agent_sla = sla_by_agent(filtered_df)

        st.bar_chart(agent_sla)

    with perf_col2:
        st.subheader("Resolution Time by Priority")

        priority_resolution = resolution_by_priority(filtered_df)

        st.bar_chart(
            priority_resolution["avg_resolution_hours"]
        )

    st.subheader("Resolution Time by Category")

    category_resolution = resolution_by_category(filtered_df)

    st.bar_chart(
        category_resolution["avg_resolution_hours"]
    )

    st.subheader("Agent Performance")

    agent_performance = (
        filtered_df.groupby("agent")
        .agg(
            tickets=("ticket_id", "count"),
            avg_response_minutes=("first_response_minutes", "mean"),
            avg_resolution_hours=("resolution_hours", "mean"),
            avg_satisfaction=("customer_satisfaction", "mean"),
        )
        .round(2)
    )

    st.dataframe(
        agent_performance,
        width="stretch",
    )


# -------------------------
# Investigation tab
# -------------------------

with tab_investigate:
    st.markdown(
        '<div class="section-kicker">Investigation</div>'
        '<div class="section-title">Inspect an individual ticket</div>',
        unsafe_allow_html=True,
    )

    ticket_options = filtered_df["ticket_id"].tolist()

    if ticket_options:
        selected_ticket_id = st.selectbox(
            "Ticket",
            options=ticket_options,
        )

        ticket = filtered_df[
            filtered_df["ticket_id"] == selected_ticket_id
        ].iloc[0]

        detail_col1, detail_col2, detail_col3, detail_col4 = st.columns(4)

        detail_col1.metric(
            "Status",
            ticket["status"],
        )

        detail_col2.metric(
            "Priority",
            ticket["priority"],
        )

        response_value = (
            f"{ticket['first_response_minutes']:.1f} min"
            if pd.notna(ticket["first_response_minutes"])
            else "—"
        )

        resolution_value = (
            f"{ticket['resolution_hours']:.1f} hrs"
            if pd.notna(ticket["resolution_hours"])
            else "—"
        )

        detail_col3.metric(
            "First Response",
            response_value,
        )

        detail_col4.metric(
            "Resolution",
            resolution_value,
        )

        ticket_details = pd.DataFrame(
            {
                "Field": [
                    "Ticket ID",
                    "Agent",
                    "Category",
                    "Priority",
                    "Status",
                    "Created At",
                    "First Response At",
                    "Resolved At",
                    "First Response Time",
                    "Resolution Time",
                    "Customer Satisfaction",
                ],
                "Value": [
                    ticket["ticket_id"],
                    ticket["agent"],
                    ticket["category"],
                    ticket["priority"],
                    ticket["status"],
                    ticket["created_at"],
                    ticket["first_response_at"],
                    (
                        ticket["resolved_at"]
                        if pd.notna(ticket["resolved_at"])
                        else "—"
                    ),
                    response_value,
                    resolution_value,
                    (
                        f"{ticket['customer_satisfaction']:.1f}/5"
                        if pd.notna(ticket["customer_satisfaction"])
                        else "—"
                    ),
                ],
            }
        )

        st.dataframe(
            ticket_details,
            hide_index=True,
            width="stretch",
        )
    else:
        st.info("No tickets match the current filters.")


# -------------------------
# Data tab
# -------------------------

with tab_data:
    st.markdown(
        '<div class="section-kicker">Data</div>'
        '<div class="section-title">Quality, records and export</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Dataset Quality")

    st.caption(
        f"Quality checks across the full dataset of {len(df)} tickets."
    )

    quality_df = pd.DataFrame(
        {
            "Check": [
                "Missing first response",
                "Resolved tickets missing resolution",
                "Resolved tickets missing satisfaction",
                "Invalid response times",
                "Invalid resolution times",
            ],
            "Issues": [
                quality["missing_first_response"],
                quality["resolved_missing_resolution"],
                quality["resolved_missing_satisfaction"],
                quality["invalid_response_times"],
                quality["invalid_resolution_times"],
            ],
        }
    )

    st.dataframe(
        quality_df,
        hide_index=True,
        width="stretch",
    )

    st.divider()

    st.subheader("Filtered Tickets")

    display_columns = [
        "ticket_id",
        "created_at",
        "agent",
        "priority",
        "category",
        "status",
        "first_response_minutes",
        "resolution_hours",
        "customer_satisfaction",
    ]

    filtered_display = filtered_df[display_columns].sort_values(
        "created_at",
        ascending=False,
    )

    st.dataframe(
        filtered_display,
        width="stretch",
    )

    csv_data = filtered_display.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Filtered Tickets",
        data=csv_data,
        file_name="support_metrics_filtered.csv",
        mime="text/csv",
        width="stretch",
    )