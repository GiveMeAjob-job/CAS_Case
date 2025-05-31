import pandas as pd


def load_sheet(sheet_name: str, usecols: str, skiprows: int) -> pd.DataFrame:
    """Read a sheet from the case_data Excel file."""
    return pd.read_excel(
        "original_data/case_data.xlsx",
        sheet_name=sheet_name,
        skiprows=skiprows,
        header=0,
        usecols=usecols,
    )


def main() -> None:
    df_exposures = pd.read_excel(
        "original_data/case_data.xlsx",
        sheet_name="Exposures",
        skiprows=4,
        header=0,
    )
    df_hurr1 = load_sheet("Historical Hurricane 1", "E:S", 2)
    df_hurr2 = load_sheet("Historical Hurricane 2", "E:K", 2)

    for name, df in {
        "exposures": df_exposures,
        "hurr1": df_hurr1,
        "hurr2": df_hurr2,
    }.items():
        df.dropna(how="all", inplace=True)
        df.drop_duplicates(inplace=True)
        print(f"[{name}] missing counts:\n{df.isna().sum()}")

    print("=== Historical Hurricane 1 (head) ===")
    print(df_hurr1.head())
    print("=== Historical Hurricane 2 (head) ===")
    print(df_hurr2.head())
    print("=== Exposures (head) ===")
    print(df_exposures.head())


if __name__ == "__main__":
    main()

