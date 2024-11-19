This is the backend source code of the Neo Technology Challenge developed using django:
To run this application:
1. install python 10 or higher
2. install the following packages:
  - asgiref==3.8.1
  - Django==5.1.3
  - django-cors-headers==4.6.0
  - djangorestframework==3.15.2
  - djangorestframework-simplejwt==5.3.1
  - et_xmlfile==2.0.0
  - Faker==33.0.0
  - numpy==2.1.3
  - openpyxl==3.1.5
  - pandas==2.2.3
  - psycopg2==2.9.10
  - psycopg2-binary==2.9.10
  - PyJWT==2.9.0
  - python-dateutil==2.9.0.post0
  - pytz==2024.2
  - six==1.16.0
  - sqlparse==0.5.2
  - typing_extensions==4.12.2
  - tzdata==2024.2
  - XlsxWriter==3.2.0
3. clone to this repository
4. migrate to postgreSQL database of the credentials stated in settings.py under DATABASE section
5. run in the terminal: python manage.py runserver

Trigger the ETL Process APIs using the following: http://localhost:8000/load-data/ and  http://localhost:8000/update-db/

The project includes the following files:
1. app.log which registers the user's events
2. data_generator.py which generates random dummy data of clients and transactions. it outputs two files: clients.csv and transactions.xslx
3. database_init.py which applies ETL processes by extracting all records from the generated csv & xslx files and loading them to the database while handling null values. This file also implements functions that handle data aggregation and transformation.
4. models.py which defines and initializes tables of the database
5. auth.py which handles login/logout authentication requests
6. fetch_api.py handles get requests
7. post_api.py handles post requests

The application demonstrates only one role for admins. 

