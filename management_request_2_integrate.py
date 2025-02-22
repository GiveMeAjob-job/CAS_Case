import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def main():
    # 1) 读取数据
    df_hurr1 = pd.read_csv("cleaned_data/hurr1_cleaned.csv")
    df_hurr2 = pd.read_excel(
        "original_data/case_data.xlsx",
        sheet_name="Historical Hurricane 2",
        skiprows=2,
        header=0,
        usecols="E:K"
    )

    # 2) 重命名字段以便统一处理
    df_hurr2.rename(columns={
        "storm_name": "storm_name",
        "date": "date",
        "longitude": "HurLon",
        "latitude": "HurLat"
    }, inplace=True)

    # 3) 合并 df_hurr1 的最大风速到 df_hurr2
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

    # 4) 计算飓风覆盖面积（仅做示例）
    df_hurr2_merged["storm_area_mi2"] = np.pi * (df_hurr2_merged["wind_radius"] ** 2)

    # 5) 做一个对照：df_hurr1_max & df_hurr2 wind speed
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

    # 6) 保存部分中间结果（可选）
    df_hurr2_merged.to_csv("cleaned_data/hurr2_merged_with_h1_wind.csv", index=False)
    wind_recon.to_csv("cleaned_data/hurr_wind_reconciliation.csv", index=False)

    # 7) 读取并合并暴露数据
    df_exposures = pd.read_csv("cleaned_data/exposures_cleaned.csv")
    df_exposure_hurr = df_exposures.assign(key=1).merge(df_hurr2_merged.assign(key=1), on="key")
    df_exposure_hurr.drop(columns=["key"], inplace=True)

    # 8) 计算地理距离近似（简单的经纬度差）
    df_exposure_hurr["lat_diff"] = abs(df_exposure_hurr["Latitude"] - df_exposure_hurr["HurLat"])
    df_exposure_hurr["lon_diff"] = abs(df_exposure_hurr["Longitude"] - df_exposure_hurr["HurLon"])
    df_exposure_hurr["is_at_risk"] = (
        (df_exposure_hurr["lat_diff"] <= 1.0) &
        (df_exposure_hurr["lon_diff"] <= 1.0)
    )

    # 9) 按照 Location 区分是否 at_risk
    df_risk = (
        df_exposure_hurr.groupby("Location")["is_at_risk"]
        .max()
        .reset_index()
    )
    df_exposures_risk = pd.merge(df_exposures, df_risk, on="Location", how="left")
    df_exposures_risk["is_at_risk"] = df_exposures_risk["is_at_risk"].fillna(False)

    # 10) 计算总暴露 & 风险暴露
    tiv_at_risk = df_exposures_risk.loc[df_exposures_risk["is_at_risk"], "TotalInsuredValue"].sum()
    tiv_total = df_exposures_risk["TotalInsuredValue"].sum()
    print(f"Total TIV: {tiv_total}, At-Risk TIV: {tiv_at_risk}, Ratio: {tiv_at_risk / tiv_total:.2%}")

    df_exposures_risk.to_csv("cleaned_data/exposures_risk.csv", index=False)

    # 11) 决定以 df_exposure_hurr["wind_speed"] 作为最终影响风速
    df_exposure_hurr["impact_wind_speed"] = df_exposure_hurr["wind_speed"]

    # 12) 选出真正落在飓风范围内的记录
    df_impacted = df_exposure_hurr[df_exposure_hurr["is_at_risk"]].copy()

    # 13) 每个飓风在投保点附近的最大风速
    df_hurr_impact_summary = (
        df_impacted.groupby("storm_name")["impact_wind_speed"]
        .max()
        .reset_index(name="MaxWind_AtRisk")
    )
    print("\n=== Hurricanes that impacted the portfolio (top wind speed) ===")
    print(df_hurr_impact_summary.head(20))

    # 14) 每个地点、每个飓风的最大风速
    df_loc_storm = (
        df_impacted.groupby(["Location", "storm_name"])["impact_wind_speed"]
        .max()
        .reset_index(name="MaxWindAtLocation")
    )
    print("\n=== Per location & storm, the max wind speed ===")
    print(df_loc_storm.head(20))

    df_hurr_impact_summary.to_csv("cleaned_data/hurr_impact_summary.csv", index=False)
    df_loc_storm.to_csv("cleaned_data/exposures_loc_storm_wind.csv", index=False)

    # 15) 把每个地点可能有多次风暴的最大风速合并回暴露表
    df_loc_storm_agg = (
        df_loc_storm.groupby("Location")["MaxWindAtLocation"]
        .max()
        .reset_index(name="MaxWindNearLocation")
    )

    df_exposures_risk2 = pd.merge(
        df_exposures_risk,
        df_loc_storm_agg,
        on="Location",
        how="left"
    )
    df_exposures_risk2["MaxWindNearLocation"].fillna(0, inplace=True)

    # 16) 定义简单的 PML 分类
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

    # ============ 以下示例为“年度风速变化”相关的新逻辑 ============

    # (A) 将 df_hurr2_merged 中的 date 解析为 datetime，并提取 year
    #     假设 df_hurr2_merged['date'] 中已有有效的日期字符串
    df_hurr2_merged["date"] = pd.to_datetime(df_hurr2_merged["date"], errors="coerce")
    df_hurr2_merged["year"] = df_hurr2_merged["date"].dt.year

    # (B) 按年份汇总：可选择 max、mean、median 等，这里演示取“平均风速”做参考
    df_wind_by_year = (
        df_hurr2_merged.groupby("year")["wind_speed"]
        .mean()  # 也可改成 .max()
        .reset_index(name="MeanWindSpeed")
    )

    # (C) 根据年度平均风速再做一个简单分类（仅示例）
    def categorize_wind_speed(speed):
        if speed >= 64:
            return "High"
        elif speed >= 50:
            return "Medium"
        else:
            return "Low"

    df_wind_by_year["WindSpeedCategory"] = df_wind_by_year["MeanWindSpeed"].apply(categorize_wind_speed)

    print("\n=== Yearly Wind Speed Summary ===")
    print(df_wind_by_year)

    # (D) （可选）可做一个年度风速变化的可视化
    plt.figure(figsize=(8, 5))
    plt.plot(df_wind_by_year["year"], df_wind_by_year["MeanWindSpeed"], marker="o")
    plt.title("Change in Average Wind Speed Over Years")
    plt.xlabel("Year")
    plt.ylabel("Average Wind Speed")
    plt.grid(True)
    plt.show()

    # ============ 以下是原先的风险可视化示例（地理散点 & 圆形覆盖）===========
    # 定义风险等级到颜色的映射
    color_map = {
        "High": "red",
        "Medium": "orange",
        "Low": "green"
    }

    plt.figure(figsize=(10, 8))

    # 按 PML_Category 分组绘制散点
    for category, group_data in df_exposures_risk2.groupby("PML_Category"):
        plt.scatter(
            group_data["Longitude"],
            group_data["Latitude"],
            s=group_data["TotalInsuredValue"] / 1000,  # 气泡大小可自行调整
            c=color_map.get(category, "gray"),         # 若找不到就默认灰
            alpha=0.6,
            label=f"{category} Risk"
        )

    # 在图上叠加飓风范围圆圈（以 df_hurr2_merged 为例）
    scaling_factor = 0.1  # 用于调节 wind_radius 到图上的实际显示
    for idx, storm_row in df_hurr2_merged.iterrows():
        if pd.isnull(storm_row["HurLon"]) or pd.isnull(storm_row["HurLat"]):
            continue
        x_center = storm_row["HurLon"]
        y_center = storm_row["HurLat"]
        radius = storm_row["wind_radius"] * scaling_factor

        # 根据 wind_speed 调节 alpha 或颜色深浅（仅做示例）
        wind_speed = storm_row["wind_speed"]
        alpha_value = 0.1 + 0.3 * (wind_speed / 64.0)
        alpha_value = min(alpha_value, 0.4)

        circle = patches.Circle(
            (x_center, y_center),
            radius=radius,
            facecolor="blue",
            alpha=alpha_value,
            edgecolor=None
        )
        plt.gca().add_patch(circle)

    plt.title("Risk Categories & Storm Overlaps")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
