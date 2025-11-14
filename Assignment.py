import streamlit as st
import pandas as pd
from datetime import timedelta
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🌍 Environmental Pollution Dashboard")
st.caption("Interactive dashboard for exploring air quality trends across cities.")

df = pd.read_csv("smooth_air_quality_dataset.csv", parse_dates=["Date"])
st.dataframe(df.head())
df.describe()

st.sidebar.header("Filters")

cities = sorted(df["City"].dropna().unique())
selected_cities = st.sidebar.multiselect("Select Cities", cities, default=cities[:3] if len(cities) > 3 else cities)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()
date_range = st.sidebar.date_input("Date Range", (min_date, max_date), min_value=min_date, max_value=max_date)
start_date = pd.to_datetime(date_range[0])
end_date = pd.to_datetime(date_range[1]) + timedelta(days=1) - timedelta(seconds=1)

aqi_min = int(df["AQI"].min())
aqi_max = int(df["AQI"].max())
aqi_range = st.sidebar.slider("AQI Range", aqi_min, aqi_max, (aqi_min, aqi_max))

filtered = df.copy()
filtered = filtered[filtered["City"].isin(selected_cities)]
filtered = filtered[(filtered["Date"] >= start_date) & (filtered["Date"] <= end_date)]
filtered = filtered[(filtered["AQI"] >= aqi_range[0]) & (filtered["AQI"] <= aqi_range[1])]

k1, k2, k3 = st.columns(3)
k1.metric("Average AQI", f"{filtered['AQI'].mean():.1f}")
k2.metric("Highest PM2.5 (µg/m³)", f"{filtered['PM2.5'].max():.1f}")
k3.metric("Lowest Humidity (%)", f"{filtered['Humidity'].min():.1f}")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("AQI / PM2.5 Trend")
    city_choice = st.selectbox("City", selected_cities if selected_cities else cities)
    metric = st.selectbox("Metric", ["AQI", "PM2.5"])
    df_city = filtered[filtered["City"] == city_choice]
    if df_city.empty:
        st.info("No data available for the selected filters.")
    else:
        fig = px.line(df_city, x="Date", y=metric, markers=True, title=f"{metric} Over Time - {city_choice}")
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Average AQI by City")
    avg_city = filtered.groupby("City", as_index=False)["AQI"].mean().sort_values("AQI", ascending=False)
    fig_bar = px.bar(avg_city, x="City", y="AQI", text="AQI", title="Average AQI by City")
    st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("PM2.5 vs Temperature")
if not filtered.empty:
    fig_scatter = px.scatter(
        filtered, x="PM2.5", y="Temperature", color="City",
        hover_data=["Date", "AQI"], title="PM2.5 vs Temperature"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("Filtered Data")
st.write(f"Rows: {len(filtered)}")
csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv_bytes, "filtered_pollution_data.csv", "text/csv")

st.subheader("Insights")
insights = []

if not filtered.empty:
    city_max_aqi = filtered.groupby("City")["AQI"].mean().idxmax()
    insights.append(f"City with highest average AQI: {city_max_aqi}")

    if filtered["PM2.5"].notna().any():
        day = filtered.loc[filtered["PM2.5"].idxmax()]["Date"].date()
        insights.append(f"Day with highest PM2.5: {day}")

if insights:
    for i in insights:
        st.write("- " + i)
else:
    st.write("No insights available for the current filtered data.")
