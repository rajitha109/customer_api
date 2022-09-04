from flask_restx import Model
from flask_restx.inputs import email
from flask_restx.fields import String, Boolean, Integer, Float
from flask_restx.reqparse import RequestParser
from werkzeug.datastructures import FileStorage

# 
# ---------------------------------------------Models-----------------------------------------------------------------------------
# 

user_model = Model(
    'CustomerUseter',
    {
        'contact_no': String,
        "public_id": String,
        "is_confirm": Boolean,
        "is_logged_in": Boolean,
        "is_inactive": Boolean,
        "token_expires_in": String,
    }
)

location_model = Model(
    'CustomerLocation',
    {
        'id':Integer,
        'label':String,
        'place_no': String,
        'street_name':String,
        'location_text':String,
        'longitude':Float,
        'latitude':Float
    }
)

prof_model = Model(
    'CustomerProfile',
    {
        'id':Integer,
        'first_name':String,
        'last_name':String,
        'email': String
    }
)

#
# ---------------------------------------Request parsers--------------------------------------------------------------------------
# 

# Use on register
reg_parser = RequestParser(bundle_errors=True)
reg_parser.add_argument('contact_no', type=str, location="json", required=True, nullable=False, help="Contact No in international format.")
reg_parser.add_argument('player_id', type=str, location="json", required=True, nullable=False, help="One signal player id")

# Use on login
# Will inherit contract no from reg_parser
login_parser = reg_parser.copy()
login_parser.add_argument('conf_code', type=str, location="json", required=True, nullable=False, help="4 digit confimation code")
login_parser.add_argument('counter', type=str, location="json", required=True, nullable=False, help="Hashed code")
login_parser.remove_argument('player_id')

# Use on location
location_parser = RequestParser(bundle_errors=True)
location_parser.add_argument('label', type=str, location="json", required=True, nullable=False, help="Location lable as string")
location_parser.add_argument('place_no', type=str, location="json", nullable=True, help="Location palce no as string")
location_parser.add_argument('street_name', type=str, location="json", nullable=True, help="Location street name as string")
location_parser.add_argument('location_text', type=str, location="json", required=True, nullable=False, help="Location text extract from map")
location_parser.add_argument('longitude', type=str, location="json", required=True, nullable=False, help="Location longitude in float")
location_parser.add_argument('latitude', type=str, location="json", required=True, nullable=False, help="Location latitude in float")

# User on profile
prof_parser = RequestParser(bundle_errors=True)
prof_parser.add_argument('first_name', type=str, location="form", required=True, nullable=False, help="First name, min=3, max=50")
prof_parser.add_argument('last_name', type=str, location="form", required=True, nullable=False, help="Last name, min=3, max=50")
prof_parser.add_argument('email', type=email(), location="form", required=True, nullable=False, help="max=120")
prof_parser.add_argument('image', type=FileStorage, location='files', help="File allowed PNG, JPG, JPEG")