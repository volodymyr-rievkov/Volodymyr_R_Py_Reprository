import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

RELATIVE_PATH = "PythonApplications/ML/Lab_2"
DATASET_NAME = "Student_Performance.csv"
DATASET_PATH = f"{RELATIVE_PATH}/{DATASET_NAME}"
COLUMN_NAME = "Performance Index"
OUTPUT_DIR_PLOTS = f"{RELATIVE_PATH}/tree_plots"
OUTPUT_DIR_PCA = f"{RELATIVE_PATH}/pca_plots"
DEPTH = [3,5,7]

def read_dataset(dataset_path=DATASET_PATH):
    dataset_name = dataset_path.split("/")[-1].replace(".csv", "")
    print(f"\n==== {dataset_name} ====")
    return pd.read_csv(dataset_path)

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

def build_and_evaluate_trees(X_train, y_train, X_val, y_val, depths=DEPTH):
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

        train_mse = mean_squared_error(y_train, y_train_pred)
        val_mse = mean_squared_error(y_val, y_val_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        val_r2 = r2_score(y_val, y_val_pred)

        scores[depth] = {
            "train_mse": train_mse, "val_mse": val_mse,
            "train_r2": train_r2, "val_r2": val_r2
        }

        print(f"Train MSE: {train_mse:.4f}, Validation MSE: {val_mse:.4f}")
        print(f"Train R2 : {train_r2:.4f}, Validation R2 : {val_r2:.4f}")
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

def pca_denoising(X_train, X_train_noisy, output_dir=OUTPUT_DIR_PCA, variance_threshold=0.95):
    print("\n==== PCA Denoising ====")
    os.makedirs(output_dir, exist_ok=True)
    numeric_cols = X_train.select_dtypes(include='number').columns

    def plot_cumulative_variance(pca_obj, title, filename):
        plt.figure(figsize=(10,6))
        plt.plot(np.cumsum(pca_obj.explained_variance_ratio_), marker='o')
        plt.xlabel('Number of Components')
        plt.ylabel('Cumulative Explained Variance')
        plt.title(title)
        plt.grid(True)
        plt.savefig(filename)
        plt.close()
        print(f"Saved plot: {filename.split('/')[-1]}")

    pca_orig = PCA()
    pca_orig.fit(X_train[numeric_cols])
    plot_cumulative_variance(pca_orig, "Original Data PCA", f"{output_dir}/pca_original_cumulative.png")

    pca_noisy = PCA()
    pca_noisy.fit(X_train_noisy[numeric_cols])
    plot_cumulative_variance(pca_noisy, "Noisy Data PCA", f"{output_dir}/pca_noisy_cumulative.png")

    cum_var = np.cumsum(pca_noisy.explained_variance_ratio_)
    n_components_95 = np.argmax(cum_var >= variance_threshold) + 1
    pca_denoise = PCA(n_components=n_components_95)
    X_train_denoised = pca_denoise.fit_transform(X_train_noisy[numeric_cols])
    X_train_denoised_reconstructed = pca_denoise.inverse_transform(X_train_denoised)

    pca_denoised_plot = PCA()
    pca_denoised_plot.fit(X_train_denoised_reconstructed)
    plot_cumulative_variance(pca_denoised_plot, "Denoised Data PCA", f"{output_dir}/pca_denoised_cumulative.png")

    X_train_denoised_df = pd.DataFrame(X_train_denoised_reconstructed, columns=numeric_cols)

    return X_train_denoised_df

def compare_scores(scores_noisy, scores_denoised, depths=DEPTH):
    print("\n==== Regression Score Comparison ====")
    header = (
        f"{'Depth':^7}|{'Noisy MSE (Train/Val)':^27}|"
        f"{'Noisy R2 (Train/Val)':^23}|{'Denoised MSE (Train/Val)':^30}|"
        f"{'Denoised R2 (Train/Val)':^27}"
    )
    print(header)
    print("-" * len(header))

    for depth in depths:
        n = scores_noisy[depth]
        d = scores_denoised[depth]

        noisy_mse = f"{n['train_mse']:.4f}/{n['val_mse']:.4f}"
        noisy_r2 = f"{n['train_r2']:.4f}/{n['val_r2']:.4f}"
        den_mse = f"{d['train_mse']:.4f}/{d['val_mse']:.4f}"
        den_r2 = f"{d['train_r2']:.4f}/{d['val_r2']:.4f}"

        print(f"{depth:^7}|{noisy_mse:^27}|{noisy_r2:^23}|{den_mse:^30}|{den_r2:^27}")
 
if __name__ == "__main__":
    # Task 1
    data = read_dataset()
    print(data.head(5))
    data = handle_nan_values(data)
    data = encode_categorical(data)
    X_train, X_val, X_test, y_train, y_val, y_test = split_data(data)
    X_train, X_val, X_test = normalize_data(X_train, X_val, X_test)

    # Task 2
    trees, scores = build_and_evaluate_trees(X_train, y_train, X_val, y_val)
    save_tree_plots(trees, X_train)

    # Task 3: 
    X_train_noisy = add_noise_to_data(X_train)
    noised_trees, scores_noisy = build_and_evaluate_trees(X_train_noisy, y_train, X_val, y_val)
    save_tree_plots(noised_trees, X_train_noisy, output_dir=f"{OUTPUT_DIR_PLOTS}_noisy")

    # Task 4: 
    X_train_denoised = pca_denoising(X_train, X_train_noisy)

    # Task 5: 
    trees_denoised, scores_denoised = build_and_evaluate_trees(X_train_denoised, y_train, X_val, y_val)
    save_tree_plots(trees_denoised, X_train_denoised, output_dir=f"{OUTPUT_DIR_PLOTS}_denoised")

    # Task 6: 
    compare_scores(scores_noisy, scores_denoised)
