from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os


base_path = '/root/airflow/django2/business_intelligence/data'
csv_path = os.path.join(base_path, 'Walmart_Sales_Cleaned_Final.csv')
extracted_path = '/tmp/walmart_extracted.csv'
transformed_path = '/tmp/walmart_transformed.csv'
output_path = csv_path 


def extract():
    df = pd.read_csv(csv_path, sep=';')
    df.to_csv(extracted_path, index=False)
    print("✅ Extract done")


def transform():
    df = pd.read_csv(extracted_path)
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['Month'] = df['Date'].dt.month
    df['Month_Name'] = df['Date'].dt.strftime('%B')
    df.to_csv(transformed_path, index=False)
    print("✅ Transform done")


def load():
    df = pd.read_csv(transformed_path)
    df.to_csv(output_path, index=False)
    print("✅ Load done to:", output_path)


default_args = {
    'start_date': datetime(2025, 6, 12),
    'retries': 1,
}

with DAG(
    dag_id='walmart_sales_etl',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False,
    tags=['walmart', 'etl']
) as dag:

    t1 = PythonOperator(
        task_id='extract',
        python_callable=extract
    )

    t2 = PythonOperator(
        task_id='transform',
        python_callable=transform
    )

    t3 = PythonOperator(
        task_id='load',
        python_callable=load
    )

    t1 >> t2 >> t3
