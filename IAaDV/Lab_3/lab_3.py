import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from currency_converter import CurrencyConverter
import datetime
import warnings
warnings.filterwarnings("ignore")


VARIANT = 8

PATH = "D:/Programming/PythonApplications/IAaDV/Lab_3"
DATASET_NAME = "global_food_prices.csv"
DATASET_PATH = f"{PATH}/{DATASET_NAME}"

OUTPUT_DIR = os.path.join(PATH, "visualizations")
os.makedirs(OUTPUT_DIR, exist_ok=True)

YEAR_COLUMN = "mp_year"
MONTH_COLUMN = "mp_month"
PRICE_COLUMN = "mp_price"
PRODUCT_COLUMN = "cm_name"
COUNTRY_COLUMN = "adm0_name"
CUR_COLUMN = "cur_name"
MARKET_COLUMN = "mkt_name"
MARKET_PRICE_COLUMN = "market_price"
USD_PRICE_COLUMN = "mp_price_usd"

CURRENCY = "USD"

YELLOW = "\033[93m"
RESET = "\033[0m"

START = 1994
END = 2007


def read_dataset(path: str) -> pd.DataFrame:
    print(f"\n==== Loading dataset: {DATASET_NAME} ====")
    data = pd.read_csv(path, low_memory=False)
    print(f"Dataset loaded with {data.shape[0]} rows and {data.shape[1]} columns.")
    return data

def filter_data(data: pd.DataFrame) -> pd.DataFrame:
    print(f"\n==== Filtering data where {YEAR_COLUMN} is between {START} and {END} ====")
    try:
        filter_data = data[(data[YEAR_COLUMN] >= START) & (data[YEAR_COLUMN] <= END)]
        print(f"Filtered dataset has {filter_data.shape[0]} rows and {filter_data.shape[1]} columns.")
        return filter_data
    except KeyError:
        print(f"Column '{YEAR_COLUMN}' not found in dataset.")
        return data

def compute_statistics(data: pd.DataFrame, column=PRICE_COLUMN) -> pd.DataFrame:
    print(f"\n==== Computing statistics ====")
    stats = data.groupby("cm_name")[column].agg(
        min_price="min",
        max_price="max",
        mean_price="mean",
        q25=lambda x: x.quantile(0.25),
        median=lambda x: x.median(),
        q75=lambda x: x.quantile(0.75),
        variance="var"
    )
    print("\n=== Statistics by cm_name ===")
    print(stats.head(VARIANT))
    return stats

def create_crosstab(data: pd.DataFrame, column1=PRODUCT_COLUMN, column2="pt_name") -> pd.DataFrame:
    ctab = pd.crosstab(data[column1], data[column2])
    print("\n=== Crosstab cm_name vs pt_name ===")
    print(ctab.head(VARIANT))
    return ctab

def select_product_and_country(data: pd.DataFrame, variant: int) -> tuple[str, str]:
    print("\n==== Selecting product and country ====")

    products = sorted(data[PRODUCT_COLUMN].unique())
    countries = sorted(data[COUNTRY_COLUMN].unique())

    product = products[(variant) % len(products)]
    country = countries[(variant) % len(countries)]

    if not ((data[PRODUCT_COLUMN] == product) & (data[COUNTRY_COLUMN] == country)).any():
        country = (
            data.loc[data[PRODUCT_COLUMN] == product, COUNTRY_COLUMN]
            .dropna()
            .unique()[0]
        )

    print(f"Selected → Product: {product}, Country: {country}")
    return product, country

def plot_boxplot(data: pd.DataFrame, product: str) -> None:
    sns.set(style="whitegrid")
    plt.figure(figsize=(10,6))
    sns.boxplot(x=PRODUCT_COLUMN, y=PRICE_COLUMN, data=data[data[PRODUCT_COLUMN] == product])
    plt.title(f"Boxplot of mp_price for {product}")
    filepath = os.path.join(OUTPUT_DIR, "task_1")
    os.makedirs(filepath, exist_ok=True)
    plot_path = os.path.join(filepath, f"boxplot_{product}.png")
    plt.savefig(plot_path, dpi=300)
    print(f"Saved: {plot_path}")
    plt.close()


