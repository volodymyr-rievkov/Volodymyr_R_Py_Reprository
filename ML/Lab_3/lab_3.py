import os
import pandas as pd
import numpy as np
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt

RELATIVE_PATH = "PythonApplications/ML/Lab_3"
DATASET_NAME = "penguins"
COLUMN_NAME = "body_mass_g"
OUTPUT_DIR_PLOTS = f"{RELATIVE_PATH}/tree_plots"
OUTPUT_DIR_SVD = f"{RELATIVE_PATH}/svd_plots"
DEPTHS = [3, 4, 5, 6]

def read_dataset():
    print(f"\n==== Loading dataset: {DATASET_NAME} ====")
    data = sns.load_dataset(DATASET_NAME)
    return data

def handle_nan_values(data, threshold=5.0):
    print("\n==== Handling missing values ====")
    for column in data.columns:
        missing_values = data[column].isna().sum()
        total_len = len(data)
        percentage = (missing_values / total_len) * 100

        if missing_values > 0:
            print(f"Missing values in '{column}': {missing_values} ({percentage:.2f}%)")

            if pd.api.types.is_numeric_dtype(data[column]):

                if percentage <= threshold:
                    data = data.dropna(subset=[column])
                    print(f"Dropped {missing_values} rows with missing values in '{column}'.")
                else:
                    mean_value = data[column].mean()
                    data[column] = data[column].fillna(mean_value)
                    print(f"Filled {missing_values} missing values in '{column}' with mean ({mean_value:.2f}).")
            else:
                if percentage <= threshold:
                    data = data.dropna(subset=[column])
                    print(f"Dropped {missing_values} rows with missing values in '{column}'.")
                else:
                    mode_value = data[column].mode()[0]
                    data[column] = data[column].fillna(mode_value)
                    print(f"Filled {missing_values} missing values in '{column}' with mode ('{mode_value}').")
        else:
            print(f"No missing values in '{column}'.")
    return data

def encode_categorical(data):
    for col in data.columns:
        if data[col].dtype == "object": 
            print(f"==== Encoding '{col}' ====")
            unique_vals = data[col].nunique()
            if unique_vals == 2:
                data[col] = data[col].map({data[col].unique()[0]: 0,
                                           data[col].unique()[1]: 1})
            else:
                data = pd.get_dummies(data, columns=[col])
    return data

def split_data(data, column_name=COLUMN_NAME, ratio=(0.7, 0.15, 0.15), random_state=42):
    print(f"\n==== Splitting data in ratio {ratio} ====")
    X = data.drop(columns=[column_name])
    y = data[column_name]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=(1 - ratio[0]), random_state=random_state, shuffle=True
    )

    val_size = ratio[1] / (ratio[1] + ratio[2]) 
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=(1 - val_size), random_state=random_state, shuffle=True
    )

    print(f"Train size: {len(X_train)}, Validation size: {len(X_val)}, Test size: {len(X_test)}")
    return X_train, X_val, X_test, y_train, y_val, y_test

def normalize_data(X_train, X_val, X_test):
    print("\n==== Normalizing numerical features ====")
    
    numeric_cols = X_train.select_dtypes(include='number').columns
    means = X_train[numeric_cols].mean()
    stds = X_train[numeric_cols].std()
    
    print("Feature means (train numeric):")
    print(means)
    print("Feature stds (train numeric):")
    print(stds)

    X_train[numeric_cols] = (X_train[numeric_cols] - means) / stds
    X_val[numeric_cols] = (X_val[numeric_cols] - means) / stds
    X_test[numeric_cols] = (X_test[numeric_cols] - means) / stds

    return X_train, X_val, X_test

def build_and_evaluate_trees(X_train, y_train, X_val, y_val, depths=DEPTHS):
    print("\n==== Building and evaluating regression trees ====")
    trees = {}
    scores = {}
    for depth in depths:
        print(f"\n--- Decision Tree Regressor (max_depth={depth}) ---")
        tree = DecisionTreeRegressor(max_depth=depth, random_state=42)
        tree.fit(X_train, y_train)
        trees[depth] = tree

        y_train_pred = tree.predict(X_train)
        y_val_pred = tree.predict(X_val)

        train_mae = mean_absolute_error(y_train, y_train_pred)
        val_mae = mean_absolute_error(y_val, y_val_pred)

        train_mse = mean_squared_error(y_train, y_train_pred)
        val_mse = mean_squared_error(y_val, y_val_pred)

        train_rmse = np.sqrt(train_mse)
        val_rmse = np.sqrt(val_mse)

        train_r2 = r2_score(y_train, y_train_pred)
        val_r2 = r2_score(y_val, y_val_pred)

        scores[depth] = {
            "train_mae": train_mae, "val_mae": val_mae,
            "train_mse": train_mse, "val_mse": val_mse,
            "train_rmse": train_rmse, "val_rmse": val_rmse,
            "train_r2": train_r2, "val_r2": val_r2
        }

        print(f"MAE  -> Train: {train_mae:.4f}, Val: {val_mae:.4f}")
        print(f"MSE  -> Train: {train_mse:.4f}, Val: {val_mse:.4f}")
        print(f"RMSE -> Train: {train_rmse:.4f}, Val: {val_rmse:.4f}")
        print(f"R²   -> Train: {train_r2:.4f}, Val: {val_r2:.4f}")
    return trees, scores

