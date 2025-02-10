import pandas as pd
import numpy as np


def main():
    df_hurr1 = pd.read_csv("cleaned_data/hurr1_cleaned.csv")
    df_hurr2 = pd.read_excel(
        "original_data/case_data.xlsx",
        sheet_name="Historical Hurricane 2",
        skiprows=2,
        header=0,
        usecols="E:K"
    )

    df_hurr2.rename(columns={
        "storm_name": "storm_name",
        "date": "date",
        "longitude": "HurLon",
        "latitude": "HurLat"
    }, inplace=True)

    df_hurr1_max = (
        df_hurr1.groupby("NAME")["WMO_WIND"]
        .max()
        .reset_index(name="max_wind_h1")
    )
    df_hurr2_merged = pd.merge(
        df_hurr2,
        df_hurr1_max,
        left_on="storm_name",
        right_on="NAME",
        how="left"
    )

    df_hurr2_merged["storm_area_mi2"] = np.pi * (df_hurr2_merged["wind_radius"] ** 2)

    df_hurr2_max = (
        df_hurr2.groupby("storm_name")["wind_speed"]
        .max()
        .reset_index(name="max_wind_h2")
    )
    wind_recon = pd.merge(
        df_hurr1_max, df_hurr2_max,
        left_on="NAME", right_on="storm_name", how="inner"
    )
    wind_recon["wind_diff"] = wind_recon["max_wind_h1"] - wind_recon["max_wind_h2"]

    df_hurr2_merged.to_csv("cleaned_data/hurr2_merged_with_h1_wind.csv", index=False)
    wind_recon.to_csv("cleaned_data/hurr_wind_reconciliation.csv", index=False)

    df_exposures = pd.read_csv("cleaned_data/exposures_cleaned.csv")
    df_exposure_hurr = df_exposures.assign(key=1).merge(df_hurr2_merged.assign(key=1), on="key")
    df_exposure_hurr.drop(columns=["key"], inplace=True)

    df_exposure_hurr["lat_diff"] = abs(df_exposure_hurr["Latitude"] - df_exposure_hurr["HurLat"])
    df_exposure_hurr["lon_diff"] = abs(df_exposure_hurr["Longitude"] - df_exposure_hurr["HurLon"])
    df_exposure_hurr["is_at_risk"] = (
            (df_exposure_hurr["lat_diff"] <= 1.0) &
            (df_exposure_hurr["lon_diff"] <= 1.0)
    )

    # groupby location => is_at_risk
    df_risk = (
        df_exposure_hurr.groupby("Location")["is_at_risk"]
        .max()
        .reset_index()
    )
    df_exposures_risk = pd.merge(df_exposures, df_risk, on="Location", how="left")
    df_exposures_risk["is_at_risk"] = df_exposures_risk["is_at_risk"].fillna(False)

    tiv_at_risk = df_exposures_risk.loc[df_exposures_risk["is_at_risk"], "TotalInsuredValue"].sum()
    tiv_total = df_exposures_risk["TotalInsuredValue"].sum()
    print(f"Total TIV: {tiv_total}, At-Risk TIV: {tiv_at_risk}, Ratio: {tiv_at_risk / tiv_total:.2%}")

    df_exposures_risk.to_csv("cleaned_data/exposures_risk.csv", index=False)

    df_exposure_hurr["impact_wind_speed"] = df_exposure_hurr["wind_speed"]
    df_impacted = df_exposure_hurr[df_exposure_hurr["is_at_risk"]].copy()

    df_hurr_impact_summary = (
        df_impacted.groupby("storm_name")["impact_wind_speed"]
        .max()
        .reset_index(name="MaxWind_AtRisk")
    )
    print("\n=== Hurricanes that impacted the portfolio (top wind speed) ===")
    print(df_hurr_impact_summary.head(20))

    df_loc_storm = (
        df_impacted.groupby(["Location", "storm_name"])["impact_wind_speed"]
        .max()
        .reset_index(name="MaxWindAtLocation")
    )
    print("\n=== Per location & storm, the max wind speed ===")
    print(df_loc_storm.head(20))

    df_hurr_impact_summary.to_csv("cleaned_data/hurr_impact_summary.csv", index=False)
    df_loc_storm.to_csv("cleaned_data/exposures_loc_storm_wind.csv", index=False)

    df_loc_storm_agg = (
        df_loc_storm.groupby("Location")["MaxWindAtLocation"]
        .max()
        .reset_index(name="MaxWindNearLocation")
    )

    df_exposures_risk2 = pd.merge(
        df_exposures_risk,  # 有 TIV, is_at_risk
        df_loc_storm_agg,  # 每个地点的 max wind
        on="Location",
        how="left"
    )
    df_exposures_risk2["MaxWindNearLocation"].fillna(0, inplace=True)


    def categorize_pml(row):
        tiv = row["TotalInsuredValue"]
        at_risk = row["is_at_risk"]
        wind = row["MaxWindNearLocation"]

        if tiv > 500_000 and at_risk and wind >= 64:
            return "High"
        elif tiv > 100_000 or wind >= 50:
            return "Medium"
        else:
            return "Low"

    df_exposures_risk2["PML_Category"] = df_exposures_risk2.apply(categorize_pml, axis=1)

    df_pml_summary = (
        df_exposures_risk2.groupby("PML_Category")["TotalInsuredValue"]
        .sum()
        .reset_index(name="TIV_Sum")
    )
    print("\n=== PML Summary (High/Medium/Low) ===")
    print(df_pml_summary)

    df_exposures_risk2.to_csv("cleaned_data/exposures_pml.csv", index=False)


if __name__ == "__main__":
    main()
