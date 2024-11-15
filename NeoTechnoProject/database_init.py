import pandas as pd
from django.http import JsonResponse
from NeoTechnoProject.models import Client, Transaction
from django.db import IntegrityError

'''
    this class includes two functions responsible for applying ETL processes 
    the two functions respectively extract data from the Clients.csv and Transactions.xlsx and load them in the database while handling null values
    in the urls.py, specific routes are defined to trigger these APIs
'''
def load_clients_to_db(request):
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


def load_trans_to_db(request):
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

