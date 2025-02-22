import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches

df_exposures = pd.read_csv("cleaned_data/exposures_cleaned.csv")

plt.figure(figsize=(8,6))
plt.scatter(
    df_exposures["Longitude"],
    df_exposures["Latitude"],
    s=df_exposures["TotalInsuredValue"]/1000,
    alpha=0.5
)
plt.title("Concentration of TIV by Geography")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()


df_hurr = pd.read_csv("cleaned_data/hurr2_merged_with_h1_wind.csv")
print("Exposures columns:", df_exposures.columns.tolist())
print("Hurricane columns:", df_hurr.columns.tolist())


# 对 df_exposures 每条记录 与 df_hurr 做 cartesian join
df_exposure_hurr = df_exposures.assign(key=1).merge(df_hurr.assign(key=1), on="key")
df_exposure_hurr.drop(columns=["key"], inplace=True)

# 此时每个exposure与每个hurricane point配对，再筛选 1度范围
df_exposure_hurr["lat_diff"] = abs(df_exposure_hurr["Latitude"] - df_exposure_hurr["HurLat"])
df_exposure_hurr["lon_diff"] = abs(df_exposure_hurr["Longitude"] - df_exposure_hurr["HurLon"])
df_exposure_hurr["is_at_risk"] = (df_exposure_hurr["lat_diff"] <= 1.0) & (df_exposure_hurr["lon_diff"] <= 1.0)

# 再 groupby location, 若有任何True则该地点算 "at risk"
df_risk = (
    df_exposure_hurr.groupby("Location")["is_at_risk"]
    .max()  # max()相当于只要有1个True就为True
    .reset_index()
)

# 与原exposures合并
df_exposures_risk = pd.merge(df_exposures, df_risk, on="Location", how="left")
df_exposures_risk["is_at_risk"] = df_exposures_risk["is_at_risk"].fillna(False)


# TIV at risk
tiv_at_risk = df_exposures_risk.loc[df_exposures_risk["is_at_risk"], "TotalInsuredValue"].sum()
tiv_total = df_exposures_risk["TotalInsuredValue"].sum()

print(f"Total TIV: {tiv_total}, At-Risk TIV: {tiv_at_risk}, Ratio: {tiv_at_risk/tiv_total:.2%}")


# A) 标记 impact_wind_speed (可以直接等于 wind_speed)
df_exposure_hurr["impact_wind_speed"] = df_exposure_hurr["wind_speed"]

# B) 只取 is_at_risk=True 的那些行
df_impacted = df_exposure_hurr[df_exposure_hurr["is_at_risk"]].copy()

df_hurr_impact_summary = (
    df_impacted.groupby("storm_name")["impact_wind_speed"]
    .max()  # 取最大风速
    .reset_index(name="MaxWind_AtRisk")
)

print("\n=== Hurricanes that impacted the portfolio (top wind speed) ===")
print(df_hurr_impact_summary.head(20))

df_loc_storm = (
    df_impacted.groupby(["Location","storm_name"])["impact_wind_speed"]
    .max()  # 同样取最大风速
    .reset_index(name="MaxWindAtLocation")
)

print("\n=== Per location & storm, the max wind speed ===")
print(df_loc_storm.head(20))

df_hurr_impact_summary.to_csv("cleaned_data/hurr_impact_summary.csv", index=False)
df_loc_storm.to_csv("cleaned_data/exposures_loc_storm_wind.csv", index=False)


# df_loc_storm: columns = ["Location","storm_name","MaxWindAtLocation"]
df_loc_storm_agg = (
    df_loc_storm.groupby("Location")["MaxWindAtLocation"]
    .max()
    .reset_index(name="MaxWindNearLocation")
)

df_exposures_risk2 = pd.merge(
    df_exposures_risk,          # 有 TIV, is_at_risk
    df_loc_storm_agg,           # 有每个地点的 max wind
    on="Location",
    how="left"
)
# 若某地点没遇到任何风暴，这里MaxWindNearLocation会是NaN
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
df_exposures_risk2["PML_Category"] = df_exposures_risk2["PML_Category"].fillna("Medium")


df_pml_summary = (
    df_exposures_risk2.groupby("PML_Category")["TotalInsuredValue"]
    .sum()
    .reset_index(name="TIV_Sum")
)
print(df_pml_summary)
print(df_exposures_risk2.columns)
print(df_exposures_risk.columns)

# ============ Angel从这里开始，不同风险等级，不同颜色 ============
# 定义风险等级到颜色的映射
color_map = {
    "High": "red",
    "Medium": "orange",
    "Low": "green"
}

# ============ 1) 绘制地点散点图 ============
plt.figure(figsize=(10,8))

# 按 PML_Category 分组绘制
for category, group_data in df_exposures_risk2.groupby("PML_Category"):
    category = str(category).strip()
    plt.scatter(
        group_data["Longitude"],
        group_data["Latitude"],
        s=group_data["TotalInsuredValue"] / 1000,  # 气泡大小可自行调整
        c=color_map.get(category, "gray"),         # 若找不到就默认灰
        alpha=0.6,
        label=f"{category} Risk"
    )

plt.legend(title="Risk Level")
plt.title("Insurance Asset Distribution by Risk Category")
plt.xlabel("Longitude")
plt.ylabel("Latitude")

plt.show()

# ============ 2) 在图上叠加飓风范围（圆形） ============
# 思路：以 (HurLon, HurLat) 为圆心，wind_radius 为半径
# 半径可做适当缩放，否则可能过大/过小

scaling_factor = 0.1  # 用于调节 wind_radius 到图上的实际显示；可根据数据范围试验
for idx, storm_row in df_hurr.iterrows():
    x_center = storm_row["HurLon"]
    y_center = storm_row["HurLat"]
    radius = storm_row["wind_radius"] * scaling_factor  # 缩放

    # 可根据 wind_speed 调节 alpha 或颜色深浅
    # 例如：越大的 wind_speed，越深的透明度
    wind_speed = storm_row["wind_speed"]
    # 用一个简单的映射： 0~64 对应 alpha 0.1~0.4
    alpha_value = 0.1 + 0.3 * (wind_speed / 64.0)
    if alpha_value > 0.4:
        alpha_value = 0.4

    circle = patches.Circle(
        (x_center, y_center),
        radius=radius,
        facecolor="blue",
        alpha=alpha_value,
        edgecolor=None
    )
    plt.gca().add_patch(circle)

# ============ 3) 设置图例、标题、坐标 ============
plt.title("Risk Categories & Storm Overlaps")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.show()


