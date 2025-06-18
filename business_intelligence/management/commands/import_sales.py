import os
import csv
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from business_intelligence.models import (
    DimDate, DimStore, DimHoliday, DimRegion, DimSalesChannel, FactSales
)

class Command(BaseCommand):
    help = 'Import data dari Walmart_Sales_Cleaned_Final.csv ke star schema (generate tanggal otomatis)'

    def handle(self, *args, **options):
        # 1) Siapkan DimHoliday (True / False)
        holiday_true, _ = DimHoliday.objects.get_or_create(
            holiday_flag=True,
            defaults={'holiday_name': 'Holiday', 'holiday_type': 'General'}
        )
        holiday_false, _ = DimHoliday.objects.get_or_create(
            holiday_flag=False,
            defaults={'holiday_name': 'Bukan Holiday', 'holiday_type': 'General'}
        )

        # 2) Siapkan DimRegion (default “Unknown”)
        region_default, _ = DimRegion.objects.get_or_create(
            city='Unknown',
            state='Unknown',
            country='Unknown'
        )

        # 3) Siapkan DimSalesChannel (default “Unknown”)
        channel_default, _ = DimSalesChannel.objects.get_or_create(
            channel_name='Unknown'
        )

        # 4) Tentukan path ke CSV
        csv_path = os.path.join(
            settings.BASE_DIR,
            'business_intelligence',
            'data',
            'Walmart_Sales_Cleaned_Final.csv'
        )
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"File CSV tidak ditemukan: {csv_path}"))
            return

        # 5) Hitung berapa baris CSV, supaya kita tahu rentang tanggal
        total_rows = 0
        with open(csv_path, newline='', encoding='utf-8') as f_count:
            reader = csv.reader(f_count)
            next(reader, None)  # lewati header
            for _ in reader:
                total_rows += 1

        # Definisikan tanggal awal—misal Senin minggu pertama
        # (ubah sesuai kebutuhan; contohnya Saya pakai 2010-01-04, karena 2010-01-01 adalah Jumat)
        # Jika ingin mulai tepat 2010-01-01, tinggal ganti.
        start_date = datetime.strptime('2010-01-04', '%Y-%m-%d').date()

        # 6) Sekarang baca ulang CSV, baris demi baris, dan assign tanggal berdasar urutan
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0
            for i, row in enumerate(reader):
                # a) DimStore: gunakan kolom “Store”
                store_id_value = int(row['Store'])
                store_obj, _ = DimStore.objects.get_or_create(
                    store_id=store_id_value,
                    defaults={'store_name': f'Store {store_id_value}', 'store_size': 'Medium'}
                )

                # b) Buat tanggal otomatis:
                #     date_obj = start_date + i minggu
                date_obj = start_date + timedelta(weeks=i)
                week = date_obj.isocalendar()[1]
                month = date_obj.month
                year = date_obj.year
                weekday_name = date_obj.strftime('%A')

                date_dim, _ = DimDate.objects.get_or_create(
                    full_date=date_obj,
                    defaults={
                        'week': week,
                        'month': month,
                        'year': year,
                        'weekday_name': weekday_name
                    }
                )

                # c) DimHoliday: berdasarkan “Holiday_Flag” (0/1)
                holiday_flag = True if row['Holiday_Flag'] in ['1','True','true'] else False
                holiday_obj = holiday_true if holiday_flag else holiday_false

                # d) Simpan FactSales
                try:
                    weekly_sales_val = float(row['Weekly_Sales'])
                except ValueError:
                    self.stdout.write(self.style.ERROR(f"Weekly_Sales tidak valid: {row}"))
                    continue

                FactSales.objects.create(
                    date=date_dim,
                    store=store_obj,
                    holiday=holiday_obj,
                    region=region_default,
                    channel=channel_default,
                    weekly_sales=weekly_sales_val
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Import data selesai! Total baris: {count}'))