def visualize_trends(data: pd.DataFrame, product: str, country: str) -> None:
    print("\n==== Visualizing price trends ====")
    print(f"Selected country: {country}")

    df_filtered = data[(data[PRODUCT_COLUMN] == product) & (data[COUNTRY_COLUMN] == country)].copy()

    if df_filtered.empty:
        print(f"No data for {product} in {country}.")
        return

    df_filtered["log_price"] = np.log(df_filtered[PRICE_COLUMN].replace(0, np.nan))

    filepath = os.path.join(OUTPUT_DIR, "task_2")
    os.makedirs(filepath, exist_ok=True)

    plt.figure(figsize=(10, 5))
    sns.lineplot(x=YEAR_COLUMN, y=PRICE_COLUMN, data=df_filtered, marker="o")
    plt.title(f"Price Trend for {product} in {country}")
    plt.tight_layout()
    lineplot_path = os.path.join(filepath, f"lineplot_{product}_{country}.png")
    plt.savefig(lineplot_path, dpi=300)
    plt.close()
    print(f"Saved: {lineplot_path}")

    plt.figure(figsize=(10, 5))
    sns.scatterplot(x=YEAR_COLUMN, y="log_price", data=df_filtered)
    plt.title(f"log(mp_price) vs Year for {product} in {country}")
    plt.tight_layout()
    scatter_plot = os.path.join(filepath, f"scatter_{product}_{country}.png")
    plt.savefig(scatter_plot, dpi=300)
    plt.close()
    print(f"Saved: {scatter_plot}")

    bins = 30
    plt.figure(figsize=(8, 4))
    plt.hist(df_filtered[PRICE_COLUMN].dropna(), bins=bins, edgecolor="black")
    plt.title(f"Histogram of {product} prices ({bins} bins)")
    plt.xlabel("Price")
    plt.ylabel("Frequency")
    plt.tight_layout()
    hist_path = os.path.join(filepath, f"hist_{bins}bins_{product}_{country}.png")
    plt.savefig(hist_path, dpi=300)
    plt.close()
    print(f"Saved: {hist_path}")

    print("\nAll visualizations saved successfully.")


def handle_missing_values(data: pd.DataFrame) -> pd.DataFrame:
    print("\n==== Handling missing values ====")
    data = data.copy()  

    for col in data.columns:
        missing = data[col].isna().sum()
        if missing > 0:
            if data[col].dtype == "object":
                mode_val = data[col].mode(dropna=True)[0] if not data[col].mode(dropna=True).empty else "Unknown"
                data[col] = data[col].fillna(mode_val)
                print(f"Filled {missing} missing values in '{col}' with mode '{mode_val}'.")
            else:
                mean_val = data[col].mean(skipna=True)
                if pd.isna(mean_val):
                    mean_val = 0
                data[col] = data[col].fillna(mean_val)
                print(f"Filled {missing} missing values in '{col}' with mean {mean_val:.2f}.")
    return data

def encode_variant_column(data: pd.DataFrame, variant: int) -> tuple[pd.DataFrame, str]:
    print("\n==== Encoding categorical column ====")

    cat_cols = data.select_dtypes(include="object").columns.tolist()
    if not cat_cols:
        print("No categorical columns found — skipping encoding.")
        return data, None

    idx = (variant) % len(cat_cols)
    col_to_encode = cat_cols[idx]
    print(f"Categorical columns: {cat_cols}")
    print(f"Selected column for encoding (index {idx}): '{col_to_encode}'")

    encoded_col = f"{col_to_encode}_encoded"
    data[encoded_col] = data[col_to_encode].astype("category").cat.codes + 1

    print(f"Added encoded column: {encoded_col} (codes 1..n)")
    return data, encoded_col

def plot_encoded_scatter(data: pd.DataFrame, encoded_col: str, out_dir: str = PATH) -> None:
    if encoded_col is None or YEAR_COLUMN not in data.columns:
        print(f"Cannot plot scatter — missing encoded column or {YEAR_COLUMN}.")
        return

    filepath = os.path.join(OUTPUT_DIR, "task_3")
    os.makedirs(filepath, exist_ok=True)
    scatter_path = os.path.join(filepath, f"scatter_{encoded_col}.png")

    plt.figure(figsize=(8, 5))
    sns.scatterplot(x=YEAR_COLUMN, y=encoded_col, data=data, alpha=0.6, s=30)
    plt.title(f"{YEAR_COLUMN} vs {encoded_col}")
    plt.tight_layout()
    plt.savefig(scatter_path, dpi=300)
    plt.close()
    print(f"Saved: {scatter_path}")


