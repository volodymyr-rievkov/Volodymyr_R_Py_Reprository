import os
import warnings
import logging
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import timedelta
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO)

from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Dropout, Bidirectional
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.optimizers import Adam

LOOK_BACK = 104 
EPOCHS = 100    
BATCH_SIZE = 32

TEST_WEEKS = 26

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CUR_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
PLOTS_DIR = os.path.join(DATA_DIR, 'plots')
os.makedirs(PLOTS_DIR, exist_ok=True)
ACF_SEAS_DIR = os.path.join(DATA_DIR, 'acf_seasonality')
os.makedirs(ACF_SEAS_DIR, exist_ok=True)
MODEL_DIR = os.path.join(DATA_DIR, 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
DATASET_PATH = os.path.join(DATA_DIR, 'Seasonal_influenza.csv')

COLUMNS = {'weekending': 'date', 'region': 'region', 'Respiratory_Virus': 'virus_type', 'Number_Positive': 'positive_cases'}

def load_data():
    logging.info(f"Loading dataset from {DATASET_PATH}")
    data = pd.read_csv(DATASET_PATH)
    
    data = data[COLUMNS.keys()]
    data = data.rename(columns=COLUMNS)

    data['positive_cases'] = pd.to_numeric(data['positive_cases'], errors='coerce').fillna(0)
    data['date'] = pd.to_datetime(data['date'])
    
    is_total_row = data['virus_type'].str.contains('Total', case=False, na=False)
    
    df_totals = data[is_total_row].groupby(['region', 'date'], as_index=False)['positive_cases'].sum()    
    df_components = data[~is_total_row].groupby(['region', 'date'], as_index=False)['positive_cases'].sum()
    
    merged = pd.merge(
        df_totals, 
        df_components, 
        on=['region', 'date'], 
        how='outer', 
        suffixes=('_total', '_components')
    )
    
    merged['positive_cases_total'] = merged['positive_cases_total'].fillna(0)
    merged['positive_cases_components'] = merged['positive_cases_components'].fillna(0)
    
    merged['positive_cases'] = merged[['positive_cases_total', 'positive_cases_components']].max(axis=1)
    
    final_data = merged[['region', 'date', 'positive_cases']].sort_values(by='date').reset_index(drop=True)
    
    logging.info(f"Data loaded. Shape: {final_data.shape}")
    return final_data

def handle_missing_values(df):
    logging.info("Handling missing values per region...")
    
    df = df.sort_values(by=['region', 'date'])
    df = df.dropna(subset=['region', 'date'])

    found = False
    for col in df.columns:
        if col in ['region', 'date']:
            continue

        missing_count = df[col].isnull().sum()
        
        if missing_count > 0:
            found = True
            logging.info(f"Column '{col}' has {missing_count} missing values")
            
            if df[col].dtype == 'object':
                df[col] = df[col].fillna(df[col].mode()[0])
            else:
                df[col] = df.groupby('region')[col].transform(
                    lambda x: x.interpolate(method='linear')
                )
                df[col] = df[col].fillna(df.groupby('date')[col].transform('mean'))              
                df[col] = df[col].fillna(df.groupby('region')[col].transform('mean'))
                df[col] = df[col].fillna(0)

    logging.info("Missing values handled" if found else "No missing values found")
    return df

def visualize_cases_histogram(df):
    logging.info("Visualizing total influenza cases by region")
    region_summary = df.groupby('region')['positive_cases'].sum().sort_values(ascending=False)
    plt.figure(figsize=(12,6))
    bars = plt.bar(region_summary.index, region_summary.values, color='skyblue')
    plt.title('Total Influenza Cases by Region')
    plt.xlabel('Region')
    plt.ylabel('Total Positive Cases')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 5, f'{int(height)}', ha='center', va='bottom')
    plt.tight_layout()
    fig_path = os.path.join(PLOTS_DIR, 'total_cases_by_region.png')
    plt.savefig(os.path.join(fig_path))
    plt.close()
    logging.info(f"Histogram saved to {fig_path}")

