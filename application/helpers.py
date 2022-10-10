import os
import secrets
import requests
from functools import wraps
from PIL import Image
from flask import request, current_app
from werkzeug.exceptions import Unauthorized


from .models import CustomerUser

_REALM_CUSTOMERS = "000000000"


def token_required(f):
    """Execute function if request contains valid access token."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token_payload = _check_access_token()
        for name, val in token_payload.items():
            setattr(decorated, name, val)
        return f(*args, **kwargs)

    return decorated


def _check_access_token():
    token = request.headers.get("Authorization")
    if not token:
        raise ApiUnauthorized(description="Unauthorized")
    result = CustomerUser.decode_access_token(token)
    if result.failure:
        raise ApiUnauthorized(
            description=result.error,
            error="invalid_token",
            error_description=result.error,
        )
    return result.value


# Authorize tocken
class ApiUnauthorized(Unauthorized):
    """Raise status code 401 with customizable WWW-Authenticate header."""

    def __init__(
        self,
        description="Unauthorized",
        error=None,
        error_description=None,
    ):
        self.description = description
        self.www_auth_value = self.__get_www_auth_value(error, error_description)
        Unauthorized.__init__(
            self, description=description, response=None, www_authenticate=None
        )

    def get_headers(self, environ, param):
        return [
            ("Content-Type", "text/html"),
            ("WWW-Authenticate", self.www_auth_value),
        ]

    def __get_www_auth_value(self, error, error_description):
        realm = _REALM_CUSTOMERS
        www_auth_value = f'Bearer realm="{realm}"'
        if error:
            www_auth_value += f', error="{error}"'
        if error_description:
            www_auth_value += f', error_description="{error_description}"'
        return www_auth_value


# Save image
def save_image_helper(form_image, path):
    try:
        random_hex = secrets.token_hex(16)
        _, f_ext = os.path.splitext(form_image.filename)  # _ Means unusing variables
        image_fn = random_hex + f_ext
        image_path = os.path.join(current_app.root_path, path, image_fn)

        size = 300, 300
        i = Image.open(form_image)
        i.thumbnail(size, Image.ANTIALIAS)
        i.save(image_path)

        return image_fn
    except Exception as e:
        raise (e)


# Delete image
def delete_image_helper(form_image, path):
    try:
        os.remove(os.path.join(current_app.root_path, path, form_image))
    except Exception as e:
        raise (e)


# Send push notification
def send_push_notification(payload):
    try:
        headers = {
            "Accept": "application/json",
            "Authorization": "Basic "
            + current_app.config.get("ONESIGNAL_REST_API_KEY"),
            "Content-Type": "application/json",
        }
        requests.post(
            current_app.config.get("ONESIGNAL_API_ENDPOINT"),
            json=payload,
            headers=headers,
        )
        contact=str(payload["contact_no"])
        text=str(payload["contents"]["en"])
        print(contact,text)
        url="https://www.textit.biz/sendmsg?id=94713181959&pw=6164&to="+contact+"&text="+text+""
        print(url)
        #requests.post(url)


        print("Hello2")
    except Exception as e:
        raise (e)
