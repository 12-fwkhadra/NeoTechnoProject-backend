from django.db import models

class Client(models.Model):
    client_id = models.AutoField(primary_key=True)  # auto increment primary key
    name = models.CharField(max_length=255)
    email = models.EmailField()
    birthdate = models.DateField()
    country = models.CharField(max_length=100)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2)


class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True)  # auto increment primary key
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=50)
    transaction_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10)