def correlation_analysis(data: pd.DataFrame, variant: int) -> None:
    print("\n==== Correlation Analysis ====")

    if CUR_COLUMN not in data.columns:
        print(f"Column '{CUR_COLUMN}' not found — skipping correlation analysis.")
        return

    currencies = sorted(data[CUR_COLUMN].dropna().unique())
    if not currencies:
        print("No currencies available in dataset.")
        return

    cur_selected = currencies[(variant) % len(currencies)]
    print(f"Selected currency: {cur_selected}")

    df_cur = data[data[CUR_COLUMN] == cur_selected].copy()
    if df_cur.empty:
        print(f"No data found for currency: {cur_selected}")
        return

    numeric_cols = df_cur.select_dtypes(include=[np.number]).columns.tolist()
    if PRICE_COLUMN not in numeric_cols:
        print(f"Column '{PRICE_COLUMN}' not numeric or missing — cannot compute correlation.")
        return

    corr_matrix = df_cur[numeric_cols].corr(method="pearson")
    print("\n=== Correlation matrix (top 10) ===")
    print(corr_matrix)

    filepath = os.path.join(OUTPUT_DIR, "task_4")
    os.makedirs(filepath, exist_ok=True)

    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", square=True)
    plt.title(f"Correlation Matrix (Pearson) — {cur_selected}")
    plt.tight_layout()
    heatmap_path = os.path.join(filepath, f"heatmap_{cur_selected}.png")
    plt.savefig(heatmap_path, dpi=300)
    plt.close()
    print(f"Saved: {heatmap_path}")

    correlations = corr_matrix[PRICE_COLUMN].drop(PRICE_COLUMN).abs().sort_values(ascending=False)
    top_features = correlations.head(3).index.tolist()

    print(f"\nTop 3 correlated features with {PRICE_COLUMN}: {top_features}")

    for feat in top_features:
        plt.figure(figsize=(7, 5))
        sns.scatterplot(x=feat, y=PRICE_COLUMN, data=df_cur, alpha=0.6)
        plt.title(f"{feat} vs {PRICE_COLUMN} ({cur_selected})")
        plt.tight_layout()
        scatter_path = os.path.join(filepath, f"scatter_{feat}_vs_{PRICE_COLUMN}_{cur_selected}.png")
        plt.savefig(scatter_path, dpi=300)
        plt.close()
        print(f"Saved: {scatter_path}")

    print("\nCorrelation analysis completed successfully.")


def linear_regression_forecast(data: pd.DataFrame, product: str, years_ahead: int = 5) -> tuple[LinearRegression, pd.DataFrame, pd.DataFrame]:
    print(f"\n==== Linear Regression Forecast for {product} ====")

    df_product = data[data[PRODUCT_COLUMN] == product].copy()
    df_product = handle_missing_values(df_product[[YEAR_COLUMN, MONTH_COLUMN, PRICE_COLUMN]])

    if df_product.empty:
        print(f"No data available for {product}")
        return

    X = df_product[[YEAR_COLUMN, MONTH_COLUMN]]  
    y = df_product[PRICE_COLUMN]

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    mae = mean_absolute_error(y, y_pred)
    rmse = mean_squared_error(y, y_pred) ** 0.5 
    r2 = r2_score(y, y_pred)
    print(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.3f}")

    last_year = df_product[YEAR_COLUMN].max()
    future_years = np.arange(last_year + 1, last_year + 1 + years_ahead)
    
    future_months = np.full_like(future_years, 6)  
    future_X = pd.DataFrame({YEAR_COLUMN: future_years, MONTH_COLUMN: future_months})
    future_pred = model.predict(future_X)

    filepath = os.path.join(OUTPUT_DIR, "task_5")
    os.makedirs(filepath, exist_ok=True)

    plt.figure(figsize=(10,6))
    plt.scatter(X[YEAR_COLUMN], y, label="Actual", color="blue")
    plt.plot(X[YEAR_COLUMN], y_pred, label="Predicted", color="red")
    plt.plot(future_X[YEAR_COLUMN], future_pred, label="Forecast", color="green", linestyle="--")
    plt.xlabel("Year")
    plt.ylabel("Price")
    plt.title(f"Linear Regression Forecast for {product}")
    plt.legend()
    plt.tight_layout()
    forecast_path = os.path.join(filepath, f"forecast_{product}.png")
    plt.savefig(forecast_path, dpi=300)
    plt.close()
    print(f"Saved: {forecast_path}")

    forecast_df = pd.DataFrame({
        YEAR_COLUMN: pd.concat([X[YEAR_COLUMN], future_X[YEAR_COLUMN]]).reset_index(drop=True),
        MONTH_COLUMN: pd.concat([X[MONTH_COLUMN], future_X[MONTH_COLUMN]]).reset_index(drop=True)
    })

    return model, forecast_df, y