def visualize_top_regions_chronology(df, n_top=3):
    logging.info(f"Visualizing chronology for top {n_top} regions")
    region_summary = df.groupby('region')['positive_cases'].sum().sort_values(ascending=False)
    top_regions = region_summary.head(n_top).index.tolist()
    df_top = df[df['region'].isin(top_regions)]
    df_pivot = df_top.pivot_table(index='date', columns='region', values='positive_cases', aggfunc='sum')
    plt.figure(figsize=(14,7))
    for region in top_regions:
        if region in df_pivot.columns:
            plt.plot(df_pivot.index, df_pivot[region], label=f"{region} ({region_summary[region]})", alpha=0.8, linewidth=2)
    plt.title(f'Chronology of Total Influenza Cases - Top {n_top} Regions')
    plt.xlabel('Date')
    plt.ylabel('Number of Positive Cases')
    plt.legend(title='Region')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(rotation=45)
    plt.tight_layout()
    fig_path = os.path.join(PLOTS_DIR, 'top_regions_chronology.png')
    plt.savefig(fig_path)
    plt.close()
    logging.info(f"Top regions chronology plot saved to {fig_path}")
    return top_regions

def boxplot_individual_regions(df, regions):
    logging.info("Creating boxplots and calculating statistics for individual regions")
    
    for region in regions:
        df_region = df[df['region'] == region]
        cases = df_region['positive_cases']
        
        # --- РОЗРАХУНОК СТАТИСТИКИ ---
        # Отримуємо базові статистики через describe()
        stats = cases.describe()
        
        Q1 = stats['25%']
        Q3 = stats['75%']
        IQR = Q3 - Q1
        median = stats['50%']
        minimum = stats['min']
        maximum = stats['max']
        mean_val = stats['mean']
        
        # Розрахунок меж вусів (стандартно 1.5 * IQR)
        # Викидами вважаються точки за межами [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Знаходимо реальні викиди в даних
        outliers = cases[(cases < lower_bound) | (cases > upper_bound)]
        num_outliers = len(outliers)
        
        # --- ВИВІД У КОНСОЛЬ ---
        logging.info(f"\n{'='*40}")
        logging.info(f"STATISTICS FOR REGION: {region}")
        logging.info(f"{'-'*40}")
        logging.info(f"Total Records : {int(stats['count'])}")
        logging.info(f"Mean          : {mean_val:.2f}")
        logging.info(f"Std Dev       : {stats['std']:.2f}")
        logging.info(f"{'-'*40}")
        logging.info(f"Min           : {minimum:.2f}")
        logging.info(f"Q1 (25%)      : {Q1:.2f}")
        logging.info(f"Median (50%)  : {median:.2f}")
        logging.info(f"Q3 (75%)      : {Q3:.2f}")
        logging.info(f"Max           : {maximum:.2f}")
        logging.info(f"IQR           : {IQR:.2f}")
        logging.info(f"{'-'*40}")
        logging.info(f"Outlier Bounds: [{lower_bound:.2f}, {upper_bound:.2f}]")
        logging.info(f"Outliers Count: {num_outliers}")
        logging.info(f"{'='*40}\n")

        # --- ПОБУДОВА ГРАФІКА ---
        plt.figure(figsize=(8,6))
        plt.boxplot(
            cases,
            vert=True,
            patch_artist=True,
            boxprops=dict(facecolor='skyblue', color='blue', linewidth=1.5),
            medianprops=dict(color='red', linewidth=2),
            whiskerprops=dict(color='blue', linewidth=1.5),
            capprops=dict(color='blue', linewidth=1.5),
            flierprops=dict(marker='o', markerfacecolor='orange', markersize=5, linestyle='none')
        )
        plt.title(f'Boxplot of Positive Influenza Cases - {region}')
        plt.ylabel('Positive Cases')
        
        # Масштабування осі Y для кращої видимості
        upper_limit = cases.quantile(0.95) * 1.05
        plt.ylim(0, max(upper_limit, maximum))
        
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        
        plt_path = os.path.join(PLOTS_DIR, f'boxplot_{region.replace(" ","_").replace("/","_")}.png')
        plt.savefig(plt_path)
        plt.close()
        logging.info(f"Boxplot saved to {plt_path}")

