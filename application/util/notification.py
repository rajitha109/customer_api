from application import db
from application.models import (
    SellerNotification,
    DeliveryNotification,
    CustomerNotification,
    AdminNotification,
)

# Cretate and view notifications
class Notification:

    # Create admin notification
    def admin_notification(text, url, permit, user_id):
        content = {"text": text, "url": url}
        try:
            notification = AdminNotification(
                content=content, intend_user_permit=permit, send_cus_id=user_id
            )
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            raise (e)

    # Create seller notification
    def seller_notification(text, url, seller_prof, permit, user_id):
        content = {"text": text, "url": url}
        try:
            notification = SellerNotification(
                content=content,
                seller_prof=seller_prof,
                intend_user_permit=permit,
                send_cus_id=user_id,
            )
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            raise (e)

    # Create delivery notification
    def delivery_notification(text, url, delivery_id, user_id):
        content = {"text": text, "url": url}
        try:
            notification = DeliveryNotification(
                content=content, deliverer_id=delivery_id, send_cus_id=user_id
            )
            db.session.add(notification)
            db.session.commit()
        except Exception as e:
            raise (e)

    # Notify user if new notification available
    def notify(user_id):
        # Get un read events
        # Check against current user permmsion
        # If permission match display alert
        notification = (
            db.session.query(CustomerNotification.id)
            .filter_by(cus_id=user_id, is_read=False)
            .all()
        )
        count = 0
        for i in notification:
            count += 1
        if count == 0:
            count = ""
        return count
