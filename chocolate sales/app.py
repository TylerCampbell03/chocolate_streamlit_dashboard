import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


st.set_page_config(page_title = "Chocolate Sales", layout = "wide")

st.title("Chocolate Sales Dashboard")
st.caption("Created by Tyler Campbell")
# -----------
# load data
# ----------

@st.cache_data

def load_data():
    data_path = Path(__file__).resolve().parent / "Chocolate_Sales.csv"
    df = pd.read_csv(data_path)
    df["Date"] = pd.to_datetime(df["Date"], format = "%d/%m/%Y")
    return df
df = load_data()

# -------
# filters
# --------

st.sidebar.header("Filters")
min_date = df["Date"].min()
max_date = df["Date"].max()
date_range = st.sidebar.date_input("Date Range", value = (min_date.date(), max_date.date()),
                                   min_value= min_date.date(), max_value = max_date.date())
country = sorted(df["Country"].unique())
product = sorted(df["Product"].unique())
country_sel = st.sidebar.multiselect("Country", country, default=country)
product_sel = st.sidebar.selectbox("Product", product)


# apply filters
start_time, end_time = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
f = df[
    (df["Date"] >= start_time) &
    (df["Date"] <= end_time) &
    (df["Country"].isin(country_sel)) &
    (df["Product"].isin([product_sel]))
].copy()

# ------------
# metrics
# -----------

people_total = f["Sales_Person"].nunique()
country_total = f["Country"].nunique()
product_total = f["Product"].nunique()
sales_total = f["Amount"].sum()
boxes_total = f["Boxes_Shipped"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Sales People", f"{people_total:,}")
c2.metric("Countries", f"{country_total:,}")
c3.metric("Sales", f"${sales_total:,.2f}")
c4.metric("Boxes Shipped", f"{boxes_total:,}")

st.divider()

# -----------
# Visuals
# -----------

left, right = st.columns(2)

time_series = (f.groupby("Date", as_index = False)["Amount"]
    .sum()
    .sort_values("Date")
               )
time_plot = px.line(time_series, x = "Date", y = "Amount", title = "Sales Over Time")
left.plotly_chart(time_plot, use_container_width = True)


top_people = (f.groupby("Sales_Person", as_index = False)["Boxes_Shipped"]
    .sum()
    .sort_values("Boxes_Shipped", ascending = False)
    .head(10)
              )
people_bar = px.bar(top_people, x = "Sales_Person", y = "Boxes_Shipped", title = "Top 10 Individuals (Boxes Sold)")
right.plotly_chart(people_bar, use_container_width = True)

sales_hist = px.histogram(f, x = "Amount", title = "Distribution of Sales")
left.plotly_chart(sales_hist, use_container_width = True)

country_box = f.groupby("Country", as_index = False)["Boxes_Shipped"].sum()
country_pit = px.pie(country_box, names = "Country", values = "Boxes_Shipped", title = "Proportion of Boxes Shipped")
right.plotly_chart(country_pit, use_container_width = True)

st.divider()

# -------------
# Dataframe
# -------------

st.subheader("Filtered Data Frame")
st.dataframe(f.sort_values("Date", ascending = False),
             use_container_width = True,
             hide_index=False)




