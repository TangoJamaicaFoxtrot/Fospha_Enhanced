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

# Market Channel Summary
market_channel_summary = build_summary(df, ["Market", "Channel"])
markets = sorted(market_channel_summary["Market"].unique())
selected_markets = st.multi_select(
  "Select Market(s)",
  markets,
  default=markets
)

filtered_market = market_channel[market_channel["Market"].isin(selected_markets)]

fig = px.bar(
    filtered_market,
    x="Channel",
    y="ROAS",
    color="Market",
    barmode="group",
    title="ROAS by Channel"
)

st.plotly_chart(fig, use_container_width=True)