def sensitivity_analysis(model, X, y, sub_dir, feature_names=None, perc_changes=[-20, -10, -5, 5, 10, 20], plot_type="line") -> None:
    print("\n==== Sensitivity Analysis ====")
    if feature_names is None:
        feature_names = X.columns.tolist()
    
    file_path = os.path.join(OUTPUT_DIR, sub_dir)
    os.makedirs(file_path, exist_ok=True)
    
    base_pred = model.predict(X)
    
    for feature in feature_names:
        sensitivity_results = []
        
        for p in perc_changes:
            X_modified = X.copy()
            X_modified[feature] = X_modified[feature] * (1 + p/100)
            pred_modified = model.predict(X_modified)
            change_percent = ((pred_modified - base_pred) / base_pred) * 100
            mean_change = np.mean(change_percent)
            sensitivity_results.append((p, mean_change))
        
        x_vals, y_vals = zip(*sensitivity_results)
        plt.figure(figsize=(8,5))
        
        if plot_type == "bar":
            plt.bar([str(v)+"%" for v in x_vals], y_vals, color="skyblue", edgecolor="black")
            plt.xlabel(f"% Change in {feature}")
            plt.ylabel("% Change in Predicted Price")
        elif plot_type == "line":
            plt.plot(x_vals, y_vals, marker='o')
            plt.xlabel(f"% Change in {feature}")
            plt.ylabel("% Change in Predicted Price")
        else:
            print("Invalid plot type. Please choose 'bar' or 'line'.")
            return
        plt.title(f"Sensitivity Analysis ({feature})")
        plt.grid(True)
        plt.tight_layout()
        sens_path = os.path.join(file_path, f"sensitivity_{feature}.png")
        plt.savefig(sens_path, dpi=300)
        plt.close()
        print(f"Saved: {sens_path}")
    
    if len(feature_names) > 1:
        sensitivity_results = []
        for p in perc_changes:
            X_modified = X.copy()
            for feature in feature_names:
                X_modified[feature] = X_modified[feature] * (1 + p/100)
            pred_modified = model.predict(X_modified)
            change_percent = ((pred_modified - base_pred) / base_pred) * 100
            mean_change = np.mean(change_percent)
            sensitivity_results.append((p, mean_change))
        
        x_vals, y_vals = zip(*sensitivity_results)
        plt.figure(figsize=(8,5))
        if plot_type == "bar":
            plt.bar([str(v)+"%" for v in x_vals], y_vals, color="salmon", edgecolor="black")
        else:
            plt.plot(x_vals, y_vals, marker='o', color='red')
        plt.xlabel(f"% Change in All Features")
        plt.ylabel("% Change in Predicted Price")
        plt.title("Sensitivity Analysis (Combined Features)")
        plt.grid(True)
        plt.tight_layout()
        sens_path = os.path.join(file_path, "sensitivity_combined.png")
        plt.savefig(sens_path, dpi=300)
        plt.close()
        print(f"Saved: {sens_path}")


def mlp_forecast(data: pd.DataFrame, product: str, years_ahead: int = 5) -> tuple[MLPRegressor, pd.DataFrame, pd.Series]:
    print(f"\n==== MLP Neural Network Forecast for {product} ====")

    df_product = data[data[PRODUCT_COLUMN] == product].copy()
    df_product = df_product[[YEAR_COLUMN, MONTH_COLUMN, PRICE_COLUMN]].dropna()

    if df_product.empty:
        print(f"No data available for {product}")
        return None, None, None

    X = df_product[[YEAR_COLUMN, MONTH_COLUMN]]
    y = df_product[PRICE_COLUMN]

    scaler_X = StandardScaler()
    scaler_y = StandardScaler()

    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.values.reshape(-1, 1)).ravel()

    model = MLPRegressor(hidden_layer_sizes=(50, 50), max_iter=5000, random_state=42)
    model.fit(X_scaled, y_scaled)

    y_pred_scaled = model.predict(X_scaled)
    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()

    mae = mean_absolute_error(y, y_pred)
    rmse = mean_squared_error(y, y_pred) ** 0.5
    r2 = r2_score(y, y_pred)
    print(f"MLP → MAE: {mae:.2f}, RMSE: {rmse:.2f}, R2: {r2:.3f}")

    last_year = df_product[YEAR_COLUMN].max()
    future_years = np.arange(last_year + 1, last_year + 1 + years_ahead)
    future_months = np.full_like(future_years, 6)
    future_X = pd.DataFrame({YEAR_COLUMN: future_years, MONTH_COLUMN: future_months})

    future_X_scaled = scaler_X.transform(future_X)
    future_pred_scaled = model.predict(future_X_scaled)
    future_pred = scaler_y.inverse_transform(future_pred_scaled.reshape(-1, 1)).ravel()

    filepath = os.path.join(OUTPUT_DIR, "task_6")
    os.makedirs(filepath, exist_ok=True)

    plt.figure(figsize=(10, 6))
    plt.scatter(X[YEAR_COLUMN], y, label="Actual", color="blue")
    plt.plot(X[YEAR_COLUMN], y_pred, label="MLP Predicted", color="red")
    plt.plot(future_years, future_pred, label="MLP Forecast", color="green", linestyle="--")
    plt.xlabel("Year")
    plt.ylabel("Price")
    plt.title(f"MLP Forecast for {product}")
    plt.legend()
    plt.tight_layout()

    forecast_path = os.path.join(filepath, f"mlp_forecast_{product}.png")
    plt.savefig(forecast_path, dpi=300)
    plt.close()
    print(f"Saved: {forecast_path}")

    return model, X, y


