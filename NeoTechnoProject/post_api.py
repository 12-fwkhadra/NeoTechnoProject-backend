import json
import traceback
from datetime import datetime
from decimal import Decimal

from django.http import JsonResponse

from NeoTechnoProject.database_init import trans_calculator
from NeoTechnoProject.fetch_api import authenticate_user, app_logger
from NeoTechnoProject.models import Transaction, Client


def add_transaction(request):

    auth_response = authenticate_user(request)

    # If authentication failed, return the error response
    if isinstance(auth_response, JsonResponse):
        return auth_response  # Return the JsonResponse from the authenticate_user function

    try:
        # Parse JSON data from the request body
        data = json.loads(request.body)  # Use `request.body` to get raw data

        if data.get('amount'):
            amount = str(data.get('amount'))
            if '.' in amount:
                amount = amount[:amount.index('.') + 3]  # Keep only 2 decimal places
            else:
                amount = amount
            if data.get('transaction_type')=='Sell':
                amount = '-'+str(amount)

        transaction_date = data.get('transaction_date', None)
        if transaction_date:
            try:
                    # Attempt to parse the ISO 8601 date format (e.g., "2024-11-10T22:00:00.000Z")
                    parsed_date = datetime.strptime(transaction_date, "%Y-%m-%dT%H:%M:%S.%fZ")

                    # Extract the date part (in year-month-day format)
                    formatted_date = parsed_date.date()  # This gives you the date in YYYY-MM-DD format

                    # Convert it to string if needed
                    formatted_date_str = str(formatted_date)
            except ValueError:
                # If the date format is invalid, log the error and return a response
                app_logger.error(f"Invalid date format for transaction_date: {transaction_date}")
                return JsonResponse({
                        'message': 'Invalid date format, must be YYYY-MM-DD',
                        'class': 'error'
                })

        tran = Transaction(
            transaction_type=data.get('transaction_type', None),  # Using `get` to handle missing keys
            transaction_date=formatted_date_str,
            amount=Decimal(amount),
            currency=data.get('currency', None),
            client_id = data.get('client_id')
        )

        # Save the object to the database
        tran.save()

        c = Client.objects.filter(client_id=tran.client_id).first()
        if c:
            c.trans_count = int(c.trans_count) + 1
            buy_sum, sell_sum = trans_calculator([tran])

            c.buy_sum += buy_sum
            c.sell_sum += abs(sell_sum)

            c.save()
        else:
            # Handle the case where no client is found for the given client_id
            app_logger.error(f"Client with client_id {tran.client_id} not found.")
            return JsonResponse({
                'message': f"Client with client_id {tran.client_id} not found.",
                'class': 'error'
            })


        # Logging the successful creation of the order
        app_logger.info(f"ADDING NEW TRANSACTION SUCCESSFUL")

        # Return a JSON response with success message and order ID
        return JsonResponse({
            'message': 'Transaction added successfully',
            'class': 'success'
        })

    except Exception as e:
        # Log any error that occurs
        traceback.print_exc()
        app_logger.error(f"Error adding transaction: {str(e)}")
        return JsonResponse({
            'message': 'Error adding transaction',
            'class': 'error'
        })
