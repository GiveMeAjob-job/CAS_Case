import pandas as pd
import numpy as np

df = pd.read_excel('original_data/case_data.xlsx')

df_hurr1 = pd.read_excel(
    'original_data/case_data.xlsx',
    sheet_name="Historical Hurricane 1",
    skiprows=2,
    header=0,
    usecols="E:S"
)

df_hurr2 = pd.read_excel(
    'original_data/case_data.xlsx',
    sheet_name="Historical Hurricane 2",
    skiprows=2,
    header=0,
    usecols="E:K"
)

df_exposures = pd.read_excel(
    'original_data/case_data.xlsx',
    sheet_name="Exposures",
    skiprows=4,
    header=0
)

sheet_names = [
    "Historical Hurricane 1",
    "Historical Hurricane 2",
    "Exposures",
    "Management Request 1",
    "Management Request 2",
    "UW Report"
]

df_exposures.dropna(how='all', inplace=True)
df_exposures.drop_duplicates(inplace=True)

df_hurr1.dropna(how='all', inplace=True)
df_hurr1.drop_duplicates(inplace=True)

df_hurr2.dropna(how='all', inplace=True)
df_hurr2.drop_duplicates(inplace=True)

#  df_exposures.to_csv('cleand_data/exposures_cleaned.csv', index=False)
#  df_exposures.to_csv('cleand_data/hurr1.csv', index=False)
#  df_exposures.to_csv('cleand_data/hurr2.csv', index=False)

print(df_hurr1.isna().sum())
print(df_hurr2.isna().sum())
print(df_exposures.isna().sum())

print("=== Historical Hurricane 1 (前5行) ===")
print(df_hurr1.head())
print(df_hurr1.columns)
print("\n=== Historical Hurricane 2 (前5行) ===")
print(df_hurr2.head())
print(df_hurr2.columns)
print("\n=== Exposures (前5行) ===")
print(df_exposures.head())
print(df_exposures.columns)