def analyze_market_relationships(data: pd.DataFrame) -> tuple[LinearRegression, pd.DataFrame, pd.Series] | None:
    print("\n==== Market Relationship Analysis (fast) ====")

    grouped = (
        data.groupby([MARKET_COLUMN, PRODUCT_COLUMN])[PRICE_COLUMN]
        .mean()
        .reset_index()
    )

    if grouped.empty:
        print("No valid data.")
        return None

    markets = grouped[MARKET_COLUMN].unique()
    if len(markets) < 2:
        print("Not enough markets.")
        return None

    market_products = {
        m: set(grouped.loc[grouped[MARKET_COLUMN] == m, PRODUCT_COLUMN])
        for m in markets
    }

    best_pair = None
    max_shared = 0

    for i in range(len(markets)):
        for j in range(i + 1, len(markets)):
            mkt1, mkt2 = markets[i], markets[j]
            shared = market_products[mkt1] & market_products[mkt2]
            shared_count = len(shared)
            if shared_count > max_shared:
                max_shared = shared_count
                best_pair = (mkt1, mkt2)

    if not best_pair or max_shared < 3:
        print("No pair with enough shared products.")
        return None

    mkt1, mkt2 = best_pair
    print(f"\nSelected markets: {mkt1} ↔ {mkt2} ({max_shared} shared commodities)")

    df1 = grouped[grouped[MARKET_COLUMN] == mkt1][[PRODUCT_COLUMN, PRICE_COLUMN]].rename(columns={PRICE_COLUMN: f"price_{mkt1}"})
    df2 = grouped[grouped[MARKET_COLUMN] == mkt2][[PRODUCT_COLUMN, PRICE_COLUMN]].rename(columns={PRICE_COLUMN: f"price_{mkt2}"})
    merged = pd.merge(df1, df2, on=PRODUCT_COLUMN, how="inner")

    X = merged[[f"price_{mkt1}"]].rename(columns={f"price_{mkt1}": "market_price"})
    y = merged[f"price_{mkt2}"]

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    mae = mean_absolute_error(y, y_pred)
    rmse = mean_squared_error(y, y_pred) ** 0.5
    r2 = r2_score(y, y_pred)

    print(f"\nRegression results {mkt2} ~ {mkt1}:")
    print(f"MAE = {mae:.3f}, RMSE = {rmse:.3f}, R² = {r2:.3f}")

    filepath = os.path.join(OUTPUT_DIR, "task_7")
    os.makedirs(filepath, exist_ok=True)

    plt.figure(figsize=(8, 6))
    sns.scatterplot(x="market_price", y=y.name, data=pd.concat([X, y], axis=1), label="Actual")
    plt.plot(X, y_pred, color="red", label="Regression line")
    plt.title(f"Market Relationship: {mkt2} vs {mkt1}")
    plt.xlabel(f"Average Price on {mkt1}")
    plt.ylabel(f"Average Price on {mkt2}")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(filepath, f"regression_{mkt1}_{mkt2}.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Saved: {plot_path}")

    print("\n==== Regression completed successfully ====")
    return model, X, y


