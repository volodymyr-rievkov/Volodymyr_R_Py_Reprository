import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np
import os
from loguru import logger

RELATIVE_PATH = "PythonApplications/MaDAiIS/Lab_1"
DATASET_NAME = "income_expenses_due_to_age"
CSV_PATH = f"{RELATIVE_PATH}/{DATASET_NAME}.csv"
LOG_PATH = f"{RELATIVE_PATH}/{DATASET_NAME}.txt"
PLOTS_DIR = f"{RELATIVE_PATH}/{DATASET_NAME}_plots"
os.makedirs(PLOTS_DIR, exist_ok=True)

COLUMNS = ['Age', 'Income']

RED     = "\033[31m"
GREEN   = "\033[32m"
RESET   = "\033[0m"


def check_histogram(ax, x, var_name, stage="Original"):
    sns.histplot(x, kde=True, bins=30, ax=ax)
    ax.set_title(f"Histogram {var_name} ({stage})")
    ax.set_xlabel(var_name)
    ax.set_ylabel("Frequency")


def check_qqplot(ax, x, var_name, stage="Original"):
    stats.probplot(x, dist="norm", plot=ax)
    ax.set_title(f"Q-Q plot {var_name} ({stage})")


def check_kstest(x, var_name, stage="Original", limit=0.05):
    x_std = (x - np.mean(x)) / np.std(x)
    ks_stat, p_val = stats.kstest(x_std, "norm")
    colour = GREEN if p_val > limit else RED
    logger.info(f"{colour}{var_name} ({stage}): KS-stat={ks_stat:.6f}, p-value={p_val:.9f}{RESET}")


def fully_check_variable(x, var_name, stage="Original"):
    logger.info(f"\n=== {var_name} ({stage}) ===")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    check_histogram(axes[0], x, var_name, stage)
    check_qqplot(axes[1], x, var_name, stage)
    plt.tight_layout()

    filename = f"{PLOTS_DIR}/{var_name}_{stage}.png"
    plt.savefig(filename, dpi=300)
    plt.close(fig)  

    check_kstest(x, var_name, stage)


def try_transformations(x):
    transformations = {
        'log': np.log1p,
        'sqrt': np.sqrt,
        'cbrt': np.cbrt
    }
    transformed_data = {}
    for name, func in transformations.items():
        transformed_data[name] = func(x)
    return transformed_data


logger.add(LOG_PATH, encoding="utf-8") 

df = pd.read_csv(CSV_PATH)
data = df[COLUMNS].dropna()

for i, col in enumerate(COLUMNS):
    fully_check_variable(data[col], col, stage="Original")

    transformed_dict = try_transformations(data[col])
    for t_name, t_data in transformed_dict.items():
        fully_check_variable(t_data, col, stage=f"{t_name}-transformed")

    if i < len(COLUMNS) - 1:
        input("\nPress Enter to continue to the next variable...")