def analyze_autocorrelation_and_seasonality(df, regions, period):
    logging.info("Analyzing autocorrelation and seasonality")
    for region in regions:
        df_region = df[df['region'] == region].sort_values('date')
        series = df_region.set_index('date')['positive_cases']
        plt.figure(figsize=(10,4))
        plot_acf(series, lags=50, alpha=0.05)
        plt.title(f'Autocorrelation (ACF) - {region}')
        plt.tight_layout()
        plt_path = os.path.join(ACF_SEAS_DIR, f'acf_{region.replace(" ","_").replace("/","_")}.png')
        plt.savefig(plt_path)
        logging.info(f"ACF plot saved to {plt_path}")
        plt.close()
        
        try:
            decomposition = seasonal_decompose(series, model='additive', period=period, extrapolate_trend='freq')
            plt.figure(figsize=(12,8))
            decomposition.plot()
            plt.suptitle(f'Seasonal Decomposition - {region}')
            plt.tight_layout(rect=[0,0.03,1,0.95])
            plt_path = os.path.join(ACF_SEAS_DIR, f'seasonal_decomposition_{region.replace(" ","_").replace("/","_")}.png')
            plt.savefig(plt_path)
            plt.close()
            logging.info(f"Seasonal decomposition plot saved to {plt_path}")
        except Exception as e:
            logging.warning(f"Seasonal decomposition failed for {region}: {e}")

def create_dataset(dataset, look_back=1):
    data_X, data_Y = [], []
    for i in range(len(dataset) - look_back):
        a = dataset[i:(i + look_back), :]
        data_X.append(a)
        data_Y.append(dataset[i + look_back, 0])
    return np.array(data_X), np.array(data_Y)

def build_and_train_model(df, region, look_back, test_weeks, epochs, batch_size):
    logging.info(f"--- Processing Region: {region} ---")
    
    safe_region_name = region.replace(" ","_").replace("/","_")
    model_path = os.path.join(MODEL_DIR, f'lstm_{safe_region_name}_{LOOK_BACK}.keras')

    region_data = df[df['region'] == region].sort_values('date')
    region_data = region_data[region_data['date'] < '2020-01-01'] 
    
    dates = region_data['date'].values
    values = region_data['positive_cases'].values.reshape(-1, 1)

    months = pd.DatetimeIndex(dates).month.to_numpy()
    
    sin_time = np.sin(2 * np.pi * months / 12).reshape(-1, 1)
    cos_time = np.cos(2 * np.pi * months / 12).reshape(-1, 1)
    
    train_size = len(values) - test_weeks
    
    if train_size <= look_back:
        logging.warning(f"Not enough data for region {region}. Skipping.")
        return

    train_raw_cases = values[:train_size]
    test_raw_cases = values[train_size - look_back:] 
    
    scaler_path = os.path.join(MODEL_DIR, f'scaler_{safe_region_name}_{LOOK_BACK}.pkl')

    if os.path.exists(scaler_path):
        logging.info(f"Existing scaler found. Loading...")
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
    else:
        logging.info("Fitting new scaler...")
        scaler = StandardScaler()
        scaler.fit(train_raw_cases)
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
    
    train_cases_scaled = scaler.transform(train_raw_cases)
    test_cases_scaled = scaler.transform(test_raw_cases)

    train_sin = sin_time[:train_size]
    train_cos = cos_time[:train_size]
    
    test_sin = sin_time[train_size - look_back:]
    test_cos = cos_time[train_size - look_back:]
    
    train_combined = np.hstack((train_cases_scaled, train_sin, train_cos))
    test_combined = np.hstack((test_cases_scaled, test_sin, test_cos))
    
    X_train, y_train = create_dataset(train_combined, look_back)
    X_test, y_test = create_dataset(test_combined, look_back)
    
    NUM_FEATURES = 3
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], NUM_FEATURES))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], NUM_FEATURES))
    
    if os.path.exists(model_path):
        logging.info(f"Existing model found. Loading...")
        model = load_model(model_path)
    else:
        logging.info(f"Training new model for {region}...")
        
        model = Sequential()
        model.add(Bidirectional(LSTM(64, return_sequences=True), input_shape=(look_back, NUM_FEATURES)))
        model.add(Dropout(0.2))
        model.add(LSTM(32, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(16, activation='relu'))
        model.add(Dense(1))
        
        opt = Adam(learning_rate=0.002)
        model.compile(loss='mean_absolute_error', optimizer=opt) 
        
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=1),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=0.00001, verbose=1)
        ]

        history = model.fit(
            X_train, y_train, 
            epochs=epochs, 
            batch_size=batch_size, 
            validation_data=(X_test, y_test), 
            callbacks=callbacks,
            verbose=1,
            shuffle=False
        )
        
        model.save(model_path)
        logging.info(f"Model saved to {model_path}")

    train_predict = model.predict(X_train)
    test_predict = model.predict(X_test)
    
    y_train_inv = scaler.inverse_transform(y_train.reshape(-1, 1))
    y_test_inv = scaler.inverse_transform(y_test.reshape(-1, 1))
    test_predict_inv = scaler.inverse_transform(test_predict)
    
    test_predict_inv[test_predict_inv < 0] = 0
    
    rmse, mae, r2 = evaluate_forecast(y_test_inv, test_predict_inv)
    logging.info(f"Region: {region} | RMSE: {rmse:.2f} | MAE: {mae:.2f} | R2: {r2:.2f}")

    plot_dates = dates[-len(y_test_inv):]

    comparison_df = pd.DataFrame({
        'Date': plot_dates,
        'Actual': y_test_inv.flatten(),
        'Predicted': test_predict_inv.flatten()
    })

    comparison_df['Date'] = pd.to_datetime(comparison_df['Date'])
    comparison_df['Diff'] = comparison_df['Actual'] - comparison_df['Predicted']
    
    table_str = comparison_df.to_string(
        index=False, 
        max_rows=10, 
        formatters={
            'Date': lambda x: x.strftime('%Y-%m-%d'),
            'Actual': lambda x: f"{x:.2f}",
            'Predicted': lambda x: f"{x:.2f}",
            'Diff': lambda x: f"{x:+.2f}"
        }
    )
    
    logging.info(f"Forecast Details:\n{table_str}")

    plot_forecast_vs_actual(plot_dates, y_test_inv, test_predict_inv, region)
    logging.info(f"--- Finished processing Region: {region} ---")

