import pymysql
import pandas as pd
from sqlalchemy import create_engine

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "Root2006!",
    "database": "shop"
}

WAREHOUSE_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "Root2006!",
    "database": "shop_data_warehouse"
}

USER_QUERY = "SELECT id FROM user;"
PRODUCT_QUERY = "SELECT id, name, price FROM product;"
ORDER_QUERY = """
    SELECT o.id AS order_id, u.id AS user_id, p.id AS product_id, 
           p.price, o.date_time
    FROM `order` o
    JOIN `user` u ON o.user_id = u.id
    JOIN product p ON o.product_id = p.id;
"""

def extract_data(query):
    connection = pymysql.connect(**DB_CONFIG)
    try:
        data = pd.read_sql(query, connection)
        return data
    except Exception as e:
        print(f"Error: Failed to extract data.\n{e}")
    finally:
        connection.close()

def clean_data(df):
    df = df.dropna()  
    for col in df.select_dtypes(include=["number"]).columns:
        df[col] = df[col].fillna(0).astype(float) 
    return df

def validate_data(df, required_columns):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    return True

def calculate_user_expenses(order_data):
    user_expense_summary = order_data.groupby('user_id').agg(
        total_expense=pd.NamedAgg(column='price', aggfunc='sum')
    ).reset_index()
    return user_expense_summary

def calculate_product_summary(order_data, product_data):
    product_purchase_summary = order_data.groupby(['product_id']).agg(
        total_quantity=pd.NamedAgg(column='product_id', aggfunc='count'),
        total_revenue=pd.NamedAgg(column='price', aggfunc='sum')
    ).reset_index()

    # Додаємо назви продуктів
    product_purchase_summary = product_purchase_summary.merge(
        product_data[['id', 'name']],
        how='left',
        left_on='product_id',
        right_on='id'
    )
    product_purchase_summary.rename(columns={'name': 'product_name'}, inplace=True)
    return product_purchase_summary

def calculate_daily_orders(order_data):
    daily_order_summary = order_data.groupby('date_time').agg(
        total_orders=pd.NamedAgg(column='order_id', aggfunc='count'),
        total_sales=pd.NamedAgg(column='price', aggfunc='sum')
    ).reset_index()
    return daily_order_summary

def transform_data(user_data, product_data, order_data):
    validate_data(order_data, ['user_id', 'product_id', 'price', 'date_time'])
    validate_data(product_data, ['id', 'name'])
    validate_data(user_data, ['id'])

    order_data = clean_data(order_data)
    product_data = clean_data(product_data)
    user_data = clean_data(user_data)

    user_expenses = calculate_user_expenses(order_data)
    product_summary = calculate_product_summary(order_data, product_data)
    daily_orders = calculate_daily_orders(order_data)

    return user_expenses, product_summary, daily_orders

def load_data(dataframe, table_name):
    try:
        engine = create_engine(
            f"mysql+pymysql://{WAREHOUSE_CONFIG['user']}:{WAREHOUSE_CONFIG['password']}@"
            f"{WAREHOUSE_CONFIG['host']}:{WAREHOUSE_CONFIG['port']}/{WAREHOUSE_CONFIG['database']}"
        )
        dataframe.to_sql(table_name, con=engine, if_exists='replace', index=False)
    except Exception as e:
        print(f"Error: Failed to load data in '{table_name}'.\n{e}")

def run_etl():
    user_data = extract_data(USER_QUERY)
    product_data = extract_data(PRODUCT_QUERY)
    order_data = extract_data(ORDER_QUERY)
    user_expenses, product_summary, daily_orders = transform_data(user_data, product_data, order_data)
    load_data(user_expenses, 'user_expense_summary')
    load_data(product_summary, 'product_purchase_summary')
    load_data(daily_orders, 'daily_order_summary')

run_etl()