import os 
from dotenv import load_dotenv
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SECRET_KEY = os.getenv('secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('db_uri')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False # Prdiction = True 

    # Platform technical
    BCRYPT_LOG_ROUNDS = 4
    TOKEN_EXPIRE_HOURS = 3
    TOKEN_EXPIRE_MINUTES = 0
    DISPLAY_LIST_LENGTH = 2 # Length of items displace at onece

    # Statci files
    UPLOAD_PATH = os.getenv('upload_path')
    DOWNLOAD_PATH = os.getenv('download_path')

    # Celery
    CELERY_BROKER_URL = os.getenv('celery_broker')
    CELERY_RESULT_BACKEND = os.getenv('celery_backend')

    # One signal
    ONESIGNAL_APP_ID =  os.getenv('onesignal_id')
    ONESIGNAL_API_ENDPOINT = os.getenv('onesignal_endpoint')
    ONESIGNAL_REST_API_KEY = os.getenv('onesignal_key')

    # Marketing
    MAX_DISTANCE = 5
    
    # System values
    GROCERY_TAXONOMY = {
        "category": "category",
        "brand": "brand",
        "size": "size",
        "unit": "unit",
    }
    FOOD_TAXONOMY = {
        "category": "category",
        "addon": "addon",
        "size": "size",
        "commission": "commission",
        "size-price": "size-price",
    }
    
    PAYMENT_METHODS = {"Cash":"s", "Card":"c", "COD":"o", "Credit":"r"}