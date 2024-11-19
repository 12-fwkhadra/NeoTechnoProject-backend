from datetime import datetime
from decimal import Decimal, ROUND_DOWN

from dateutil.parser import parser
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
import xlsxwriter
import logging

from django.utils.dateformat import DateFormat

from NeoTechnoProject.database_init import trans_calculator
from NeoTechnoProject.models import Client, Users, Transaction, decode_auth_token

app_logger = logging.getLogger('app_logger')

def authenticate_user(request):
    token = request.headers.get('Authorization')

    if not token:
        return JsonResponse({"message": "Unauthorized. Token is missing."}, status=401)

    try:
        # Extract the token without the "Bearer " part
        auth_token = token.split(" ")[1]

        # Decode and validate the token (this should be handled by JWTAuthentication already)
        decoded_token = decode_auth_token(auth_token)
        print("Decoded Token: ", decoded_token)

        # Retrieve user from token data (you can customize this part if needed)
        user_id = decoded_token.get('sub')
        user = Users.objects.filter(user_id=user_id).first()

        if not user:
            return JsonResponse({"message": "User not found."}, status=404)

        # Now check if the user origin is valid (you can customize this based on your logic)
        if decoded_token.get('authapi') != 'backend-portal':
            app_logger.error(f"Unauthorized access by user {user.user_id}. User origin is not valid.")
            return JsonResponse({"message": "Unauthorized access. Invalid user origin."}, status=403)

    except Exception as e:
        app_logger.error(f"Error decoding token: {str(e)}")
        return JsonResponse({"message": "Invalid or expired token."}, status=401)
def get_Clients(request):

        auth_response = authenticate_user(request)

        # If authentication failed, return the error response
        if isinstance(auth_response, JsonResponse):
            return auth_response  # Return the JsonResponse from the authenticate_user function

        filter = request.GET.get('search_query', None)
        date = request.GET.get('date', None)
        country = request.GET.get('country', None)
        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 100)

        clients = Client.objects.all()

        if filter:
            clients = clients.filter(
                Q(name__icontains=filter) | Q(email__icontains=filter) | Q(client_id__icontains=filter)
            )
        if date:
            clients = clients.filter(birthdate=date)
        if country:
            clients = clients.filter(country=country)

        clients = clients.order_by('client_id')
        paginator = Paginator(clients, per_page)
        page_obj = paginator.get_page(page)
        clients_data = []
        for client in page_obj:

            client_data = {
                'id': client.client_id,
                'name': client.name,
                'birthdate': client.birthdate,
                'country': client.country,
                'email': client.email,
                'balance': client.account_balance,
                'nb_trans': client.trans_count,
                'buy_sum': client.buy_sum,
                'sell_sum': client.sell_sum
            }
            clients_data.append(client_data)

        return JsonResponse({'clients': clients_data, 'total_pages': paginator.num_pages, 'total': paginator.count, 'per_page': per_page, 'page': page})

def get_trans_per_clients(request, cid):
        auth_response = authenticate_user(request)

        # If authentication failed, return the error response
        if isinstance(auth_response, JsonResponse):
            return auth_response  # Return the JsonResponse from the authenticate_user function

        date_range = request.GET.get('dateRange', None)
        trans_per_clients = Transaction.objects.filter(client_id=cid).order_by('transaction_id')

        if date_range != 'null':
            date_range = date_range.replace('{','').replace('}','')
            start_date, end_date = date_range.split(',')

            start_date = datetime.strptime(start_date, '%d/%m/%Y').date()  # Directly get date object
            end_date = datetime.strptime(end_date, '%d/%m/%Y').date()

            start_date = start_date.strftime('%Y-%m-%d')

            end_date = end_date.strftime('%Y-%m-%d')

            trans_per_clients = trans_per_clients.filter(transaction_date__gte=start_date, transaction_date__lte=end_date).order_by('transaction_id')

        page = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 100)
        paginator = Paginator(trans_per_clients, per_page)
        page_obj = paginator.get_page(page)
        trans_data = []
        for t in page_obj:
            rate, amount = exchange_rates(t.currency, t.amount)
            t_data = {
                'id': t.transaction_id,
                'type': t.transaction_type,
                'date': t.transaction_date,
                'amount': t.amount,
                'currency': t.currency,
                'rate': rate,
                'in_usd': amount.quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            }
            trans_data.append(t_data)

        return JsonResponse({'trans': trans_data, 'total_pages': paginator.num_pages, 'total': paginator.count, 'per_page': per_page, 'page': page})

