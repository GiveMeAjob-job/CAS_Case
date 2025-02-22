import pandas as pd

df_hurr1 = pd.read_excel(
    "original_data/case_data.xlsx",
    sheet_name="Historical Hurricane 1",
    skiprows=2,
    header=0,
    usecols="E:S"
)

print("原始列名：", df_hurr1.columns.tolist())

rename_dict = {
    ' ': 'SID',
    'Year': 'SEASON',
    ' .1': 'NUMBER',
    ' .2': 'BASIN',
    ' .3': 'SUBBASIN',
    ' .4': 'NAME',
    ' .5': 'ISO_TIME',
    ' .6': 'NATURE',
    'degrees_north': 'LAT',
    'degrees_east': 'LON',
    'kts': 'WMO_WIND',
    'mb': 'WMO_PRES',
    ' .7': 'WMO_AGENCY',
    ' .8': 'TRACK_TYPE',
    'km': 'DIST2LAND'
}
df_hurr1.rename(columns=rename_dict, inplace=True)

print("重命名后列名：", df_hurr1.columns.tolist())

df_hurr1 = df_hurr1[
    (df_hurr1["SEASON"] >= 1985) & (df_hurr1["SEASON"] <= 2020)
]

print(df_hurr1.head(10))


storm_count = (
    df_hurr1.groupby(["SEASON", "NATURE"])["SID"]
    .nunique()
    .reset_index(name="StormCount")
)

print("\n=== 按年份 & 风暴类型，风暴数统计 ===")
print(storm_count.head(20))

storm_count.to_csv("cleaned_data/storm_count_by_year_type.csv", index=False)

max_wind_per_storm = (
    df_hurr1.groupby("SID")["WMO_WIND"]
    .max()
    .reset_index(name="MaxWind")
)

print("\n=== 每个风暴的最大风速 ===")
print(max_wind_per_storm.head(20))
max_wind_per_storm.to_csv("cleaned_data/max_wind_per_storm.csv", index=False)

import matplotlib.pyplot as plt
import seaborn as sns

df_year_storm = (
    df_hurr1.groupby(["SEASON", "SID"])["WMO_WIND"]
    .max()
    .reset_index(name="MaxWind")
)

plt.figure(figsize=(10,6))
sns.lineplot(data=df_year_storm, x="SEASON", y="MaxWind", hue="SID", marker="o")
plt.title("Change in Maximum Wind Speed per Storm over Time (1985~2020)")
plt.xlabel("Year")
plt.ylabel("Maximum Wind Speed")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left", ncol=1)

plt.tight_layout()
#plt.show()

df_hurr1.to_csv("cleaned_data/hurr1_cleaned.csv", index=False)


import pandas as pd
import matplotlib.pyplot as plt

# 读取数据
file_path = "cleaned_data/storm_count_by_year_type.csv"  # 请替换为你的 CSV 文件路径
df = pd.read_csv(file_path)

# 确保数据格式正确
df.columns = df.columns.str.strip()  # 去除列名可能的空格
df['SEASON'] = df['SEASON'].astype(int)
df['StormCount'] = df['StormCount'].astype(int)

# 按 NATURE 进行分组，并绘制不同风暴类型随时间变化的趋势
plt.figure(figsize=(12, 6))

for nature, group in df.groupby('NATURE'):
    plt.plot(group['SEASON'], group['StormCount'], marker='o', label=nature)

plt.xlabel("Year")
plt.ylabel("Hurricane Count")
plt.title("Hurricane Counts by Type Over Time")
plt.legend(title="Hurricane Type")
plt.grid(True)
plt.show()
