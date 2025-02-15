import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

def load_data():
    """
    Loads the cleaned exposures, hurricane,
    and any needed merges. Adjust paths as required.
    """
    df_exposures = pd.read_csv("cleaned_data/exposures_cleaned.csv")

    df_hurr = pd.read_csv("cleaned_data/hurr2_merged_with_h1_wind.csv")

    df_exposures_risk = pd.read_csv("cleaned_data/exposures_risk.csv")

    return df_exposures, df_hurr, df_exposures_risk

def main():
    st.title("Dynamic Underwriting Report")

    df_exposures, df_hurr, df_exposures_risk = load_data()

    st.sidebar.header("Filters")

    all_locs = sorted(df_exposures["Location"].unique())
    loc_selected = st.sidebar.multiselect(
        "Choose Location(s):",
        options=all_locs,
        default=all_locs[:3]  # pick a few by default
    )

    all_storms = sorted(df_hurr["storm_name"].unique())
    storm_selected = st.sidebar.multiselect(
        "Choose Hurricanes by Name:",
        options=all_storms,
        default=all_storms[:5]
    )

    if "year" in df_hurr.columns:
        years_all = sorted(df_hurr["year"].unique())
        year_selected = st.sidebar.multiselect(
            "Choose Hurricane Year(s):",
            options=years_all,
            default=years_all  # select all by default
        )
    else:
        year_selected = []

    x_years = st.sidebar.number_input(
        "Past X Years of Policy Results:", min_value=1, max_value=50, value=5
    )


    df_expos_filtered = df_exposures[df_exposures["Location"].isin(loc_selected)].copy()

    if len(df_expos_filtered) > 0:
        max_pol_year = df_expos_filtered["PolicyYear"].max()
        min_pol_year = max_pol_year - x_years + 1
        df_expos_filtered = df_expos_filtered[df_expos_filtered["PolicyYear"] >= min_pol_year]

    df_hurr_filtered = df_hurr[df_hurr["storm_name"].isin(storm_selected)].copy()

    # Filter Hurricanes by year if relevant
    if "year" in df_hurr.columns and len(year_selected) > 0:
        df_hurr_filtered = df_hurr_filtered[df_hurr_filtered["year"].isin(year_selected)]


    # --- Exposures Summary ---
    st.subheader("Filtered Exposures Summary")
    st.write(f"Locations: {loc_selected} | Past {x_years} Years | Rows: {len(df_expos_filtered)}")
    if len(df_expos_filtered) > 0:
        total_tiv = df_expos_filtered["TotalInsuredValue"].sum()
        st.write(f"**Total Insured Value**: {total_tiv:,.2f}")

    # --- Hurricane Summary ---
    st.subheader("Filtered Hurricanes Summary")
    st.write(f"Storms: {storm_selected} | Years: {year_selected if year_selected else 'All Available'}")
    st.write(f"Rows: {len(df_hurr_filtered)}")
    if len(df_hurr_filtered) > 0:
        max_ws = df_hurr_filtered["wind_speed"].max()
        st.write(f"**Max Wind Speed** among chosen storms: {max_ws} kt")

    st.subheader("Visualizing Exposures Over Years")
    if len(df_expos_filtered) > 0:
        chart_data = (
            df_expos_filtered.groupby("PolicyYear")["TotalInsuredValue"]
            .sum()
            .reset_index()
        )
        c = alt.Chart(chart_data).mark_bar().encode(
            x="PolicyYear:O",
            y="TotalInsuredValue:Q",
            tooltip=["PolicyYear", "TotalInsuredValue"]
        ).properties(width=600, height=400)
        st.altair_chart(c, use_container_width=True)

    st.subheader("Map of Selected Locations")
    if "Latitude" in df_expos_filtered.columns and "Longitude" in df_expos_filtered.columns:
        # 1) Create a copy with non-null lat/lon
        df_map = df_expos_filtered[["Latitude", "Longitude"]].dropna(how="any").copy()
        # 2) Rename columns to lowercase so Streamlit st.map() can detect them
        df_map.rename(columns={"Latitude": "latitude", "Longitude": "longitude"}, inplace=True)
        st.map(df_map)
    else:
        st.write("No latitude/longitude to display in Exposures.")

    st.subheader("Risk & Hurricanes Info")
    df_risk_filtered = df_exposures_risk[df_exposures_risk["Location"].isin(loc_selected)].copy()
    if len(df_risk_filtered) > 0:
        if "PolicyYear" in df_risk_filtered.columns:
            df_risk_filtered = df_risk_filtered[df_risk_filtered["PolicyYear"] >= min_pol_year]
        at_risk_count = df_risk_filtered["is_at_risk"].sum()
        st.write(f"**At-Risk Count** among selected: {at_risk_count} / {len(df_risk_filtered)}")
        st.write(df_risk_filtered.head(10))

if __name__ == "__main__":
    main()