def evaluate_forecast(y_true, y_pred):
    min_len = min(len(y_true), len(y_pred))
    y_true = y_true[:min_len]
    y_pred = y_pred[:min_len]
    
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return rmse, mae, r2

def plot_forecast_vs_actual(dates, y_true, y_pred, region):
    min_len = min(len(dates), len(y_true), len(y_pred))
    dates = dates[:min_len]
    y_true = y_true[:min_len]
    y_pred = y_pred[:min_len]

    plt.figure(figsize=(12,6))
    plt.plot(dates, y_true, label='Actual Data', color='blue', linewidth=2)
    plt.plot(dates, y_pred, label='LSTM Forecast', color='red', linestyle='--', linewidth=2)
    
    plt.title(f'Forecast vs Actual - {region}')
    plt.xlabel('Date')
    plt.ylabel('Positive Cases')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    
    safe_region = region.replace(" ","_").replace("/","_")
    plt.savefig(os.path.join(MODEL_DIR, f'forecast_{TEST_WEEKS}_vs_actual_{safe_region}.png'))
    plt.close()

def visualize_future_forecast(region, history_df, forecast_df):
    logging.info(f"Visualizing future forecast for {region}")
    
    plt.figure(figsize=(14, 7))
    
    plt.plot(history_df['date'], history_df['positive_cases'], 
             label='Historical Data', color='blue', linewidth=2)
    
    last_hist_date = history_df.iloc[-1]['date']
    last_hist_val = history_df.iloc[-1]['positive_cases']
    
    plot_forecast_dates = [last_hist_date] + list(forecast_df['date'])
    plot_forecast_vals = [last_hist_val] + list(forecast_df['predicted_cases'])
    
    plt.plot(plot_forecast_dates, plot_forecast_vals, 
             label='Future Forecast', color='red', linestyle='--', linewidth=2, marker='o', markersize=4)

    plt.title(f'Future Influenza Forecast - {region}')
    plt.xlabel('Date')
    plt.ylabel('Predicted Cases')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    safe_region = region.replace(" ", "_").replace("/", "_")
    plot_path = os.path.join(MODEL_DIR, f'future_{len(forecast_df)}_forecast_{safe_region}.png')
    
    plt.savefig(plot_path)
    plt.close()
    logging.info(f"Future forecast plot saved to {plot_path}")

