import pandas as pd
import numpy as np


def main():
    """
    1) 从 Excel 中读取 Exposures 表
    2) 去除空行、重复行
    3) 重命名关键列（如需要）
    4) 转换数据类型 & 处理异常值
    5) 输出干净的 exposures_cleaned.csv
    """

    # 1. 读取原始Exposures数据
    df_exposures = pd.read_excel(
        "original_data/case_data.xlsx",
        sheet_name="Exposures",
        skiprows=4,
        header=0
    )
    print("=== 原始 Exposures 前几行 ===")
    print(df_exposures.head())
    print(df_exposures.columns)

    # 2. 去除全空行、重复行
    df_exposures.dropna(how="all", inplace=True)
    df_exposures.drop_duplicates(inplace=True)

    # 3. 重命名列以避免空格或奇怪字符
    rename_dict = {
        "Location": "Location",
        "Latitude": "Latitude",
        "Longitude": "Longitude",
        "Total Insured Value": "TotalInsuredValue",
        "Premium": "Premium",
        "Losses - Non Catastrophe": "NonCatLoss",
        "PolicyYear": "PolicyYear"
    }
    df_exposures.rename(columns=rename_dict, inplace=True)

    # 4. 转换数据类型
    for col in ["TotalInsuredValue", "Premium", "NonCatLoss"]:
        df_exposures[col] = (
            df_exposures[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .astype(float)
        )

    # 5. 检查负值或异常值（示例：不应出现负的保费或负的TIV）
    df_exposures = df_exposures[df_exposures["TotalInsuredValue"] > 0]
    df_exposures = df_exposures[df_exposures["Premium"] >= 0]

    # 6. 打印检查
    print("\n=== 清洗后的 Exposures 简要统计 ===")
    print(df_exposures.describe())
    print(df_exposures.info())

    # 7. 存为 cleaned CSV (或Excel)
    output_path = "cleaned_data/exposures_cleaned.csv"
    df_exposures.to_csv(output_path, index=False)
    print(f"\n清洗后的 Exposures 已保存到: {output_path}")


if __name__ == "__main__":
    main()
