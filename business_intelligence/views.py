import os
import json
import pandas as pd
from django.shortcuts import render
from django.http import Http404

def dashboard_view(request):
    # Lokasi file hasil ETL
    airflow_csv_path = '/root/airflow/django2/business_intelligence/data/Walmart_Sales_Cleaned_Final.csv'

    if not os.path.exists(airflow_csv_path):
        raise Http404("Data hasil ETL dari Airflow tidak ditemukan.")

    df = pd.read_csv(airflow_csv_path, sep=';')
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['Month'] = df['Date'].dt.month

    # === SCHEMA 1 === Penjualan Bulanan: Holiday vs Non-Holiday
    monthly_sales = df.groupby(['Month', 'Holiday_Flag'])['Weekly_Sales'].mean().unstack().fillna(0)
    labels_schema1 = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    data_nonholiday = monthly_sales.get(0, pd.Series([0]*12)).tolist()
    data_holiday = monthly_sales.get(1, pd.Series([0]*12)).tolist()

    # === SCHEMA 2 === Pengaruh Suhu & Harga BBM
    df['Temp_Group'] = pd.cut(df['Temperature'], bins=2)
    df['Fuel_Group'] = pd.cut(df['Fuel_Price'], bins=2)
    external = df.groupby(['Fuel_Group', 'Temp_Group'])['Weekly_Sales'].sum().unstack().fillna(0)
    labels_schema2 = [str(idx) for idx in external.index]
    fuel_labels = [str(col) for col in external.columns]
    data_schema2 = external.values.tolist()

    # === SCHEMA 3 === Pengaruh CPI & Pengangguran
    df['CPI_Group'] = pd.cut(df['CPI'], bins=4)
    df['Unemp_Group'] = pd.cut(df['Unemployment'], bins=4)
    macro = df.groupby(['CPI_Group', 'Unemp_Group'])['Weekly_Sales'].mean().unstack().fillna(0)
    labels_schema3 = [str(idx) for idx in macro.index]
    unemp_labels = [str(col) for col in macro.columns]
    data_schema3 = macro.transpose().values.tolist()

    #  Tren Mingguan
    df_weekly = df.groupby('Date')['Weekly_Sales'].sum().reset_index()
    labels_weekly = df_weekly['Date'].dt.strftime('%Y-%m-%d').tolist()
    data_weekly = df_weekly['Weekly_Sales'].tolist()

    #  Performa per Toko
    df_store = df.groupby('Store')['Weekly_Sales'].mean().sort_values(ascending=False)
    labels_store = df_store.index.astype(str).tolist()
    data_store = df_store.tolist()

    context = {
        # SCHEMA 1
        'labels_schema1': labels_schema1,
        'data_nonholiday': data_nonholiday,
        'data_holiday': data_holiday,

        # SCHEMA 2
        'labels_schema2': labels_schema2,
        'fuel_labels': fuel_labels,
        'data_schema2': data_schema2,

        # SCHEMA 3
        'labels_schema3': labels_schema3,
        'unemp_labels': unemp_labels,
        'data_schema3': data_schema3,

        
        'labels_weekly': labels_weekly,
        'data_weekly': data_weekly,
        'labels_store': labels_store,
        'data_store': data_store,
    }

    return render(request, 'business_intelligence/dashboard.html', context)
