import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    """
    读取 exposures_cleaned.csv 后，
    1) 按年份汇总关键字段 (TIV, Premium, Losses)
    2) 计算 Loss Ratio, Loss Cost, Premium per $100 TIV
    3) 分别绘制随时间变化的趋势图
    """

    # =============== 1) 读取清洗后的 Exposures 数据 ===============
    df_exposures = pd.read_csv("cleaned_data/exposures_cleaned.csv")

    print("\n=== Exposures 前5行 ===")
    print(df_exposures.head())
    print(df_exposures.info())

    # =============== 2) 按年份汇总 TIV, Premium, Losses ===============
    # Management Request 1想看“所有地点总体”在每个 PolicyYear 的表现
    df_year = (
        df_exposures
        .groupby("PolicyYear", as_index=False)
        .agg({
            "TotalInsuredValue": "sum",
            "Premium": "sum",
            "NonCatLoss": "sum"  # 即 Losses - Non Catastrophe
        })
    )
    # 现在 df_year 包含 [PolicyYear, TotalInsuredValue, Premium, NonCatLoss]

    # =============== 3) 计算各项指标 ===============
    # 1) Loss Ratio = Losses / Premium
    df_year["LossRatio"] = df_year["NonCatLoss"] / df_year["Premium"]

    # 2) Loss Cost = Losses / TIV
    df_year["LossCost"] = df_year["NonCatLoss"] / df_year["TotalInsuredValue"]

    # 3) Premium per $100 TIV = (Premium / (TIV / 100)) = (Premium * 100 / TIV)
    df_year["Premium_per_100_TIV"] = (
        100 * df_year["Premium"] / df_year["TotalInsuredValue"]
    )

    # =============== 4) 画图：随时间的变化趋势 ===============
    plt.figure(figsize=(10,6))

    # a) Plot TIV
    sns.lineplot(
        data=df_year,
        x="PolicyYear", y="TotalInsuredValue",
        marker="o", label="TIV"
    )

    # b) Plot Premium
    sns.lineplot(
        data=df_year,
        x="PolicyYear", y="Premium",
        marker="o", label="Premium"
    )

    # 这样 TIV & Premium 会在同一张图上，数字量级如果相差太多，可能要用副Y轴。

    plt.title("TIV & Premium Over Time")
    plt.xlabel("Policy Year")
    plt.ylabel("Amount in $")
    plt.legend()
    plt.tight_layout()
    plt.savefig("pic/tiv_premium_over_time.png", dpi=300, bbox_inches="tight")
    plt.show()

    # 画 LossRatio:
    plt.figure(figsize=(8,5))
    sns.lineplot(
        data=df_year,
        x="PolicyYear", y="LossRatio",
        marker="o"
    )
    plt.title("Loss Ratio Over Time")
    plt.xlabel("Policy Year")
    plt.ylabel("Loss Ratio")
    plt.tight_layout()
    plt.savefig("pic/loss_ratio_over_time.png", dpi=300, bbox_inches="tight")
    plt.show()

    # 画 Premium_per_100_TIV:
    plt.figure(figsize=(8,5))
    sns.lineplot(
        data=df_year,
        x="PolicyYear", y="Premium_per_100_TIV",
        marker="o"
    )
    plt.title("Premium per $100 TIV Over Time")
    plt.xlabel("Policy Year")
    plt.ylabel("Premium per $100 TIV")
    plt.tight_layout()
    plt.savefig("pic/premium_per_100_tiv_over_time.png", dpi=300, bbox_inches="tight")
    plt.show()

    # 画 LossCost:
    plt.figure(figsize=(8,5))
    sns.lineplot(
        data=df_year,
        x="PolicyYear", y="LossCost",
        marker="o"
    )
    plt.title("Loss Cost Over Time")
    plt.xlabel("Policy Year")
    plt.ylabel("Loss Cost")
    plt.tight_layout()
    plt.savefig("pic/loss_cost_over_time.png", dpi=300, bbox_inches="tight")
    plt.show()

    # =============== 5) 输出结果表格 ===============
    df_year.to_csv("cleaned_data/exposures_summary_by_year.csv", index=False)
    print("\n年度汇总信息已存为 exposures_summary_by_year.csv")

if __name__ == "__main__":
    main()