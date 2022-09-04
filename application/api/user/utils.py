import datetime
from flask import current_app

from application import celery
from application.helpers import save_image_helper, delete_image_helper, send_push_notification

IMAGE_PATH = current_app.config.get('UPLOAD_PATH') +'/img/cus_usr'

# Generate unique material ref key
def gen_ref_key(tbl, type):
    count = tbl.query.count()
    count += 1
    return type+str(count)+'-'+datetime.datetime.now().strftime('%y%m%d')


# Save image
def save_image(form_image):
    return save_image_helper(form_image, IMAGE_PATH)


# Delete image
def delete_image(form_image):
     delete_image_helper(form_image, IMAGE_PATH)


# Parse push notification
# Asyn func
@celery.task(name='user.send_push_notification')
def parse_push_notification(payload):
    send_push_notification(payload)
    
