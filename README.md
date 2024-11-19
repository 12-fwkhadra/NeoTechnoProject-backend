This is the backend source code of the Neo Technology Challenge:
To run this application:
1. install python 10 or greater
2. install the following packages:
  asgiref==3.8.1
  Django==5.1.3
  django-cors-headers==4.6.0
  djangorestframework==3.15.2
  djangorestframework-simplejwt==5.3.1
  et_xmlfile==2.0.0
  Faker==33.0.0
  numpy==2.1.3
  openpyxl==3.1.5
  pandas==2.2.3
  psycopg2==2.9.10
  psycopg2-binary==2.9.10
  PyJWT==2.9.0
  python-dateutil==2.9.0.post0
  pytz==2024.2
  six==1.16.0
  sqlparse==0.5.2
  typing_extensions==4.12.2
  tzdata==2024.2
  XlsxWriter==3.2.0
3. clone to this repository
4. run: python manage.py runserver

In order for the project to work successfully, make sure to migrate to postgreSQL database of the credentials stated in settings.py under DATABASE section

Trigger the ETL Process APIs using the following: http://localhost:8000/load-data/ and  http://localhost:8000/update-db/

