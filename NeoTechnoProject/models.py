from datetime import datetime
import datetime
import jwt
from django.db import models
from django.conf import settings  # to access SECRET_KEY from Django settings
from django.contrib.auth.hashers import make_password, check_password


def encode_auth_token(user_id, role, remember):
    """
    Generates the Auth Token
    :param user_id: The user's ID for whom the token is generated.
    :param role: The user's role (to include in the token).
    :param remember: Determines the token's expiration time (1 = long expiration, 0 = short expiration).
    :return: JWT token (string) or exception message.
    """
    try:
        exp_time = datetime.datetime.now(datetime.timezone.utc) + (
            datetime.timedelta(days=10) if remember == 1 else datetime.timedelta(days=1)
        )

        payload = {
            'exp': exp_time,  # Expiration time
            'iat': datetime.datetime.now(datetime.timezone.utc),  # Issued At
            'sub': user_id,  # Subject (user_id)
            'role': role,  # User role
            'purp': 'login',  # Purpose (login)
        }

        # Encode the token using the secret key
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    except Exception as e:
        return str(e)


def decode_auth_token(auth_token):
    """
    Decodes the Auth Token to validate and retrieve user information.
    :param auth_token: JWT token to be decoded.
    :return: Decoded payload (if valid), or exception message (if invalid).
    """
    try:
        payload = jwt.decode(auth_token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload  # Decoded token payload with user_id, role, etc.

    except jwt.ExpiredSignatureError:
        return "Signature has expired. Please log in again."
    except jwt.InvalidTokenError:
        return "Invalid token. Please check your token."


class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  # Ensures unique email addresses
    password = models.CharField(max_length=255)  # Store hashed password
    role = models.CharField(max_length=50)  # Role (e.g., admin, user, etc.)

    def set_password(self, raw_password):
        """
        Hash and set the password for the user.
        :param raw_password: The plain password.
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Check if the provided password matches the stored hash.
        :param raw_password: The plain password to check.
        :return: True if passwords match, else False.
        """
        return check_password(raw_password, self.password)

    def generate_auth_token(self, remember=False):
        """
        Generates an authentication token for the user.
        :param remember: If True, token expiration is extended to 10 days; otherwise, 1 day.
        :return: JWT token (string)
        """
        return encode_auth_token(self.user_id, self.role, remember)

    def __str__(self):
        return self.name


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

