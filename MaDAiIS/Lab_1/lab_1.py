import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np
import os

RELATIVE_PATH = "PythonApplications/MaDAiIS/Lab_1"
CSV_PATH = f"{RELATIVE_PATH}/train.csv"
COLUMNS = ['Age', 'Fare']

dataset_name = os.path.splitext(os.path.basename(CSV_PATH))[0]
output_dir = f"{RELATIVE_PATH}/{dataset_name}_plots"
os.makedirs(output_dir, exist_ok=True)


def check_histogram(ax, x, var_name, stage="Original"):
    sns.histplot(x, kde=True, bins=30, ax=ax)
    ax.set_title(f"Histogram {var_name} ({stage})")
    ax.set_xlabel(var_name)
    ax.set_ylabel("Frequency")


def check_qqplot(ax, x, var_name, stage="Original"):
    stats.probplot(x, dist="norm", plot=ax)
    ax.set_title(f"Q-Q plot {var_name} ({stage})")


def check_kstest(x, var_name, stage="Original"):
    x_std = (x - np.mean(x)) / np.std(x)
    ks_stat, p_val = stats.kstest(x_std, "norm")
    print(f"{var_name} ({stage}): KS-stat={ks_stat:.3f}, p-value={p_val:.3f}")


def fully_check_variable(x, var_name, stage="Original"):
    print(f"\n=== {var_name} ({stage}) ===")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    check_histogram(axes[0], x, var_name, stage)
    check_qqplot(axes[1], x, var_name, stage)
    plt.tight_layout()

    filename = f"{output_dir}/{var_name}_{stage}.png"
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


df = pd.read_csv(CSV_PATH)
data = df[COLUMNS].dropna()

for col in COLUMNS:
    fully_check_variable(data[col], col, stage="Original")

    transformed_dict = try_transformations(data[col])
    for t_name, t_data in transformed_dict.items():
        fully_check_variable(t_data, col, stage=f"{t_name}-transformed")

    input("\nPress Enter to continue to the next variable...")