def exchange_rates(currency, amount):
    if currency == 'USD':
       return 1, amount
    elif currency == 'EUR':
        return 1.05, amount * Decimal('1.05')
    elif currency == 'GBP':
        return 1.26, amount * Decimal('1.26')
    elif currency == 'AUD':
        return 0.65, amount * Decimal('0.65')
    elif currency == 'CAD':
        return 0.71, amount * Decimal('0.71')

def get_countries(request):
    auth_response = authenticate_user(request)

    # If authentication failed, return the error response
    if isinstance(auth_response, JsonResponse):
        return auth_response  # Return the JsonResponse from the authenticate_user function

    countries = Client.objects.all().values('country').distinct()
    return JsonResponse({'countries': list(countries)})

def get_currencies(request):
    auth_response = authenticate_user(request)

    # If authentication failed, return the error response
    if isinstance(auth_response, JsonResponse):
        return auth_response  # Return the JsonResponse from the authenticate_user function

    currency = Transaction.objects.all().values('currency').distinct()
    return JsonResponse({'currency': list(currency)})

def export_Clients(request):
    auth_response = authenticate_user(request)

    if isinstance(auth_response, JsonResponse):
        return auth_response

    filter = request.GET.get('search_query', None)
    date = request.GET.get('date', None)
    country = request.GET.get('country', None)
    clients = Client.objects.all()

    if filter:
        clients = clients.filter(
            Q(name__icontains=filter) | Q(email__icontains=filter) | Q(client_id__icontains=filter)
        )
    if date:
        clients = clients.filter(birthdate=date)
    if country:
        clients = clients.filter(country=country)

    clients = clients.order_by('client_id')

    csv_filename = 'Clients.csv'

    try:
        write_to_excel(clients, csv_filename)

        # Return the Excel file as a downloadable response
        with open(csv_filename, 'rb') as excel_file:
            response = HttpResponse(excel_file.read(),
                                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = f'attachment; filename={csv_filename}'
            return response

    except Client.DoesNotExist:
        app_logger.error(f"EXPORTING ALL Clients ERROR: No clients found.")
        return JsonResponse({"message": "Orders not found", 'class': 'error'}, status=404)

    except Exception as e:
        app_logger.error(f"Exporting ALL Clients ERROR: {e}")
        return JsonResponse({"message": "An error occured", 'class': 'error'}, status=500)

def write_to_excel(clients, excel_filename):

        workbook = xlsxwriter.Workbook(excel_filename)
        worksheet = workbook.add_worksheet()

        fieldnames = ['client id', 'name', 'email', 'birthdte', 'country', 'current balance', 'total transactions', 'total buys', 'total sells']

        # Write the headers
        for col_num, header in enumerate(fieldnames):
            worksheet.write(0, col_num, header)

        for row_num, client in enumerate(clients, 1):
            worksheet.write(row_num, 0, client.client_id)
            worksheet.write(row_num, 1, client.name if client.name else '')
            worksheet.write(row_num, 2, client.email if client.email else '')
            worksheet.write(row_num, 3, DateFormat(client.birthdate).format('Y-m-d') if client.birthdate else '')
            worksheet.write(row_num, 4, client.country if client.country else '')
            worksheet.write(row_num, 5, client.account_balance if client.account_balance else '0')
            worksheet.write(row_num, 6, client.trans_count if client.trans_count else '0')
            worksheet.write(row_num, 7, client.buy_sum if client.buy_sum else '0')
            worksheet.write(row_num, 8, client.sell_sum if client.sell_sum else '0')

        workbook.close()

def delete_transaction(request, tid):

    if tid:
        try:
            # Get the record to delete
            transaction = Transaction.objects.get(transaction_id=tid)
            c = Client.objects.filter(client_id=transaction.client_id).first()

            if c:
                c.trans_count = int(c.trans_count) -1
                buy_sum, sell_sum = trans_calculator([transaction])

                c.buy_sum -= buy_sum
                c.sell_sum -= abs(sell_sum)

                c.save()
            else:
                # Handle the case where no client is found for the given client_id
                app_logger.error(f"Client with client_id {transaction.client_id} not found when deleting transaction.")
                return JsonResponse({
                    'message': f"Failed to delete transaction of no client",
                    'class': 'error'
                })
            # Delete the record
            transaction.delete()
            app_logger.info(f"Transaction {tid} for client {c.client_id} deleted.")
            return JsonResponse({'class': 'success', "message": "Transaction deleted successfully"})

        except Transaction.DoesNotExist:
            return JsonResponse({"class": "error", "message": "Transaction not found"})
    else:
        return JsonResponse({"class": "error", "message": "No Transaction ID provided"})