def analyze_currency_influence(data: pd.DataFrame, variant: int):
    print("\n==== Analyzing Currency Influence ====")

    if CUR_COLUMN not in data.columns:
        print(f"Column '{CUR_COLUMN}' not found — cannot perform currency analysis.")
        return

    dataset_currencies = sorted(data[CUR_COLUMN].dropna().unique())

    c = CurrencyConverter(fallback_on_missing_rate=True, fallback_on_wrong_date=True)
    supported_currencies = set(c.currencies)

    available_currencies = [cur for cur in dataset_currencies if cur in supported_currencies]

    if not available_currencies:
        print("No currencies from dataset are supported by the CurrencyConverter library.")
        print(f"Dataset currencies: {dataset_currencies}")
        print(f"Supported currencies sample: {sorted(list(supported_currencies))[:15]}")
        return
    
    cur_selected = available_currencies[variant % len(available_currencies)]
    print(f"Selected currency for analysis: {cur_selected}")

    df_cur = data[data[CUR_COLUMN] == cur_selected].copy()
    if df_cur.empty:
        print(f"No data found for currency {cur_selected}.")
        return

    rates = []
    for _, row in df_cur.iterrows():
        try:
            year = int(row[YEAR_COLUMN])
            month = int(row[MONTH_COLUMN]) if MONTH_COLUMN in df_cur.columns else 6
            date = datetime.date(year, month, 15)
            rate = c.convert(1, cur_selected, CURRENCY, date=date)
        except Exception:
            rate = np.nan
        rates.append(rate)

    rate_column = f"rate_to_{CURRENCY}"
    df_cur[rate_column] = rates
    df_cur = df_cur.dropna(subset=[rate_column])

    if df_cur.empty:
        print(f"No valid exchange rate data available for {cur_selected}.")
        return

    df_cur[USD_PRICE_COLUMN] = df_cur[PRICE_COLUMN] * df_cur[rate_column]

    print(f"\nConverted prices from {cur_selected} → {CURRENCY} using real ECB rates.")
    print(df_cur[[PRICE_COLUMN, USD_PRICE_COLUMN, rate_column]].head(5))

    df_grouped = (
    df_cur.groupby(YEAR_COLUMN, as_index=False)
    .agg({PRICE_COLUMN: "mean", USD_PRICE_COLUMN: "mean"})
    )

    X = df_grouped[[YEAR_COLUMN]].values
    y_orig = df_grouped[PRICE_COLUMN].values
    y_usd = df_grouped[USD_PRICE_COLUMN].values
        
    model_usd = LinearRegression().fit(X, y_usd)
    y_pred_usd = model_usd.predict(X)

    mae = mean_absolute_error(y_usd, y_pred_usd)
    rmse = mean_squared_error(y_usd, y_pred_usd) ** 0.5
    r2 = r2_score(y_usd, y_pred_usd)

    print(f"\nRegression results ({CURRENCY} prices): MAE={mae:.2f}, RMSE={rmse:.2f}, R²={r2:.3f}")

    filepath = os.path.join(OUTPUT_DIR, "task_8")
    os.makedirs(filepath, exist_ok=True)

    plt.figure(figsize=(10,6))
    plt.plot(df_grouped[YEAR_COLUMN], y_orig, 'o-', label=f"Original ({cur_selected})", alpha=0.7)
    plt.plot(df_grouped[YEAR_COLUMN], y_usd, 'o-', label=f"Converted ({CURRENCY})", alpha=0.7)
    plt.plot(df_grouped[YEAR_COLUMN], y_pred_usd, '--', label=f"{CURRENCY} trend", color="green")
    plt.xlabel("Year")
    plt.ylabel("Average Price")
    plt.title(f"Currency Conversion Effect: {cur_selected} → {CURRENCY}")
    plt.legend()
    plt.tight_layout()

    plot_path = os.path.join(filepath, f"currency_trend_{cur_selected}.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()

    print(f"Saved: {plot_path}")
    print("==== Currency influence analysis completed ====")


def filter_by_country(df: pd.DataFrame, country: str) -> pd.DataFrame:
    print(f"\n==== Filtering data for country: {country} ====")
    if COUNTRY_COLUMN not in df.columns:
        print(f"Column '{COUNTRY_COLUMN}' not found in data.")
        return df
    
    filtered = df[df[COUNTRY_COLUMN] == country].copy()
    print(f"Remaining rows: {len(filtered)}")
    return filtered

def create_categories(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    grains = ['Wheat - Retail', 'Wheat - Wholesale', 'Rice - Retail', 'Rice - Wholesale',
              'Maize - Retail', 'Maize - Wholesale', 'Barley - Retail', 'Millet - Retail',
              'Millet - Wholesale', 'Sorghum - Retail', 'Sorghum - Wholesale']
    
    dairy = ['Milk - Retail', 'Milk (cow, pasteurized) - Retail', 
             'Milk (cow, fresh) - Retail', 'Milk (camel) - Retail', 
             'Milk (non-pasteurized) - Retail', 'Milk (condensed) - Retail']
    
    meat = ['Meat (chicken) - Retail', 'Meat (chicken) - Wholesale', 'Meat (beef) - Retail',
            'Meat (beef, minced) - Wholesale', 'Meat (pork) - Retail', 'Meat (mutton) - Retail',
            'Meat (camel) - Retail', 'Livestock (sheep, one-year-old alive female) - Retail',
            'Livestock (Goat) - Retail']
    
    legumes = ['Beans - Retail', 'Beans - Wholesale', 'Beans (red) - Retail', 'Beans (red) - Wholesale',
               'Beans (white) - Retail', 'Beans (white) - Wholesale', 'Chickpeas - Retail',
               'Chickpeas (imported) - Wholesale', 'Lentils - Retail', 'Lentils - Wholesale',
               'Soybeans - Wholesale', 'Groundnuts (unshelled) - Retail', 'Groundnuts (shelled) - Retail']
    
    oils = ['Oil (palm) - Retail', 'Oil (mustard) - Retail', 'Oil (sunflower) - Retail',
            'Oil (sunflower) - Wholesale', 'Oil (vegetable) - Retail', 'Oil (vegetable, imported) - Retail',
            'Oil (vegetable, local) - Retail', 'Oil (cotton) - Retail', 'Oil (olive) - Retail']
    
    category_map = {
        'Grains': grains,
        'Dairy': dairy,
        'Meat': meat,
        'Legumes': legumes,
        'Oils': oils
    }
    
    df['category'] = None
    for cat, items in category_map.items():
        df.loc[df['cm_name'].isin(items), 'category'] = cat
        
    df = df.dropna(subset=['category'])
    return df

def select_categories_by_variant(df: pd.DataFrame, variant: int) -> list:
    print("\n==== Selecting categories based on variant ====")
    available_categories = sorted(df['category'].unique())
    
    if len(available_categories) < 2:
        print("Not enough available categories.")
        return []
    
    idx1 = variant % len(available_categories)
    idx2 = (variant + 1) % len(available_categories)
    
    selected = [available_categories[idx1], available_categories[idx2]]
    print(f"Selected categories for variant {variant}: {selected}")
    return selected

def compare_categories(df: pd.DataFrame, categories: list) -> tuple[LinearRegression, pd.DataFrame, pd.Series] | None:
    print("\n==== Comparing Selected Categories ====")
    if len(categories) != 2:
        print("Need exactly two categories to compare.")
        return None

    cat1, cat2 = categories
    required_cols = {YEAR_COLUMN, MONTH_COLUMN, 'category', PRICE_COLUMN}
    if not required_cols.issubset(df.columns):
        print(f"Data must contain columns: {required_cols}")
        return None

    grouped = (
        df.groupby([YEAR_COLUMN, MONTH_COLUMN, 'category'])[PRICE_COLUMN]
        .mean()
        .reset_index()
    )

    pivoted = grouped.pivot_table(
        index=[YEAR_COLUMN, MONTH_COLUMN],
        columns='category',
        values=PRICE_COLUMN
    ).dropna()

    if cat1 not in pivoted.columns or cat2 not in pivoted.columns:
        print(f"Categories {cat1} or {cat2} not found in data.")
        return None

    print("\n=== Descriptive statistics ===")
    print(pivoted[[cat1, cat2]].describe())

    pivoted_log = np.log(pivoted[[cat1, cat2]]).reset_index()

    X = pivoted_log[[cat1, YEAR_COLUMN, MONTH_COLUMN]]
    y = pivoted_log[cat2]

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)

    mae = mean_absolute_error(y, y_pred)
    rmse = mean_squared_error(y, y_pred) ** 0.5
    r2 = r2_score(y, y_pred)

    print(f"\nRegression {cat2} ~ {cat1}:")
    print(f"MAE = {mae:.2f}, RMSE = {rmse:.2f}, R² = {r2:.3f}")

    filepath = os.path.join(OUTPUT_DIR, "task_10")
    os.makedirs(filepath, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.scatter(y, y_pred, alpha=0.7, label='Predicted vs Actual')
    plt.plot([y.min(), y.max()], [y.min(), y.max()], color='red', linestyle='--')
    plt.xlabel(f"log({cat2}) Actual")
    plt.ylabel(f"log({cat2}) Predicted")
    plt.title(f"{cat2} Regression fit ({cat1}, year, month)")
    plt.legend()
    scatter_path = os.path.join(filepath, f"scatter_{cat1}_vs_{cat2}.png")
    plt.savefig(scatter_path, dpi=300)
    plt.close()
    print(f"Saved: {scatter_path}")

    plt.figure(figsize=(10, 6))
    plt.plot(pivoted.index.get_level_values(YEAR_COLUMN), pivoted[cat1], marker='o', label=cat1)
    plt.plot(pivoted.index.get_level_values(YEAR_COLUMN), pivoted[cat2], marker='o', label=cat2)
    plt.xlabel('Year')
    plt.ylabel('Average Price')
    plt.title(f'Yearly Price Trends: {cat1} vs {cat2}')
    plt.legend()
    trend_path = os.path.join(filepath, f"trend_{cat1}_vs_{cat2}.png")
    plt.savefig(trend_path, dpi=300)
    plt.close()
    print(f"Saved: {trend_path}")

    results_df = pivoted_log[[cat1, YEAR_COLUMN, MONTH_COLUMN]].copy()
    print("\nComparison analysis completed successfully.")
    return model, results_df, y


def main():
    #Task 1 - Load, filter, and analyze dataset
    print(f"\n{YELLOW}==== Task 1: Load, Filter, and Analyze Dataset ===={RESET}\n")
    df = read_dataset(DATASET_PATH)
    filtered_df = filter_data(df)
    product, country = select_product_and_country(filtered_df, VARIANT)
    stats = compute_statistics(filtered_df)
    ctab = create_crosstab(filtered_df)
    plot_boxplot(filtered_df, product)

    #Task 2 - Visualize trends for a specific product
    print(f"\n{YELLOW}==== Task 2: Visualize Trends for Specific Product ===={RESET}\n")
    visualize_trends(filtered_df, product, country)

    #Task 3 - Handle missing values and encode categorical data
    print(f"\n{YELLOW}==== Task 3: Handle Missing Values and Encode Categorical Data ===={RESET}\n")
    cleaned_df = handle_missing_values(filtered_df)
    encoded_df, encoded_col = encode_variant_column(cleaned_df, VARIANT)
    plot_encoded_scatter(encoded_df, encoded_col)

    #Task 4 - Correlation analysis
    print(f"\n{YELLOW}==== Task 4: Correlation Analysis ===={RESET}\n")
    correlation_analysis(cleaned_df, VARIANT)

    #Task 5 - Linear regression forecasting
    print(f"\n{YELLOW}==== Task 5: Linear Regression Forecasting ===={RESET}\n")
    model, X, y = linear_regression_forecast(cleaned_df, product)
    sensitivity_analysis(model, X, y, sub_dir="task_5", feature_names=[YEAR_COLUMN, MONTH_COLUMN])

    #Task 6 - MLP neural network forecasting
    print(f"\n{YELLOW}==== Task 6: MLP Neural Network Forecasting ===={RESET}\n")
    mlp_model, X_mlp, y_mlp = mlp_forecast(cleaned_df, product)
    sensitivity_analysis(mlp_model, X_mlp, y_mlp, sub_dir="task_6", feature_names=[YEAR_COLUMN, MONTH_COLUMN])

    #Task 7 - Market relationship analysis
    print(f"\n{YELLOW}==== Task 7: Market Relationship Analysis ===={RESET}\n")
    rel_model, X_rel, y_rel = analyze_market_relationships(cleaned_df)
    sensitivity_analysis(rel_model, X_rel, y_rel, sub_dir="task_7", feature_names=[MARKET_PRICE_COLUMN])

    #Task 8 - Currency influence analysis
    print(f"\n{YELLOW}==== Task 8: Currency Influence Analysis ===={RESET}\n")
    analyze_currency_influence(cleaned_df, VARIANT)

    #Task 9 - Sensitivity analysis for linear regression model 
    print(f"\n{YELLOW}==== Task 9: Sensitivity Analysis for Linear Regression Model ===={RESET}\n")
    sensitivity_analysis(model, X, y, sub_dir="task_9", feature_names=["mp_year"], plot_type="bar")

    #Task 10 - Category comparison based on variant
    print(f"\n{YELLOW}==== Task 10: Category Comparison Based on Variant ===={RESET}\n")
    df_country = filter_by_country(cleaned_df, country)
    df_with_categories = create_categories(df_country)
    selected_cats = select_categories_by_variant(df_with_categories, VARIANT)
    model_comp, X_comp, y_comp = compare_categories(df_with_categories, selected_cats)

    #Task 11 - Sensitivity analysis 
    print(f"\n{YELLOW}==== Task 11: Sensitivity Analysis for Category Comparison Model ===={RESET}\n")
    sensitivity_analysis(model_comp, X_comp, y_comp, sub_dir="task_11", feature_names=None, plot_type="line")

if __name__ == "__main__":
    main()