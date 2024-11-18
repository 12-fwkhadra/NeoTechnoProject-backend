import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.hashers import check_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Users, decode_token_payload, decode_token_authapi, decode_auth_token, BlacklistToken, encode_auth_token
import logging
app_logger = logging.getLogger('app_logger')

class LoginAPI(View):

    """
    Admin Login Resource
    """

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        try:
            # Get the POST data (JSON)
            post_data = json.loads(request.body)

            # Check if email and password are provided
            if not post_data or not all(k in post_data for k in ('email', 'password')):
                responseObject = {
                    'status': 'fail',
                    'message': 'Invalid data provided.',
                    'class': 'error'
                }
                return JsonResponse(responseObject, status=400)

            # Fetch user by email
            user = Users.objects.filter(email=post_data.get('email')).first()

            if user and user.role == 'admin' and check_password(post_data.get('password'), user.password):
                # Generate auth token
                auth_token = encode_auth_token(user.user_id, 'backend-portal')

                if auth_token:

                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged in.',
                        'auth_token': auth_token,
                        'role': user.role,
                        'user': user.user_id
                    }

                    app_logger.info(f"LOGIN PROCESS SUCCESSFUL: USER {user.email} of role {user.role} is authenticated and logging in successfully.")
                    return JsonResponse(responseObject, status=200)
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': 'Failed to generate authentication token.',
                        'class': 'error'
                    }
                    app_logger.error(f"LOGIN PROCESS ERROR: USER {user.email} failed to generate a valid token.")
                    return JsonResponse(responseObject, status=500)
            else:
                responseObject = {
                    'status': 'fail',
                    'message': 'Invalid email or password.',
                    'class': 'error'
                }
                app_logger.error(f"LOGIN PROCESS ERROR: Invalid credentials for USER {post_data.get('email')}")
                return JsonResponse(responseObject, status=401)

        except Exception as e:
            error_message = str(e)
            app_logger.error(f"LOGIN PROCESS ERROR: {error_message}")
            return JsonResponse({'message': error_message, 'class': 'error'}, status=500)


class AdminAPI(View):
    """
    Admin Resource
    """

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        # Get the Authorization header
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]  # Extract token after 'Bearer'
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.',
                    'class': 'error'
                }
                app_logger.error("ADMIN PORTAL AUTHENTICATION ERROR: bearer token malformed.")
                return JsonResponse(responseObject, status=401)
        else:
            auth_token = ''

        if auth_token:
            try:
                resp = decode_auth_token(auth_token)
                payl = decode_token_payload(auth_token)
                authapi = decode_token_authapi(auth_token)

                if not isinstance(resp, str) and payl == 'login':
                    if authapi == 'backend-portal':
                        # Fetch user data
                        user = Users.objects.get(id=resp)

                        responseObject = {
                            'status': 'success',
                            'data': {
                                'user_id': user.user_id,
                                'email': user.email,
                                'role': user.role
                            }
                        }
                        return JsonResponse(responseObject, status=200)
                    else:
                        responseObject = {
                            'status': 'fail',
                            'message': 'Wrong authentication portal',
                            'class': 'error'
                        }
                        app_logger.error("ADMIN PORTAL AUTHENTICATION ERROR: wrong authentication portal.")
                        return JsonResponse(responseObject, status=401)
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': resp,
                        'class': 'error'
                    }
                    app_logger.error(f"ADMIN PORTAL AUTHENTICATION ERROR: {resp}.")
                    return JsonResponse(responseObject, status=401)
            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': str(e),
                    'class': 'error'
                }
                app_logger.error(f"ADMIN PORTAL AUTHENTICATION ERROR: {str(e)}")
                return JsonResponse(responseObject, status=401)

        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.',
                'class': 'error'
            }
            app_logger.error("ADMIN PORTAL AUTHENTICATION ERROR: invalid invite token provided.")
            return JsonResponse(responseObject, status=401)


class LogoutAPI(View):
    """
    Logout Resource
    """

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        # Get the Authorization header
        auth_header = request.headers.get('Authorization')

        if auth_header:
            try:
                auth_token = auth_header.split(" ")[1]  # Extract token after 'Bearer'
            except IndexError:
                responseObject = {
                    'status': 'fail',
                    'message': 'Bearer token malformed.',
                    'class': 'error'
                }
                app_logger.error("LOGOUT ERROR: bearer token malformed.")
                return JsonResponse(responseObject, status=401)
        else:
            auth_token = ''

        if auth_token:
            try:
                # Decode the auth token (implement your decoding logic)
                resp = decode_auth_token(auth_token)
                if not isinstance(resp, str):
                    blacklist_token = BlacklistToken(token=auth_token)
                    blacklist_token.save()

                    # Check the origin of the user from the token (portal type)
                    CheckUserOrigin = decode_token_authapi(auth_token)  # Replace with actual method
                    if CheckUserOrigin == 'manager-portal':
                        app_logger.info(f"MANAGER LOGOUT SUCCESSFUL: USER {resp} logged out from the user portal successfully.")
                    else:
                        app_logger.info(f"ADMIN LOGOUT SUCCESSFUL: ADMIN {resp} logged out from the admin portal successfully.")

                    responseObject = {
                        'status': 'success',
                        'message': 'Successfully logged out.',
                        'class': 'success'
                    }
                    return JsonResponse(responseObject, status=200)
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': resp,
                        'class': 'error'
                    }
                    app_logger.error(f"LOGOUT ERROR: {resp}")
                    return JsonResponse(responseObject, status=401)

            except Exception as e:
                responseObject = {
                    'status': 'fail',
                    'message': str(e),
                    'class': 'error'
                }
                app_logger.error(f"LOGOUT ERROR: {str(e)}")
                return JsonResponse(responseObject, status=500)

        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.',
                'class': 'error'
            }
            app_logger.error("LOGOUT ERROR: invalid auth token provided.")
            return JsonResponse(responseObject, status=403)
