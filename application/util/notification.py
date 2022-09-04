from flask_login import current_user

from application import db
from application.models import (
    SellerNotification,
    DeliveryNotification,
    CustomerNotification,
    AdminNotification,
)
from application.helpers import check_user_role

# Cretate and view notifications
class Notification:

    # Create admin notification
    def admin_notification(text, url, permit):
        content = {"text": text, "url": url}
        try:
            notification = AdminNotification(content=content, intend_user_permit=permit)
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            raise (e)

    # Create seller notification
    def seller_notification(text, url, seller_prof, permit):
        content = {"text": text, "url": url}
        try:
            notification = SellerNotification(
                content=content,
                seller_prof=seller_prof,
                intend_user_permit=permit,
                send_admin_id=current_user.id,
            )
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            raise (e)

    # Create delivery notification
    def delivery_notification(text, url, delivery_id):
        content = {"text": text, "url": url}
        try:
            notification = DeliveryNotification(
                content=content, deliverer_id=delivery_id, send_admin_id=current_user.id
            )
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            raise (e)

    # Create customer notification
    def customer_notification(self, text, url, cus_id):
        content = {"text": text, "url": url}
        try:
            notification = CustomerNotification(
                content=content, cus_id=cus_id, send_admin_id=current_user.id
            )
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            raise (e)

    # Notify user if new notification available
    @staticmethod
    def notify():
        # Get un read events
        # Check against current user permmsion
        # If permission match display alert
        notification = (
            db.session.query(AdminNotification.intend_user_permit)
            .filter_by(is_read=False, admin_id=None)
            .all()
        )
        count = 0
        for i in notification:
            is_auth = check_user_role(i.intend_user_permit)
            if is_auth:
                count += 1
        if count == 0:
            count = ""
        return count
