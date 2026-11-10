"""
Name:       Elizabeth Menjivar and Solomiia Rusyn
CS230:      Section 2
Data:       New York Housing Market

Description:
This program is a Streamlit data explorer for the New York housing market.
Users can filter properties by borough, price range, bedrooms, and view charts and maps.
"""

import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import altair as alt

st.set_page_config(
    page_title="NY Housing Explorer",
    page_icon="🏙️",
    layout="wide"
)


BOROUGH_COLORS = {
    "Manhattan": [255, 0, 0],
    "Brooklyn": [0, 128, 255],
    "Queens": [0, 200, 0],
    "Bronx": [255, 165, 0],
    "Staten Island": [128, 0, 128]
}

@st.cache_data
def load_data(csv_path: str):
    df = pd.read_csv(csv_path)
    df = df.rename(columns={
        "PRICE": "sale_price",
        "PROPERTYSQFT": "gross_sqft",
        "BEDS": "bedrooms",
        "LOCALITY": "borough",
        "SUBLOCALITY": "neighborhood",
        "LATITUDE": "latitude",
        "LONGITUDE": "longitude"
    })
    # [DATATYPES] Convert columns to numeric types
    df["sale_price"] = pd.to_numeric(df["sale_price"], errors="coerce")
    df = df.dropna(subset=["sale_price"])
    df["gross_sqft"] = pd.to_numeric(df["gross_sqft"], errors="coerce")
    df = df[df["gross_sqft"] > 0]
    # [COLUMNS] Add new calculated column
    df["price_per_sqft"] = df["sale_price"] / df["gross_sqft"]
    # [FILTER1] Filter by one condition (price range)
    df = df[(df["sale_price"] > 10000) & (df["sale_price"] < 200_000_000)]
    df["neighborhood"] = df["neighborhood"].fillna("Unknown")
    return df

# [FUNC2P] Function with two+ parameters, one default
def filter_data(df, boroughs, price_range, min_beds=0):
    # [FILTER2] Filter by two conditions (price range AND bedrooms)
    filtered = df[
        (df["sale_price"] >= price_range[0]) &
        (df["sale_price"] <= price_range[1])
    ]
    if boroughs:
        filtered = filtered[filtered["borough"].isin(boroughs)]
    filtered = filtered[filtered["bedrooms"] >= min_beds]
    return filtered

# [FUNCRETURN2] Function returning two values
def get_extremes(df):
    # [MAXMIN] Find largest and smallest values
    max_row = df.loc[df["sale_price"].idxmax()]
    min_row = df.loc[df["sale_price"].idxmin()]
    return max_row, min_row

# [GROUPBY] Group data by borough
def borough_summary(df):
    return df.groupby("borough").agg(
        avg_price=("sale_price", "mean"),
        median_price=("sale_price", "median"),
        n=("sale_price", "count")
    ).reset_index()

# [GROUPBY] Group data by neighborhood
def neighborhood_summary(df, borough):
    subset = df[df["borough"] == borough]
    return subset.groupby("neighborhood").agg(
        avg_price=("sale_price", "mean"),
        median_price=("sale_price", "median"),
        n=("sale_price", "count")
    ).reset_index().sort_values("avg_price", ascending=False)

# [DICTMETHOD] Using dictionary
def get_borough_color(name: str):
    return BOROUGH_COLORS.get(name, [200, 200, 200])

