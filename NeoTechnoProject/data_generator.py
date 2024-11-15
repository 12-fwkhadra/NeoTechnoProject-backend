import pandas as pd
import random
from faker import Faker

fake = Faker()

'''
    this function generates random data of clients using python faker library
    takes the number of clients to be generated as an input
    returns dataframe of the generated clients
'''
def generate_clients(num_clients):
    countries = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Italy', 'Spain', 'Australia', 'Lebanon', 'UAE', 'Mexico', 'Kuwait', 'Jordan', 'Norway']
    clients_data = []

    for client_id in range(1, num_clients + 1):
        name = fake.name()
        email = fake.email()
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=70).strftime("%Y-%m-%d")
        country = random.choice(countries)
        account_balance = round(random.uniform(100.0, 5000.0), 2)

        clients_data.append([client_id, name, email, date_of_birth, country, account_balance])

    clients_df = pd.DataFrame(clients_data, columns=['client_id', 'name', 'email', 'date_of_birth', 'country', 'account_balance'])
    return clients_df

'''
    this function generates random transaction records using python faker library
    takes the number of transactions to generate and the number of clients to map to the transaction records
    returns dataframe of the generated transaction records
'''
def generate_transactions(num_transactions, num_clients):
    transaction_types = ['buy', 'sell']
    currencies = ['USD', 'EUR', 'GBP', 'AUD', 'CAD']
    transactions_data = []

    for transaction_id in range(1, num_transactions + 1):
        client_id = random.randint(1, num_clients)
        transaction_type = random.choice(transaction_types)
        transaction_date = fake.date_this_year().strftime("%Y-%m-%d")
        amount = round(random.uniform(50.0, 1500.0), 2) if transaction_type == 'buy' else round(
            random.uniform(-1500.0, -50.0), 2)
        currency = random.choice(currencies)

        transactions_data.append([transaction_id, client_id, transaction_type, transaction_date, amount, currency])

    transactions_df = pd.DataFrame(transactions_data, columns=['transaction_id', 'client_id', 'transaction_type', 'transaction_date', 'amount', 'currency'])
    return transactions_df


clients_df = generate_clients(500)
transactions_df = generate_transactions(1500, 500)

#saving the generated dataframes in csv and xlsx respectively
clients_df.to_csv('clients.csv', index=False)
transactions_df.to_excel('transactions.xlsx', index=False)

print("Data generation completed.")