def predict_future_weeks(df, region, n_weeks):
    logging.info(f"--- Starting future forecast for Region: {region} ({n_weeks} weeks) ---")
    
    safe_region_name = region.replace(" ", "_").replace("/", "_")
    model_path = os.path.join(MODEL_DIR, f'lstm_{safe_region_name}_{LOOK_BACK}.keras')
    scaler_path = os.path.join(MODEL_DIR, f'scaler_{safe_region_name}_{LOOK_BACK}.pkl')

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        logging.error(f"Model or scaler not found for {region}. Please train the model first.")
        return

    try:
        model = load_model(model_path)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
    except Exception as e:
        logging.error(f"Error loading model/scaler: {e}")
        return

    region_data = df[df['region'] == region].sort_values('date')
    last_window_data = region_data.tail(LOOK_BACK)
    last_date = last_window_data['date'].max()
    
    input_cases = last_window_data['positive_cases'].values.reshape(-1, 1)
    input_scaled_cases = scaler.transform(input_cases)
    
    input_months = pd.DatetimeIndex(last_window_data['date']).month.to_numpy()
    
    input_sin = np.sin(2 * np.pi * input_months / 12).reshape(-1, 1)
    input_cos = np.cos(2 * np.pi * input_months / 12).reshape(-1, 1)
    
    input_combined = np.hstack((input_scaled_cases, input_sin, input_cos))
    current_batch = input_combined.reshape(1, LOOK_BACK, 3)
    
    future_predictions = []
    future_dates = []

    for i in range(n_weeks):
        pred_scaled = model.predict(current_batch, verbose=0)
        future_predictions.append(pred_scaled[0, 0])
        
        next_date = last_date + timedelta(weeks=(i + 1))
        future_dates.append(next_date)
        
        next_month = next_date.month
        next_sin = np.sin(2 * np.pi * next_month / 12)
        next_cos = np.cos(2 * np.pi * next_month / 12)
        
        new_step = np.array([[pred_scaled[0, 0], next_sin, next_cos]])
        new_step = new_step.reshape(1, 1, 3)
        
        current_batch = np.append(current_batch[:, 1:, :], new_step, axis=1)

    future_predictions = np.array(future_predictions).reshape(-1, 1)
    future_predictions_inv = scaler.inverse_transform(future_predictions)
    future_predictions_inv[future_predictions_inv < 0] = 0

    forecast_df = pd.DataFrame({
        'date': future_dates,
        'predicted_cases': future_predictions_inv.flatten()
    })
    forecast_str = forecast_df.to_string(
        index=False, 
        max_rows=10, 
        formatters={
            'date': lambda x: x.strftime('%Y-%m-%d'),
            'predicted_cases': lambda x: f"{x:.2f}"
        }
    )
    logging.info(f"Generated forecast for next {n_weeks} weeks.\n {forecast_str}")
    
    history_context = region_data.tail(104)[['date', 'positive_cases']]
    visualize_future_forecast(region, history_context, forecast_df)
    
    return forecast_df

if __name__ == "__main__":
    df = load_data()
    df = handle_missing_values(df)
    visualize_cases_histogram(df)
    top_regions = visualize_top_regions_chronology(df, n_top=2)
    boxplot_individual_regions(df, top_regions)
    analyze_autocorrelation_and_seasonality(df, top_regions, period=LOOK_BACK)

    for region in top_regions:
        build_and_train_model(df, region, LOOK_BACK, TEST_WEEKS, EPOCHS, BATCH_SIZE)
        predict_future_weeks(df, region, n_weeks=26)

    logging.info("All processing completed.")