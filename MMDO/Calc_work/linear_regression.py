import csv
import numpy as np
from time import time
from tabulate import tabulate
import pandas as pd

def read_data(file_path):
    X = []
    y = []
    quality_mapping = {"low": 0, "medium": 1, "high": 2}
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            features = [float(x) for x in row[:-1]]
            X.append(features)
            quality = row[-1].strip().lower()
            y.append(quality_mapping.get(quality, 0))
    return np.array(X), np.array(y), headers[:-1]

def normalize_data(X):
    X_mean = np.mean(X, axis=0)
    X_std = np.std(X, axis=0)
    X_std[X_std == 0] = 1
    X_normalized = (X - X_mean) / X_std
    return X_normalized

def train_test_split_manual(X, y, test_size=0.2, random_state=42):
    np.random.seed(random_state)
    indices = np.random.permutation(X.shape[0])
    test_size = int(test_size * X.shape[0])
    test_indices = indices[:test_size]
    train_indices = indices[test_size:]
    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]
    return X_train, X_test, y_train, y_test

def linear_regression(X, y):
    X_with_bias = np.hstack([np.ones((X.shape[0], 1)), X])
    XtX = np.dot(X_with_bias.T, X_with_bias)
    XtX_inv = np.linalg.inv(XtX)
    Xty = np.dot(X_with_bias.T, y)
    beta = np.dot(XtX_inv, Xty)
    return beta, 0

def lasso_regression(X, y, alpha=0.1, max_iter=1000, tol=1e-4):
    X_with_bias = np.hstack([np.ones((X.shape[0], 1)), X])
    n_features = X_with_bias.shape[1]
    w = np.zeros(n_features)
    learning_rate = 0.01
    iterations = 0
    for _ in range(max_iter):
        y_pred = np.dot(X_with_bias, w)
        residuals = y_pred - y
        gradient = np.dot(X_with_bias.T, residuals) / X.shape[0]
        gradient[1:] += alpha * np.sign(w[1:])
        w_new = w - learning_rate * gradient
        if np.max(np.abs(w_new - w)) < tol:
            break
        w = w_new
        iterations += 1
    return w, iterations

def ridge_regression(X, y, alpha=0.1, max_iter=1000, tol=1e-4):
    X_with_bias = np.hstack([np.ones((X.shape[0], 1)), X])
    n_features = X_with_bias.shape[1]
    w = np.zeros(n_features)
    learning_rate = 0.01
    iterations = 0
    for _ in range(max_iter):
        y_pred = np.dot(X_with_bias, w)
        residuals = y_pred - y
        gradient = np.dot(X_with_bias.T, residuals) / X.shape[0]
        gradient[1:] += 2 * alpha * w[1:]
        w_new = w - learning_rate * gradient
        if np.max(np.abs(w_new - w)) < tol:
            break
        w = w_new
        iterations += 1
    return w, iterations

def predict(X, w):
    X_with_bias = np.hstack([np.ones((X.shape[0], 1)), X])
    return np.dot(X_with_bias, w)

def mean_squared_error(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

def root_mean_squared_error(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

def train_model(name, model_func, X_train, y_train, alpha=None):
    start_time = time()
    if alpha is None:
        w, iterations = model_func(X_train, y_train)
    else:
        w, iterations = model_func(X_train, y_train, alpha=alpha)
    training_time = time() - start_time
    return w, iterations, training_time

def evaluate_model(X_test, y_test, w):
    y_pred = predict(X_test, w)
    mse = mean_squared_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    return mse, rmse

def select_best_alpha(model_func, X_train, y_train, X_test, y_test, alphas):
    best_mse = float('inf')
    best_alpha = None
    best_w = None
    best_iterations = 0
    best_training_time = 0
    for alpha in alphas:
        start_time = time()
        w, iterations = model_func(X_train, y_train, alpha=alpha)
        training_time = time() - start_time
        y_pred = predict(X_test, w)
        mse = mean_squared_error(y_test, y_pred)
        if mse < best_mse:
            best_mse = mse
            best_alpha = alpha
            best_w = w
            best_iterations = iterations
            best_training_time = training_time
    return best_w, best_iterations, best_training_time, best_mse, best_alpha

FILENAME = "D:\\Programming\\PythonApplications\\MMDO\\Calc_work\\wine_quality_classification.csv"
X, y, feature_names = read_data(FILENAME)
X_train, X_test, y_train, y_test = train_test_split_manual(X, y)
X_train_normalized = normalize_data(X_train)
X_test_normalized = normalize_data(X_test)

results = []
models = [
    ('OLS', linear_regression, None),
    ('Lasso (alpha=0.1)', lasso_regression, 0.1),
    ('Ridge (alpha=0.1)', ridge_regression, 0.1)
]

for name, model_func, alpha in models:
    w, iterations, training_time = train_model(name, model_func, X_train_normalized, y_train, alpha)
    mse, rmse = evaluate_model(X_test_normalized, y_test, w)
    results.append({
        'Model': name,
        'Training Time (s)': training_time,
        'Iterations': iterations,
        'MSE': mse,
        'RMSE': rmse
    })

alphas = [0.01, 0.1, 1, 10]
for name, model_func in [('Lasso', lasso_regression), ('Ridge', ridge_regression)]:
    best_w, best_iterations, best_training_time, best_mse, best_alpha = select_best_alpha(model_func, X_train_normalized, y_train, X_test_normalized, y_test, alphas)
    results.append({
        'Model': f'{name} (Best alpha={best_alpha})',
        'Training Time (s)': best_training_time,
        'Iterations': best_iterations,
        'MSE': best_mse,
        'RMSE': np.sqrt(best_mse)
    })

print("\nТаблиця порівняння моделей:")
print(tabulate(results, headers='keys', tablefmt='grid', floatfmt='.6f'))
results_df = pd.DataFrame(results)
results_df.to_csv('model_comparison_manual.csv', index=False)