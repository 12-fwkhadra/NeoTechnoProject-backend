from decimal import Decimal, ROUND_DOWN

import pandas as pd
from django.http import JsonResponse
from NeoTechnoProject.models import Client, Transaction, Users
from django.db import IntegrityError, connection

'''
    this class functions responsible for applying ETL processes 
    the functions respectively extract data from the Clients.csv and Transactions.xlsx and load them in the database while handling null values and calculating the required fields
    in the urls.py, specific routes are defined to trigger these APIs
'''

def data_init(request):
    load_clients_to_db()
    load_trans_to_db()
    add_users()
    return JsonResponse({'message': f'Successfully initialized data.'}, status=200)
def load_clients_to_db():

    clients_df = pd.read_csv(r'NeoTechnoProject/clients.csv')

    clients_to_add = []
    try:
        for index, row in clients_df.iterrows():
            try:
                #create a new object of the Client table defined in models.py
                new_client = Client(
                    name = None if pd.isna(row['name']) else row['name'],
                    email = None if pd.isna(row['email']) else row['email'],
                    birthdate = None if pd.isna(row['date_of_birth']) else row['date_of_birth'],
                    country = None if pd.isna(row['country']) else row['country'],
                    account_balance = None if pd.isna(row['account_balance']) else row['account_balance']
                )
                clients_to_add.append(new_client)
            except IntegrityError as e:
                print(f'Error: {e}')

        if clients_to_add:
            #use bulk create to insert all instances to the Clients table at once for better performance
            Client.objects.bulk_create(clients_to_add)
            print(f"Successfully inserted {len(clients_to_add)} clients.")

            return JsonResponse({'message': f'Successfully inserted {len(clients_to_add)} clients.'}, status=200)
        else:
            return JsonResponse({'message': 'No transactions to insert.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def load_trans_to_db():
    trans_df = pd.read_excel(r'NeoTechnoProject/transactions.xlsx')

    transactions_to_create = []
    try:
        for index, row in trans_df.iterrows():
            try:
                # Get the client instance for the foreign key relationship
                client = Client.objects.get(client_id=row['client_id'])

                new_transaction = Transaction(
                        client_id=client.client_id,
                        transaction_type=None if pd.isna(row['transaction_type']) else row['transaction_type'],
                        transaction_date=None if pd.isna(row['transaction_date']) else row['transaction_date'],
                        amount=None if pd.isna(row['amount']) else row['amount'],
                        currency=None if pd.isna(row['currency']) else row['currency']
                )

                transactions_to_create.append(new_transaction)

            except Client.DoesNotExist:
                print(f"Error: Client with email {row['client_email']} does not exist.")
            except IntegrityError as e:
                print(f'Error: {e} for row {index}')  # Adding index for better error tracking

        if transactions_to_create:
            Transaction.objects.bulk_create(transactions_to_create)
            print(f"Successfully inserted {len(transactions_to_create)} transactions.")
            return JsonResponse({'message': f'Successfully inserted {len(transactions_to_create)} transactions.'}, status=200)
        else:
            return JsonResponse({'message': 'No transactions to insert.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def update_Clients(request):
    clients = Client.objects.all()
    print(clients)
    for client in clients:
        c_trans = Transaction.objects.filter(client_id=client.client_id)
        nb_trans = c_trans.count()
        buy_sum, sell_sum = trans_calculator(c_trans)

        client.trans_count = nb_trans
        client.buy_sum = buy_sum
        client.sell_sum = abs(sell_sum)

        client.save()
    return JsonResponse({'message': f'Successfully updated clients.'}, status=200)

def trans_calculator(transcations):
    buy_sum = Decimal('0.00')
    sell_sum = Decimal('0.00')

    for tran in transcations:
        new_amount = Decimal('0.00')
        if tran.currency == 'USD':
            new_amount = tran.amount
        elif tran.currency == 'EUR':
            new_amount = tran.amount * Decimal('1.05')
        elif tran.currency == 'GBP':
            new_amount = tran.amount * Decimal('1.26')
        elif tran.currency == 'AUD':
            new_amount = tran.amount * Decimal('0.65')
        elif tran.currency == 'CAD':
            new_amount = tran.amount * Decimal('0.71')

        new_amount = new_amount.quantize(Decimal('0.01'), rounding=ROUND_DOWN)

        if new_amount >= 0:
            buy_sum += new_amount
        else: #sell
            sell_sum += new_amount

    return buy_sum, abs(sell_sum)

def add_users():
    user = Users(name="John Doe", email="john@example.com", role="admin")
    user.set_password("123")  # Hash the password
    user.save()

    return JsonResponse({'message': f'Successfully inserted user.'}, status=200)

