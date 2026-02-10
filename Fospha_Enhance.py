import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

df = pd.read_csv("Fospha Data 2.csv", sep=";")

# Fix date column
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Date_Year_Month"] = df["Date"].dt.to_period("M").astype(str)

# Fix category inconsistencies
df_cat_cols = ["Market", "Channel", "Source", "Campaign", "Date_Year_Month"]
for col in df_cat_cols:
    df[col] = df[col].astype(str).str.title().str.strip()

# Change data type of numeric columns
df_num_cols = ["Cost", "Fospha Attribution Conversions", "Fospha Attribution Revenue",
               "Fospha Attribution New Conversions"]

for col in df_num_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")


st.sidebar.header("Filters")

markets = sorted(df["Market"].dropna().unique())
months = sorted(df["Date_Year_Month"].dropna().unique())

selected_markets = st.sidebar.multiselect("Market", markets, default=markets)
selected_date = st.sidebar.multiselect("Date", months, default=months)

filtered_df = df[
    (df["Market"].isin(selected_markets)) &
    (df["Date_Year_Month"].isin(selected_date))
]

# Build summary engine
def build_summary(df, groupby_col):
    summary = (df.groupby(groupby_col).agg(
        Total_Visits=("Visits", "sum"),
        Cost=("Cost", "sum"),
        Conversions=("Fospha Attribution Conversions", "sum"),
        Revenue=("Fospha Attribution Revenue", "sum"),
        New_Conversions=("Fospha Attribution New Conversions", "sum")
    ).reset_index()
              )
    summary["ROAS"] = ((summary["Revenue"] / summary["Cost"]).round(2))
    summary["CAC"] = ((summary["Cost"] / summary["New_Conversions"]).round(2))
    summary["CPP"] = ((summary["Cost"] / summary["Conversions"]).round(2))
    summary["AOV"] = ((summary["Revenue"] / summary["Conversions"]).round(2))
    summary["Return_Conversions"] = ((summary["Conversions"] - summary["New_Conversions"]).round(2))
    summary_num_cols = ["Total_Visits", "Cost", "Conversions", "Revenue", "New_Conversions"]
    for col in summary_num_cols:
        summary[summary_num_cols] = summary[summary_num_cols].round(2)
    
    return summary

# Market / Paid Channel Summary
market_channel_summary = build_summary(filtered_df, ["Market", "Channel"])
paid_channels = ["Paid Search - Generic", "Paid Shopping", "Paid Social", "Performance Max"]
market_paid_channel_summary = market_channel_summary[market_channel_summary["Channel"].isin(paid_channels)]

metrics = ["ROAS", "CAC", "CPP", "AOV", "Conversions", "New_Conversions", "Return_Conversions"]
selected_metric = st.selectbox(
    "Select Metric to Visualise",
    metrics,
    index=0
)

fig = px.bar(
    market_paid_channel_summary,
    x="Channel",
    y=selected_metric,
    color="Market",
    barmode="group",
    title=(f"{selected_metric} by Channel and Market")
)

st.plotly_chart(fig, use_container_width=True)
    
    
