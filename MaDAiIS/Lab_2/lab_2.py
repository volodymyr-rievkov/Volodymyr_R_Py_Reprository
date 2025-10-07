import pandas as pd
from scipy.stats import ttest_1samp, ttest_ind
import matplotlib.pyplot as plt
import os
import math

RELATIVE_PATH = "PythonApplications/MaDAiIS/Lab_2"
DATASET_NAME = "DataScience_salaries_2025.csv"
PATH = f"{RELATIVE_PATH}/{DATASET_NAME}"
YELLOW = "\033[33m"
RED = "\033[31m"
GREEN = "\033[32m"
RESET = "\033[0m"
COLUMN = "salary_in_usd"
GROUP_COLUMN = "job_title"
SAMPLES = [["Software Developer", "Product Analyst"], ["AI Developer", "Python Developer"]]

def read_dataset(dataset_path=PATH):
    dataset_name = dataset_path.split("/")[-1].replace(".csv", "")
    print(f"\n{'='*10} Dataset: {dataset_name} {'='*10}\n")
    return pd.read_csv(dataset_path)

def analyze_dataset(dataset):
    print(f"{YELLOW}Dataset shape: {RESET}{dataset.shape[0]} rows x {dataset.shape[1]} columns")
    
    print(f"\n{YELLOW}Columns:{RESET}\n")
    for i, col in enumerate(dataset.columns, 1):
        print(f"{i}. {col}")
    
    print(f"\n{YELLOW}Dataset info:{RESET}\n")
    dataset.info()
    
    print(f"\n{YELLOW}Numerical description:{RESET}\n")
    print(dataset.describe().T)
    
    print(f"\n{YELLOW}First 10 rows:{RESET}\n")
    print(dataset.head(10))

def test_hypotesis(dataset, H0, column=COLUMN, alternative="two-sided"):
    P_LIMIT = 0.05

    data = dataset[column].dropna()
    mean = data.mean()
    std = data.std()

    t_stat, p_value_two_sided = ttest_1samp(data, popmean=H0)

    if alternative == "two-sided":
        p_value = p_value_two_sided
        alt_label = "Mean = H0"
    elif alternative == "greater":
        p_value = p_value_two_sided / 2 if t_stat > 0 else 1 - p_value_two_sided / 2
        alt_label = "Mean < H0"
    elif alternative == "less":
        p_value = p_value_two_sided / 2 if t_stat < 0 else 1 - p_value_two_sided / 2
        alt_label = "Mean > H0"
    else:
        raise ValueError("alternative must be 'two-sided', 'greater', or 'less'")

    print(f"\n{YELLOW}Hypothesis Testing for column '{column}' ({alternative}){RESET}")
    print(f"Mean: {mean:.2f}, Std: {std:.2f}, H0: {H0:.2f}")
    print(f"{RED if p_value < P_LIMIT else GREEN}T-statistic: {t_stat:.3f}, P-value: {p_value:.3f}{RESET}")

    if p_value < P_LIMIT:
        print(f"{RED}H0 rejected ({alt_label}){RESET}")
    else:
        print(f"{GREEN}H0 accepted ({alt_label}){RESET}")

    plot_dir = f"{RELATIVE_PATH}/plots"
    os.makedirs(plot_dir, exist_ok=True)

    plt.figure(figsize=(10,6))
    plt.hist(data, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    plt.axvline(mean, color='green', linestyle='dashed', linewidth=2, label=f'Mean: {mean:.2f}')
    plt.axvline(H0, color='red', linestyle='dashed', linewidth=2, label=f'H0: {H0:.2f}')
    plt.title(f"Histogram of {column} ({alternative})")
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_dir, f"{column}_H0_{int(H0)}.png")  
    plt.savefig(plot_path)
    plt.close()

    print(f"Histogram saved to {plot_path}")

def mean_values_by_column_subplots(dataset, group_column, value_column=COLUMN, batch_size=10):
    mean_by_group = (
        dataset.groupby(group_column)[value_column]
        .mean()
        .sort_values(ascending=False)
    )

    print(f"\n{YELLOW}Average {value_column} by {group_column}{RESET}")
    print(mean_by_group)

    n_groups = math.ceil(len(mean_by_group) / batch_size)
    _, axes = plt.subplots(n_groups, 1, figsize=(10, n_groups * 5))

    if n_groups == 1:
        axes = [axes]

    for i, ax in enumerate(axes):
        start = i * batch_size
        end = start + batch_size
        batch = mean_by_group.iloc[start:end]

        ax.barh(batch.index, batch.values, color='skyblue', edgecolor='black')
        ax.set_xlabel(f"Average {value_column}")
        ax.set_ylabel(group_column)
        ax.set_title(f"{group_column} ({start+1}-{min(end, len(mean_by_group))})")
        ax.invert_yaxis()

        for j, v in enumerate(batch.values):
            ax.text(v, j, f"{v:.0f}", va='center', ha='left', fontsize=8)

    plt.tight_layout()

    plot_dir = f"{RELATIVE_PATH}/plots"
    os.makedirs(plot_dir, exist_ok=True)
    plot_path = os.path.join(plot_dir, f"mean_{group_column}_subplots.png")
    plt.savefig(plot_path)
    plt.close()

    print(f"Subplot chart saved to {plot_path}")
 