def main():
    st.title("New York Housing Explorer")

    csv_path = "NY-House-Dataset.csv"
    df = load_data(csv_path)

    st.sidebar.header("Filters")

    min_price, max_price = df["sale_price"].min(), df["sale_price"].max()
    boroughs = sorted(df["borough"].dropna().unique().tolist())

    # [ST1] Multi-select widget
    selected_boroughs = st.sidebar.multiselect("Select borough(s):", options=boroughs, default=boroughs)

    # [ST2] Slider widget
    price_range = st.sidebar.slider("Sale price range:", int(min_price), int(max_price),
                                    (int(min_price), int(max_price)), step=10000)

    # [ST3] Radio button widget
    stat_choice = st.sidebar.radio("Statistic:", options=["Average", "Median"])

    # [ST4] Dropdown  widget
    chosen_borough = st.sidebar.selectbox("Choose a borough:", options=selected_boroughs if selected_boroughs else boroughs)

    # [ST5] Text input widget
    note = st.sidebar.text_input("Add a note for your analysis:")

    # [ST6] Checkbox widget
    show_hist = st.sidebar.checkbox("Show histogram of prices")

    # [FUNCCALL2] filter_data
    filtered = filter_data(df, selected_boroughs, price_range)

    st.write(f"### Properties Found: {len(filtered):,}")
    if note:
        st.info(f"Note: {note}")

    if filtered.empty:
        st.warning("No matching properties. Widen your filters.")
        return

    # [CHART1] Bar chart of borough prices
    st.subheader("Price Comparison by Borough")
    boro_stats = borough_summary(filtered)
    y_col = "avg_price" if stat_choice == "Average" else "median_price"
    st.bar_chart(boro_stats.set_index("borough")[y_col])

    # [CHART2] Neighborhood bar chart
    st.subheader("Neighborhood Breakdown")
    nh = neighborhood_summary(filtered, chosen_borough)
    st.bar_chart(nh.set_index("neighborhood")["avg_price"].head(15))

    # [CHART3] Scatter plot
    st.subheader("Price vs Property Size")
    scatter = alt.Chart(filtered.sample(min(3000, len(filtered)))).mark_circle(size=40).encode(
        x="gross_sqft", y="sale_price", color="borough",
        tooltip=["borough", "neighborhood", "sale_price", "gross_sqft"]
    ).properties(height=400)
    st.altair_chart(scatter, use_container_width=True)

    # [CHART4] Histogram
    if show_hist:
        st.subheader("Histogram of Sale Prices")
        st.bar_chart(filtered["sale_price"].value_counts().sort_index())

    # [CHART5] Pie chart
    st.subheader("Proportion of Listings by Borough")
    pie_data = boro_stats.copy()
    pie = alt.Chart(pie_data).mark_arc().encode(
        theta="n", color="borough", tooltip=["borough", "n"]
    )
    st.altair_chart(pie, use_container_width=True)

    # [MAP] PyDeck map visualization
    st.subheader("Map of Properties")
    map_df = filtered.dropna(subset=["latitude", "longitude"]).copy()
    if not map_df.empty:
        map_df["color"] = map_df["borough"].apply(get_borough_color)
        layer = pdk.Layer("ScatterplotLayer", data=map_df,
                          get_position=["longitude", "latitude"],
                          get_fill_color="color", get_radius=40, pickable=True)
        view = pdk.ViewState(latitude=map_df["latitude"].mean(),
                             longitude=map_df["longitude"].mean(), zoom=10, pitch=45)
        st.pydeck_chart(pdk.Deck(initial_view_state=view, layers=[layer],
                                 tooltip={"html": "<b>{borough}</b><br>${sale_price}"}))

    # [FUNCRETURN2]
    st.subheader("Price Extremes")
    max_row, min_row = get_extremes(filtered)
    st.write(f"**Most Expensive:** ${max_row['sale_price']:,.0f} in {max_row['borough']}")
    st.write(f"**Least Expensive:** ${min_row['sale_price']:,.0f} in {min_row['borough']}")

    # [LISTCOMP]
    st.subheader("Borough Name Lengths")
    borough_lengths = [len(b) for b in boroughs]
    st.write("Lengths of borough names:", borough_lengths)

    # [ITERLOOP]
    st.subheader("Borough Color Codes")
    for b, c in BOROUGH_COLORS.items():
        st.write(f"{b}: {c}")

    # [LAMBDA]
    st.subheader("Price Category Classification")
    df["price_category"] = df["sale_price"].apply(lambda x: "High" if x > 1_000_000 else "Low")
    st.write(df[["sale_price", "price_category"]].head())

if __name__ == "__main__":
    main()




