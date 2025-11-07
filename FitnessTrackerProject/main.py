import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import logging

HRV_FILE = 'PythonApplications/FitnessTrackerProject/data/sensor_hrv.csv'
SLEEP_FILE = 'PythonApplications/FitnessTrackerProject/data/sleep_diary.csv'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_hrv_data(file_path):
    logger.info("Loading HRV data...")
    df = pd.read_csv(file_path)
    df['ts_start'] = pd.to_datetime(df['ts_start'], unit='ms')
    df['date'] = df['ts_start'].dt.date
    df['user_id'] = df['deviceId']
    logger.info(f"HRV shape: {df.shape}")
    return df

def load_sleep_data(file_path):
    logger.info("Loading sleep data...")
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].dt.date
    df['user_id'] = df['userId']
    logger.info(f"Sleep shape: {df.shape}")
    return df

def aggregate_hrv_data(df_hrv):
    logger.info("Aggregating HRV data...")
    daily_hrv = df_hrv.groupby(['user_id', 'date']).agg({
        'HR': 'mean',
        'rmssd': 'mean',
        'steps': 'sum',
        'calories': 'sum'
    }).reset_index()
    logger.info(f"Daily HRV shape: {daily_hrv.shape}")
    return daily_hrv

def merge_data(daily_hrv, df_sleep):
    logger.info("Merging data...")
    df_merged = daily_hrv.merge(df_sleep[['user_id', 'date', 'sleep_duration', 'sleep_efficiency']], 
                                on=['user_id', 'date'], how='left')
    logger.info(f"Shape after merge: {df_merged.shape}")
    return df_merged

def handle_nan(df):
    logger.info("Handling NaN values...")
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].interpolate(method='time')
    df[numeric_cols] = df[numeric_cols].fillna(method='ffill').fillna(method='bfill')
    logger.info(f"NaN after handling: {df.isnull().sum().sum()}")
    return df.reset_index()

def normalize_data(df):
    logger.info("Normalizing data...")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    scaler = MinMaxScaler()
    df[numeric_cols] = scaler.fit_transform(df[numeric_cols])
    logger.info("Data normalized (0-1 scale)")
    return df

def split_data(df):
    logger.info("Splitting data...")
    train_size = int(len(df) * 0.8)
    train_df = df.iloc[:train_size].copy()
    test_df = df.iloc[train_size:].copy()
    logger.info(f"Train shape: {train_df.shape}, Test shape: {test_df.shape}")
    return train_df, test_df

def main():
    df_hrv = load_hrv_data(HRV_FILE)
    df_sleep = load_sleep_data(SLEEP_FILE)
    daily_hrv = aggregate_hrv_data(df_hrv)
    df_merged = merge_data(daily_hrv, df_sleep)
    df_processed = handle_nan(df_merged)
    df_normalized = normalize_data(df_processed)
    train_df, test_df = split_data(df_normalized)
    print("Columns after merge:", df_merged.columns.tolist())
    print("\nFirst 5 rows (after processing):")
    print(df_normalized.head())

if __name__ == "__main__":
    main()