def test_samples(dataset, column=COLUMN, group_col="experience_level", group1="MI", group2="SE", alternative="two-sided"):

    P_LIMIT = 0.05
    data1 = dataset[dataset[group_col] == group1][column].dropna()
    data2 = dataset[dataset[group_col] == group2][column].dropna()

    t_stat, p_value_two_sided = ttest_ind(data1, data2, equal_var=False)  

    if alternative == "two-sided":
        p_value = p_value_two_sided
        alt_label = f"{group1} = {group2}"
    elif alternative == "greater":
        t_stat_signed = data1.mean() - data2.mean()
        p_value = p_value_two_sided / 2 if t_stat_signed > 0 else 1 - p_value_two_sided / 2
        alt_label = f"{group1} < {group2}"
    elif alternative == "less":
        t_stat_signed = data1.mean() - data2.mean()
        p_value = p_value_two_sided / 2 if t_stat_signed < 0 else 1 - p_value_two_sided / 2
        alt_label = f"{group1} > {group2}"
    else:
        raise ValueError("alternative must be 'two-sided', 'greater', or 'less'")

    print(f"\n{YELLOW}Comparing {group1} vs {group2} for column '{column}' ({alternative}){RESET}")
    print(f"Mean {group1}: {data1.mean():.2f}, Mean {group2}: {data2.mean():.2f}")
    print(f"{RED if p_value < P_LIMIT else GREEN}T-statistic: {t_stat:.3f}, P-value: {p_value:.3f}{RESET}")

    if p_value < P_LIMIT:
        print(f"{RED}H rejected ({alt_label}){RESET}")
    else:
        print(f"{GREEN}H accepted ({alt_label}){RESET}")

    plot_dir = f"{RELATIVE_PATH}/plots"
    os.makedirs(plot_dir, exist_ok=True)
    plt.figure(figsize=(10,6))
    plt.hist(data1, bins=30, alpha=0.6, label=group1, color='skyblue', edgecolor='black')
    plt.hist(data2, bins=30, alpha=0.6, label=group2, color='orange', edgecolor='black')
    plt.axvline(data1.mean(), color='blue', linestyle='dashed', linewidth=2, label=f'{group1} mean')
    plt.axvline(data2.mean(), color='red', linestyle='dashed', linewidth=2, label=f'{group2} mean')
    plt.title(f"{group1} vs {group2} ({alternative})")
    plt.xlabel(column)
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(plot_dir, f"{group1}_vs_{group2}.png")  
    plt.savefig(plot_path)
    plt.close()
    print(f"Histogram saved to {plot_path}")

if __name__ == "__main__":
    dataset = read_dataset()
    analyze_dataset(dataset)

    input("\nPress Enter to start testing H0s...")

    H0s = [158000, 150000]
    for i, H0 in enumerate(H0s):
        test_hypotesis(dataset, H0, column=COLUMN, alternative="two-sided")
        test_hypotesis(dataset, H0, column=COLUMN, alternative="greater")
        test_hypotesis(dataset, H0, column=COLUMN, alternative="less")
        if(i < len(H0s) - 1):
            input("\nPress Enter to continue...")

    input("\nPress Enter to start testing samples...")

    mean_values_by_column_subplots(dataset, group_column=GROUP_COLUMN, value_column=COLUMN)
    for i, sample in enumerate(SAMPLES): 
        test_samples(dataset, column=COLUMN, group_col=GROUP_COLUMN, group1=sample[0], group2=sample[1], alternative="two-sided")
        test_samples(dataset, column=COLUMN, group_col=GROUP_COLUMN, group1=sample[0], group2=sample[1], alternative="greater")
        test_samples(dataset, column=COLUMN, group_col=GROUP_COLUMN, group1=sample[0], group2=sample[1], alternative="less")
        if(i < len(SAMPLES) - 1):
            input("\nPress Enter to continue...")
