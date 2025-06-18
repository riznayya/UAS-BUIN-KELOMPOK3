from django.db import models

# Create your models here.
# Dimensi Tanggal
class DimDate(models.Model):
    date_id = models.AutoField(primary_key=True)  # PK otomatis
    full_date = models.DateField()                # misal YYYY-MM-DD
    week = models.IntegerField()
    month = models.IntegerField()
    year = models.IntegerField()
    weekday_name = models.CharField(max_length=20)

    def __str__(self):
        return str(self.full_date)  # agar mudah dibaca di admin

# Dimensi Store
class DimStore(models.Model):
    store_id = models.AutoField(primary_key=True)
    store_name = models.CharField(max_length=100)
    store_size = models.CharField(max_length=50)

    def __str__(self):
        return self.store_name

# Dimensi Holiday
class DimHoliday(models.Model):
    holiday_id = models.AutoField(primary_key=True)
    holiday_flag = models.BooleanField()           # True/False
    holiday_name = models.CharField(max_length=100, blank=True, null=True)
    holiday_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.holiday_name if self.holiday_name else f"Flag {self.holiday_flag}"

# Dimensi Region (default “Unknown” atau sesuaikan data region-mu)
class DimRegion(models.Model):
    region_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.city}, {self.state}"

# Dimensi Sales Channel (jika kamu hanya pakai satu, bisa default “Unknown”)
class DimSalesChannel(models.Model):
    channel_id = models.AutoField(primary_key=True)
    channel_name = models.CharField(max_length=100)

    def __str__(self):
        return self.channel_name

# Tabel Fakta: FactSales
class FactSales(models.Model):
    date = models.ForeignKey(DimDate, on_delete=models.CASCADE)
    store = models.ForeignKey(DimStore, on_delete=models.CASCADE)
    holiday = models.ForeignKey(DimHoliday, on_delete=models.CASCADE)
    region = models.ForeignKey(DimRegion, on_delete=models.CASCADE)
    channel = models.ForeignKey(DimSalesChannel, on_delete=models.CASCADE)
    weekly_sales = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"Sales {self.weekly_sales} pada {self.date.full_date}"

