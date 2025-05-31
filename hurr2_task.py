import pandas as pd
import numpy as np

# 读取已经清洗完成的 hurr1 数据
df_hurr1 = pd.read_csv("cleaned_data/hurr1_cleaned.csv")
print("【df_hurr1】", df_hurr1.shape)
print(df_hurr1.head())

df_hurr2 = pd.read_excel(
    "original_data/case_data.xlsx",
    sheet_name="Historical Hurricane 2",
    skiprows=2,
    header=0,
    usecols="E:K"
)
print("【df_hurr2】", df_hurr2.shape)
print(df_hurr2.head())

print("【df_hurr2】列名：", df_hurr2.columns.tolist())

rename_dict_h2 = {
    "storm_name": "storm_name",
    "date": "date",
    "longitude": "HurLon",
    "latitude": "HurLat",

}
df_hurr2.rename(columns=rename_dict_h2, inplace=True)


# (A) 在Hurr1中按风暴名称分组，提取最大WMO风速
df_hurr1_max = (
    df_hurr1.groupby("NAME")["WMO_WIND"]
    .max()
    .reset_index(name="max_wind_h1")
)

# (B) 合并到 Hurr2
df_hurr2_merged = pd.merge(
    df_hurr2,
    df_hurr1_max,
    left_on="storm_name",
    right_on="NAME",
    how="left"
)

print("\n=== df_hurr2 with Hurr1 wind ===")
print(df_hurr2_merged.head(10))

df_hurr2_merged["storm_area_mi2"] = np.pi * (df_hurr2_merged["wind_radius"] ** 2)

# 每个风暴的最大/平均面积：
storm_area = (
    df_hurr2_merged.groupby("storm_name")["storm_area_mi2"]
    .mean()
    .reset_index(name="avg_area_mi2")
)
print("\n=== 每个风暴的平均面积 (mi²) ===")
print(storm_area.head(10))

storm_area.to_csv("cleaned_data/hurr2_storm_area.csv", index=False)


# (A) Hurr1最高风速
df_hurr1_max = (
    df_hurr1.groupby("NAME")["WMO_WIND"]
    .max()
    .reset_index(name="max_wind_h1")
)

# (B) Hurr2最高风速
df_hurr2_max = (
    df_hurr2.groupby("storm_name")["wind_speed"]
    .max()
    .reset_index(name="max_wind_h2")
)

# (C) 合并
wind_recon = pd.merge(
    df_hurr1_max,
    df_hurr2_max,
    left_on="NAME",
    right_on="storm_name",
    how="inner"
)

# (D) 做差
wind_recon["wind_diff"] = wind_recon["max_wind_h1"] - wind_recon["max_wind_h2"]

print("\n=== 对比Hurr1与Hurr2的最高风速 ===")
print(wind_recon.head(20))

wind_recon.to_csv("cleaned_data/hurr_wind_reconciliation.csv", index=False)

df_hurr2_merged.to_csv("cleaned_data/hurr2_merged_with_h1_wind.csv", index=False)