def save_tree_plots(trees, X_train, output_dir=OUTPUT_DIR_PLOTS):
    print("\n==== Saving regression tree plots ====")
    os.makedirs(output_dir, exist_ok=True)
    for depth, tree in trees.items():
        plt.figure(figsize=(20, 10))
        plot_tree(tree, feature_names=X_train.columns, filled=True, fontsize=10)
        filename = f"{output_dir}/regression_tree_depth_{depth}.png"
        plt.savefig(filename)
        print(f"Saved tree plot as {filename.split('/')[-1]}")
        plt.close()

def add_noise_to_data(X_train, low=-0.1, high=0.1, random_state=42):
    print("\n==== Adding noise to training data ====")
    np.random.seed(random_state)
    X_train_noisy = X_train.copy()
    numeric_cols = X_train_noisy.select_dtypes(include='number').columns

    for col in numeric_cols:
        noise = np.random.uniform(low, high, size=len(X_train_noisy))
        X_train_noisy[col] += noise

    return X_train_noisy

def svd_denoising(X_train, X_train_noisy, output_dir=OUTPUT_DIR_SVD, energy_threshold=0.98):
    print("\n==== SVD Performance ====")
    os.makedirs(output_dir, exist_ok=True)
    numeric_cols = X_train.select_dtypes(include='number').columns

    print("\n==== Original data ====")
    U_orig, S_orig, VT_orig = np.linalg.svd(X_train[numeric_cols].values, full_matrices=False)
    X_orig_df = pd.DataFrame(U_orig @ np.diag(S_orig) @ VT_orig, columns=numeric_cols)

    print("==== Noisy data ====")
    U_noisy, S_noisy, VT_noisy = np.linalg.svd(X_train_noisy[numeric_cols].values, full_matrices=False)
    X_noisy_df = pd.DataFrame(U_noisy @ np.diag(S_noisy) @ VT_noisy, columns=numeric_cols)

    print("==== Denoised data ====")
    cum_energy = np.cumsum(S_noisy**2) / np.sum(S_noisy**2)
    k = np.argmax(cum_energy >= energy_threshold) + 1

    X_denoised = U_noisy[:, :k] @ np.diag(S_noisy[:k]) @ VT_noisy[:k, :]
    X_denoised_df = pd.DataFrame(X_denoised, columns=numeric_cols)

    print("\n==== Saving Heatmaps ====")
    for data, name in zip([X_orig_df, X_noisy_df, X_denoised_df],
                          ["Original", "Noisy", "Denoised"]):
        plt.figure(figsize=(12,6))
        plt.title(f"{name} data heatmap")
        plt.imshow(data, aspect='auto', cmap='viridis')
        plt.colorbar()
        filename = f"{output_dir}/{name.lower()}_heatmap.png"
        plt.savefig(filename)
        print(f"Saved heatmap as {filename.split('/')[-1]}")
        plt.close()

    return X_denoised_df

def compare_scores(scores_noisy, scores_denoised, depths=DEPTHS):
    print("\n==== Regression Score Comparison ====")
    header = (
        f"{'Depth':^7}|{'Noisy MAE (Train/Val)':^27}|"
        f"{'Noisy R2 (Train/Val)':^27}|{'Denoised MAE (Train/Val)':^30}|"
        f"{'Denoised R2 (Train/Val)':^27}"
    )
    print(header)
    print("-" * len(header))

    for depth in depths:
        n = scores_noisy[depth]
        d = scores_denoised[depth]

        noisy_mae = f"{n['train_mae']:.2f}/{n['val_mae']:.2f}"
        noisy_r2 = f"{n['train_r2']:.2f}/{n['val_r2']:.2f}"
        den_mae = f"{d['train_mae']:.2f}/{d['val_mae']:.2f}"
        den_r2 = f"{d['train_r2']:.2f}/{d['val_r2']:.2f}"

        print(f"{depth:^7}|{noisy_mae:^27}|{noisy_r2:^27}|{den_mae:^30}|{den_r2:^27}")

    print("-" * len(header))

if __name__ == "__main__":
    # Task 1
    data = read_dataset()
    data = handle_nan_values(data)
    data = encode_categorical(data)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(data)
    X_train, X_val, X_test = normalize_data(X_train, X_val, X_test)

    # Task 2
    trees, scores = build_and_evaluate_trees(X_train, y_train, X_val, y_val)
    save_tree_plots(trees, X_train)

    # Task 3
    X_train_noisy = add_noise_to_data(X_train)
    trees_noisy, scores_noisy = build_and_evaluate_trees(X_train_noisy, y_train, X_val, y_val)
    save_tree_plots(trees_noisy, X_train_noisy, output_dir=f"{OUTPUT_DIR_PLOTS}_noisy")

    # Task 4
    X_train_denoised = svd_denoising(X_train, X_train_noisy)
    trees_denoised, scores_denoised = build_and_evaluate_trees(X_train_denoised, y_train, X_val[X_train_denoised.columns], y_val)
    save_tree_plots(trees_denoised, X_train_denoised, output_dir=f"{OUTPUT_DIR_PLOTS}_denoised")

    # Task 5
    compare_scores(scores_noisy, scores_denoised)
