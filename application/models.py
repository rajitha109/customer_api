from datetime import datetime, timedelta, timezone
from uuid import uuid4
from flask import current_app
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.ext.hybrid import hybrid_method
from sqlalchemy import func
import jwt

from application import db
from application.util.result import Result
from application.util.datetime_util import utc_now, dtaware_fromtimestamp
from application.util.calc import gc_distance, rate_cal


# Map Admin permission with admin user
AdminPermissionMap = db.Table(
    'admin_permission_map', db.Model.metadata,
    db.Column('admin_id', db.Integer, db.ForeignKey('admin_user.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('admin_permission.id'))
) 


# Admin user permision
class AdminPermission(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(80), nullable=False, unique=True)


# Admin user
class AdminUser(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_confirm = db.Column(db.Boolean, nullable=False, default=False)
    is_super = db.Column(db.Boolean, nullable=False, default=False)
    is_inactive = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # on the `AdminUser` model to use permission-based authorization.
    permissions = db.relationship('AdminPermission', secondary=AdminPermissionMap, backref=db.backref('adminuser', lazy='dynamic'))
    # AdminProfile one to one
    profile = db.relationship('AdminProfile', uselist=False, backref='adminuser', lazy=True)
    # SellerPaymentWithdrawal one to many
    seller_withdrawal = db.relationship('SellerPaymentWithdrawal', backref='adminuser', lazy=True)
    # SellerPaymentFine one many 
    seller_fine = db.relationship('SellerPaymentFine', backref='adminuser', lazy=True)
    # DeliveryPaymentWithdrawal one to many
    delivery_withdrawal = db.relationship('DeliveryPaymentWithdrawal', backref='adminuser', lazy=True)
    # SellerTicket one to many
    seller_ticket = db.relationship('SellerTicket', backref='adminuser', lazy=True)
    # DeliveryTicket one to many
    delivery_ticket = db.relationship('DeliveryTicket', backref='adminuser', lazy=True)
    # CustomerTicket one to many
    cus_ticket = db.relationship('CustomerTicket', backref='adminuser', lazy=True)
    # Promo one to many
    promo = db.relationship('Promo', backref='adminuser', lazy=True)
    # Ad one to many
    ad = db.relationship('Ad', backref='adminuser', lazy=True)
    # GroceryProductSuggest one to many
    groccery_suggest = db.relationship('GroceryProductSuggest', backref='adminuser',  lazy=True)
    # AdminNotification one to many
    notification = db.relationship('AdminNotification', backref='adminuser',  lazy=True)
    # SellerNotification one to many
    seller_notification = db.relationship('SellerNotification', backref='adminuser',  lazy=True)
    # DeliveryNotification one to many
    delivery_notification = db.relationship('DeliveryNotification', backref='adminuser',  lazy=True)
    # CustomerNotification one to many
    cus_notification = db.relationship('CustomerNotification', backref='adminuser',  lazy=True)
    # Cupon one to many
    cupon = db.relationship('Cupon', backref='adminuser',  lazy=True)

    def __repr__(self):
        return f"AdminUser('{self.id}')"


# Profile of admin user
class AdminProfile(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nic = db.Column(db.String(12), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name =  db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(150), nullable=False)   
    contact_no = db.Column(db.String(15),  unique=True, nullable=False)
    job = db.Column(db.String(20), nullable=False)
    image = db.Column(db.String(50), nullable=False, default='default_avatar.png')
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False, unique=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"AdminProfile('{self.first_name}')"


# Map seller permission with seller user
SellerPermissionMap = db.Table(
    'seller_permission_map', db.Model.metadata,
    db.Column('seller_id', db.Integer, db.ForeignKey('seller_user.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('seller_permission.id'))
) 


# Admin user permision
class SellerPermission(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(80), nullable=False, unique=True)


# Seller user
class SellerUser(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_confirm = db.Column(db.Boolean, nullable=False, default=False)
    confirm_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    is_employee = db.Column(db.Boolean, nullable=False, default=False)
    is_logged_in = db.Column(db.Boolean, nullable=False, default=False)
    is_inactive = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # on the `SelerUser` model to use permission-based authorization.
    permissions = db.relationship('SellerPermission', secondary=SellerPermissionMap, backref=db.backref('selleruser', lazy='dynamic'))
    # SellerProfile one to one
    profile = db.relationship('SellerProfile', uselist=False, backref='selleruser', lazy=True)
    # SellerEmployee one to one
    emp = db.relationship('SellerEmployee', uselist=False, backref='selleruser', lazy=True)
    # SellerPayment one to one
    pay = db.relationship('SellerPayment', uselist=False, backref='selleruser', lazy=True)
    # SellerNotification ont to many
    notificatin = db.relationship('SellerNotification', backref='selleruser',  lazy=True)

    def __repr__(self):
        return f"SellerUser('{self.id}')"


# Seller profile
# Directyl connected to seller
class SellerProfile(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(1), nullable=False) # g = Grocery f = Food
    first_name = db.Column(db.String(50), nullable=False)
    last_name =  db.Column(db.String(50), nullable=False)
    organization = db.Column(db.String(50), nullable=False)
    street_address = db.Column(db.String(120), nullable=False)
    city_address = db.Column(db.String(30), nullable=False)
    postcode = db.Column(db.Integer, nullable=False)
    contact_no = db.Column(db.String(15),  unique=True, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(50), nullable=False, default='default_avatar.png')
    seller_id = db.Column(db.Integer, db.ForeignKey('seller_user.id'), nullable=False, unique=True)
    is_inactive = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # SellerGroceryCategory one to one
    grocery_cat =  db.relationship('SellerGroceryCategory', uselist=False, backref='sellerprofile',  lazy=True)
    # Food one to many
    food = db.relationship('Food', backref='sellerprofile',  lazy=True)
    # FoodTaxonomy one to many
    food_tax = db.relationship('FoodTaxonomy', backref='sellerprofile',  lazy=True)
    # SellerEmployee one to one
    emp = db.relationship('SellerEmployee', backref='sellerprofile',  lazy=True)
    # SellerBusinessHours one to one
    hours =  db.relationship('SellerBusinessHours', uselist=False, backref='sellerprofile',  lazy=True)
    # SellerBusinessSpecialDa one to many
    spec_date = db.relationship('SellerBusinessSpecialDate', backref='sellerprofile',  lazy=True)
    # SellerBank one to one
    bank = db.relationship('SellerBank', uselist=False, backref='sellerprofile',  lazy=True)
    # SellerPricePlan one to many
    price_plan = db.relationship('SellerPricePlan', backref='sellerprofile',  lazy=True)
    # GroceryProductStock one to many
    stock = db.relationship('GroceryProductStock', backref='sellerprofile',  lazy=True)
    # Order one to many
    order = db.relationship('Order', backref='sellerprofile',  lazy=True)
    # SellerTicket one to many
    ticket = db.relationship('SellerTicket', backref='sellerprofile',  lazy=True)
    # CustomerSellerFeedback one to many
    feedback_customer_seller = db.relationship('CustomerSellerFeedback', backref='sellerprofile',  lazy=True)
    # SellerCustomerFeedback one to many
    feedback_seller_customer =  db.relationship('SellerCustomerFeedback', backref='sellerprofile', lazy=True)
    # SellerDeliveryFeedback one to many
    feedback_seller_delivery =  db.relationship('SellerDeliveryFeedback', backref='sellerprofile', lazy=True)
    # DeliverySellerFeedback one to many
    feedback_delivery_seller =  db.relationship('DeliverySellerFeedback', backref='sellerprofile', lazy=True)
    # SellerPromo one to many
    promo = db.relationship('SellerPromo', backref='sellerprofile', lazy=True)
    # GroceryProductSuggest one to many
    groccery_suggest = db.relationship('GroceryProductSuggest', backref='sellerprofile',  lazy=True)
    # SellerNotification one to many
    notification = db.relationship('SellerNotification', backref='sellerprofile',  lazy=True)
    # AdminNotification one to many
    admin_notification = db.relationship('AdminNotification', backref='sellerprofile',  lazy=True)
    # DeliveryNotification one to many
    delivery_notification = db.relationship('DeliveryNotification', backref='sellerprofile',  lazy=True)
    # CustomerNotification one to many
    cus_notification = db.relationship('CustomerNotification', backref='sellerprofile',  lazy=True)

    @hybrid_method
    def distance(self, longitude, latitude):
        return gc_distance(longitude, latitude, self.longitude, self.latitude)

    @distance.expression
    def distance(cls, longitude, latitude):
        return gc_distance(longitude, latitude, cls.longitude, cls.latitude, math=func)

    def __repr__(self):
        return f"SellerProfile('{self.ref_no}')"



# Seller selected main grocery catetogry
class SellerGroceryCategory(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('grocery_product_term.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    __table_args__ = (db.UniqueConstraint(seller_prof, cat_id),) # Composite unique key

    def __repr__(self):
        return f"SellerGroceryCategory('{self.id}')"


# Seller Business Hours
class SellerBusinessHours(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(JSON)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"SellerBusinessHours('{self.content}')"


#  Seller special dates for business
class SellerBusinessSpecialDate(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    content = db.Column(JSON)
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"SellerBusinessSpecialDate'{self.date}')"


#  Seller bank details
class SellerBank(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(20), nullable=False)
    branch = db.Column(db.String(30), nullable=False)
    acc_no = db.Column(db.String(12), nullable=False)
    acc_holder = db.Column(db.String(75), nullable=False)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"SellerBank'{self.date}')"


# Seller specific price plan
class SellerPricePlan(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"SellerBank'{self.date}')"


#  Seller employee profile
#  Only employee seller accounts
class SellerEmployee(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    nic = db.Column(db.String(12), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name =  db.Column(db.String(50), nullable=False)
    job = db.Column(db.String(20), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller_user.id'), nullable=False, unique=True)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"SellerEmployee('{self.id}')"


# Seller payment
class SellerPayment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    earn = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Total earning
    arrears = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Arrears from earning
    fine = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    seller_id = db.Column(db.Integer, db.ForeignKey('seller_user.id'), nullable=False, unique=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # SellerPaymentWithdrawal one to many
    withdrawal = db.relationship('SellerPaymentWithdrawal', backref='sellerpayment', lazy=True)
    # SellerPaymentArrears one to many
    pay_arrears = db.relationship('SellerPaymentArrears', backref='sellerpayment', lazy=True)
    # SellerPaymentFine one to many
    pay_fine = db.relationship('SellerPaymentFine', backref='sellerpayment', lazy=True)

    def __repr__(self):
        return f"SellerPayment('{self.id}')"


# Withdrawals and withdrawal request of seller
class SellerPaymentWithdrawal(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    amount = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    note = db.Column(db.String(255), nullable=True)
    is_request = db.Column(db.Boolean, nullable=False, default=False) # Seller action
    is_transfer = db.Column(db.Boolean, nullable=False, default=False) # AAdmin
    is_receive = db.Column(db.Boolean, nullable=False, default=False) # Seller / Automatic
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    is_cancel = db.Column(db.Boolean, nullable=False, default=False)
    pay_id = db.Column(db.Integer, db.ForeignKey('seller_payment.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # SellerPaymentArrears one to manay
    arrears = db.relationship('SellerPaymentArrears', backref='sellerpaymentwithdrawal', lazy=True)

    def __repr__(self):
        return f"SellerPaymentWithdrawal('{self.ref_no}')"


# Arrears for seller
class SellerPaymentArrears(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    note = db.Column(db.String(255), nullable=True)
    is_receive = db.Column(db.Boolean, nullable=False, default=False) # Seller action
    is_deduct = db.Column(db.Boolean, nullable=False, default=False) # Admin action
    pay_id = db.Column(db.Integer, db.ForeignKey('seller_payment.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    withdrawl_id = db.Column(db.Integer, db.ForeignKey('seller_payment_withdrawal.id'), nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f" SellerPaymentArrears('{self.id}')"


# Fines of seller
class SellerPaymentFine(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    amount = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    note = db.Column(db.String(255), nullable=True)
    pay_id = db.Column(db.Integer, db.ForeignKey('seller_payment.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f" SellerPaymentFine('{self.id}')"


#  Seller Blacklist tockents
class SellerBlacklistToken(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, default=utc_now)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<SellerBlacklistToken token={self.token}>"


# Delivery Charges
class DeliveryPricePlan(db.Model):

    id = db.Column(db.Integer, primary_key=True)  
    type = db.Column(db.String(8), nullable=False)
    base_rate = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    cost_per_km = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # DeliveryProfile one to many
    profile = db.relationship('DeliveryProfile', backref='deliverypriceplan', lazy=True)

    def __repr__(self):
        return f"DeliveryCharges('{self.id}')"


# Delivery User
class DeliveryUser(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid4()))
    contact_no = db.Column(db.String(15),  unique=True, nullable=False) 
    is_confirm = db.Column(db.Boolean, nullable=False, default=False)
    confirm_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    is_logged_in = db.Column(db.Boolean, nullable=False, default=False)
    is_inactive = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # DeliveryProfile one to one
    profile = db.relationship('DeliveryProfile', uselist=False, backref='deliveryuser', lazy=True)
    # DeliveryVehicle one to one 
    vehicle = db.relationship('DeliveryVehicle', uselist=False, backref='deliveryuser', lazy=True)
    # DeliveryBank one to one
    bank = db.relationship('DeliveryBank', uselist=False, backref='deliveryuser', lazy=True)
    # OrderMobile one to many
    order_mobile = db.relationship('OrderMobile', backref='deliveryuser', lazy=True)
    # OrderReturn one to many
    order_return = db.relationship('OrderReturn', backref='deliveryuser', lazy=True)
    # DeliveryPayment one to one 
    pay = db.relationship('DeliveryPayment', uselist=False, backref='deliveryuser', lazy=True)
    # DeliveryTicket one to many
    ticket = db.relationship('DeliveryTicket', backref='deliveryuser', lazy=True)
    # CustomerDeliveryFeedback one to many
    feedback_customer_delivery =  db.relationship('CustomerDeliveryFeedback', backref='deliveryuser', lazy=True)
    # SellerDeliveryFeedback one to many
    feedback_seller_delivery =  db.relationship('SellerDeliveryFeedback', backref='deliveryuser', lazy=True)
    # DeliveryCustomerFeedback one to many
    feedback_delivery_customer =  db.relationship('DeliveryCustomerFeedback', backref='deliveryuser', lazy=True)
    # DeliverySellerFeedback one to many
    feedback_delivery_seller =  db.relationship('DeliverySellerFeedback', backref='deliveryuser', lazy=True)
    # DeliveryNotification
    notification = db.relationship('DeliveryNotification', backref='deliveryuser', lazy=True)
    # AdminNotification one to many
    admin_notification = db.relationship('AdminNotification', backref='deliveryuser', lazy=True)
    # SellerNotification onr to many
    seller_notification = db.relationship('SellerNotification', backref='deliveryuser', lazy=True)
    # CustomerNotification one to many
    cus_notification = db.relationship('CustomerNotification', backref='deliveryuser', lazy=True)

    def __repr__(self):
        return f"DeliveryUser('{self.id}')"


# Deliverer profile
class DeliveryProfile(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    nic = db.Column(db.String(12), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name =  db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    street_address = db.Column(db.String(120), nullable=False)
    city_address = db.Column(db.String(30), nullable=False)
    postcode = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(50), nullable=False, default='default_avatar.png')
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=False, unique = True)
    price_plan = db.Column(db.Integer, db.ForeignKey('delivery_price_plan.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"DeliveryProfile('{self.ref_no}')"


# Deliverer vehicle
class DeliveryVehicle(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(8), nullable=False)
    reg_no = db.Column(db.String(10), unique=True, nullable=False)
    note = db.Column(db.String(100), nullable=True)
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"DeliveryVehicle('{self.reg_no}')"


# Deliverer specific bank
class DeliveryBank(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(20), nullable=False)
    branch = db.Column(db.String(30), nullable=False)
    acc_no = db.Column(db.String(12), nullable=False)
    acc_holder = db.Column(db.String(75), nullable=False)
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"DeliveryBank'{self.id}')"


# Delivery payment
class DeliveryPayment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    earn = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Total earning
    arrears = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Arrears from earning
    cash_in_hand = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Collection of COD
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # DeliveryPaymentWithdrawal one to many 
    withdrawal = db.relationship('DeliveryPaymentWithdrawal', backref='deliverypayment', lazy=True)
    # DeliveryPaymentArrears one to many
    pay_arrears = db.relationship('DeliveryPaymentArrears', backref='deliverypayment', lazy=True)
    # DeliveryPaymentCashInHand one to many
    pay_cahs_in_hand = db.relationship('DeliveryPaymentCashInHand', backref='deliverypayment', lazy=True)
    # DeliveryPaymentDeposit one to many
    deposit = db.relationship('DeliveryPaymentDeposit', backref='deliverypayment', lazy=True)

    def __repr__(self):
        return f"DeliveryPayment('{self.id}')" 


# Withdrawals and withdrawal request of deliverer
class DeliveryPaymentWithdrawal(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    amount = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    note = db.Column(db.String(255), nullable=True)
    is_request = db.Column(db.Boolean, nullable=False, default=False) # Seller action
    is_transfer = db.Column(db.Boolean, nullable=False, default=False) # AAdmin
    is_receive = db.Column(db.Boolean, nullable=False, default=False) # Seller / Automatic
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    is_cancel = db.Column(db.Boolean, nullable=False, default=False)
    pay_id = db.Column(db.Integer, db.ForeignKey('delivery_payment.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # DeliveryPaymentArrears one to manay
    arrears = db.relationship('DeliveryPaymentArrears', backref='deliverypaymentwithdrawal', lazy=True)

    def __repr__(self):
        return f"DeliveryPaymentWithdrawal('{self.ref_no}')"


# Arrears for deliverer
class DeliveryPaymentArrears(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    note = db.Column(db.String(255), nullable=True)
    is_receive = db.Column(db.Boolean, nullable=False, default=False) # Deliverer action
    is_deduct = db.Column(db.Boolean, nullable=False, default=False) # Admin action
    pay_id = db.Column(db.Integer, db.ForeignKey('delivery_payment.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    withdrawl_id = db.Column(db.Integer, db.ForeignKey('delivery_payment_withdrawal.id'), nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"DeliveryPaymentArrears('{self.id}')"


# Deliverer cash in hand of COD 
class DeliveryPaymentCashInHand(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    is_deposit = db.Column(db.Boolean, nullable=False, default=False)
    pay_id = db.Column(db.Integer, db.ForeignKey('delivery_payment.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    deposit_id = db.Column(db.Integer, db.ForeignKey('delivery_payment_deposit.id'), nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"DeliveryPaymentCashInHand('{self.id}')"


# Dposit by deliverer
class DeliveryPaymentDeposit(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    amount = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    transaction_no = db.Column(db.String(20), nullable=True)
    is_receive = db.Column(db.Boolean, nullable=False, default=False)
    pay_id = db.Column(db.Integer, db.ForeignKey('delivery_payment.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # DeliveryPaymentCashInHand one to many
    cash_in_hand = db.relationship('DeliveryPaymentCashInHand', backref='deliverypaymentdeposit', lazy=True)

    def __repr__(self):
        return f"DeliveryPaymentDeposit('{self.ref_no}')"


#  Deliverer Blacklist tockents
class DeliveryBlacklistToken(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, default=utc_now)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<DeliveryBlacklistToken token={self.token}>"


# Payment Processing price plan
class PaymentProcessPricePlan(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(15),  unique=True, nullable=False)
    value = db.Column(db.String(8),  nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"PaymentProcessPricePlan('{self.id}')"


# Customer user
class CustomerUser(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True, default=lambda: str(uuid4()))
    contact_no = db.Column(db.String(15),  unique=True, nullable=False) 
    is_confirm = db.Column(db.Boolean, nullable=False, default=False)
    confirm_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    is_logged_in = db.Column(db.Boolean, nullable=False, default=False)
    is_inactive = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # CustomerProfile one to one
    profile = db.relationship('CustomerProfile', uselist=False, backref='customeruser', lazy=True)
    # CustomerLocation one to many
    location = db.relationship('CustomerLocation', backref='customeruser', lazy=True)
    # CustomerCard one to many
    card = db.relationship('CustomerCard', backref='customeruser', lazy=True)
    # OrderMobile one to many
    order_mobile = db.relationship('OrderMobile', backref='customeruser', lazy=True)
    # CustomerTicket one to many
    ticket = db.relationship('CustomerTicket', backref='customeruser', lazy=True)
    # CustomerRefund one to many
    refund = db.relationship('CustomerRefund', backref='customeruser', lazy=True)
    # CustomerSellerFeedback one to many
    feedback_customer_seller =  db.relationship('CustomerSellerFeedback', backref='customeruser', lazy=True)
    # CustomerDeliveryFeedback one to many
    feedback_customer_delivery =  db.relationship('CustomerDeliveryFeedback', backref='customeruser', lazy=True)
    # SellerCustomerFeedback one to many
    feedback_seller_customer =  db.relationship('SellerCustomerFeedback', backref='customeruser', lazy=True)
    # DeliveryCustomerFeedback one to many
    feedback_delivery_customer =  db.relationship('DeliveryCustomerFeedback', backref='customeruser', lazy=True)
    # CustomerNotification one to many
    notification = db.relationship('CustomerNotification', backref='customeruser', lazy=True)
    # AdminNotification one to many
    admin_notification = db.relationship('AdminNotification', backref='customeruser', lazy=True)
    # SellerNotification onr to many
    seller_notification = db.relationship('SellerNotification', backref='customeruser', lazy=True)
    # DeliveryNotification one to many
    delivery_notification = db.relationship('DeliveryNotification', backref='customeruser', lazy=True)

    def encode_access_token(self):
        now = datetime.now(timezone.utc)
        token_age_h = current_app.config.get("TOKEN_EXPIRE_HOURS")
        token_age_m = current_app.config.get("TOKEN_EXPIRE_MINUTES")
        expire = now + timedelta(hours=token_age_h, minutes=token_age_m)
        payload = dict(exp=expire, iat=now, user_id=self.id, sub=self.public_id)
        key = current_app.config.get("SECRET_KEY")
        return jwt.encode(payload, key, algorithm="HS256")
    
    @staticmethod
    def decode_access_token(access_token):
        if isinstance(access_token, bytes):
            access_token = access_token.decode("ascii")
        if access_token.startswith("Bearer "):
            split = access_token.split("Bearer")
            access_token = split[1].strip()
        try:
            key = current_app.config.get("SECRET_KEY")
            payload = jwt.decode(access_token, key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            error = "Access token expired. Please log in again."
            return Result.Fail(error)
        except jwt.InvalidTokenError:
            error = "Invalid token. Please log in again."
            return Result.Fail(error)
        
        if CustomerBlacklistToken.check_blacklist(access_token):
            error = "Token blacklisted. Please log in again."
            return Result.Fail(error)
        user_dict = dict(
            user_id = payload["user_id"],
            public_id=payload["sub"],
            token=access_token,
            expires_at=payload["exp"],
        )

        return Result.Ok(user_dict)

    def __repr__(self):
        return f"CustomerUser('{self.id}')"


# Customer profile
class CustomerProfile(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name =  db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(50), nullable=False, default='default_avatar.png')
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False, unique = True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerProfile('{self.ref_no}')"


# Customer location
class CustomerLocation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(10), nullable=False)
    place_no = db.Column(db.String(75), nullable=True)
    street_name = db.Column(db.String(75), nullable=True)
    location_text = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerLocation('{self.id}')"


# Customer specific Bank
class CustomerCard(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    bank_name = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(1), nullable=False) # v = Visa, m = Master, a = Amex 
    card_no = db.Column(db.String(255), nullable=False)
    cvv = db.Column(db.String(255), nullable=False)
    holder = db.Column(db.String(75), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerCard('{self.id}')"


# Customer refund 
class CustomerRefund(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(1), nullable=False) # d = Deposit c = Credited
    value = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    is_refund = db.Column(db.Boolean, nullable=False, default=False)
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False)
    return_id = db.Column(db.Integer, db.ForeignKey('order_return.id'), nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerRefund('{self.ref_no}')"


# Customer Blacklist tockents
class CustomerBlacklistToken(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, default=utc_now)
    expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, expires_at):
        self.token = token
        self.expires_at = dtaware_fromtimestamp(expires_at, use_tz=timezone.utc)
    
    @classmethod
    def check_blacklist(cls, token):
        exists = cls.query.filter_by(token=token).first()
        return True if exists else False

    def __repr__(self):
        return f"<CustomerBlacklistToken token={self.token}>"


# Grocery product term
# Terms use as taxonomies for grocery product
class GroceryProductTerm(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    description = db.Column(JSON, nullable=True)
    image = db.Column(db.String(50), nullable=False, default='default_grocery.png')
    is_inactive = db.Column(db.Boolean, nullable=False, default=False) 
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # GroceryProductTermMap one to many
    product = db.relationship('GroceryProductTermMap', backref='groceryproductterm',  lazy=True)
    # PromoGrocery one to many
    promo = db.relationship('PromoGrocery', backref='groceryproductterm',  lazy=True)
    # AdGrocery one to many
    ad = db.relationship('AdGrocery', backref='groceryproductterm',  lazy=True)
    
    def __repr__(self):
        return f"GroceryProductTerm('{self.term}')"


# Grocery product taxonomy
# Terms fall in to taxonomies
class GroceryProductTaxonomy(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    taxonomy = db.Column(db.String(50), nullable=False) # category, brand, size, unit 
    description = db.Column(db.String(100), nullable=True)
    term_id = db.Column(db.Integer, db.ForeignKey('grocery_product_term.id'), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('grocery_product_term.id'), nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # Term relationship aliase
    grocery_term = db.relationship("GroceryProductTerm", foreign_keys=[term_id])
    parent_term = db.relationship("GroceryProductTerm", foreign_keys=[parent_id])

    def __repr__(self):
        return f"GroceryProductTaxonomy('{self.taxonomy}')"


# Map grocery product with grocery product taxonomy term
class GroceryProductTermMap(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('grocery_product.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('grocery_product_term.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint(product_id, term_id),) # Composite unique key

    def __repr__(self):
        return f"GroceryProductTermMap('{self.id}')"


# Grocery product
class GroceryProduct(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    is_feature = db.Column(db.Boolean, nullable=False, default=False) # Promotion option
    state = db.Column(db.Integer, nullable=False) # 0 = Inactice, 1 = Live, 2 = Pause
    is_suggest = db.Column(db.Boolean, nullable=False, default=False) # Suggest by seller
    is_accept = db.Column(db.Boolean, nullable=False, default=False) # Acceot grcery sugges bu seller
    is_reject = db.Column(db.Boolean, nullable=False, default=False) # Reject grcery sugges bu seller
    image = db.Column(db.String(50), nullable=False, default='default_grocery.png')   
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # Map term taxonomies for product
    taxonomy = db.relationship('GroceryProductTermMap', backref='groceryproduct',  lazy=True)
    # GroceryProductRemark one to many
    remark = db.relationship('GroceryProductRemark', backref='groceryproduct',  lazy=True)
    # GroceryProductStock one to many
    stock = db.relationship('GroceryProductStock', backref='groceryproduct',  lazy=True)
    # OrderGrocery one to many
    order = db.relationship('OrderGrocery', backref='groceryproduct',  lazy=True)
    # GroceryProductSuggest one to many
    suggest = db.relationship('GroceryProductSuggest', backref='groceryproduct',  lazy=True)

    def __repr__(self):
        return f"GroceryProduct('{self.ref_no}')"


# Grocery product remarks
# Add remarks to products
class GroceryProductRemark(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('grocery_product.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"GroceryProductRemark('{self.ref_no}')"


# Grocery product stock
# Related to seller
class GroceryProductStock(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Float, nullable=False)
    regular_price = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    sale_price = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    is_idle = db.Column(db.Boolean, nullable=False, default=False)
    product_id = db.Column(db.Integer, db.ForeignKey('grocery_product.id'), nullable=False)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"GroceryProductStock('{self.id}')"


# Seller suggest grocery product
class GroceryProductSuggest(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('grocery_product.id'), nullable=False)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False) # Suggest profile
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True) # Reviewd user
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f" GroceryProductSuggest('{self.id}')"


# Food term
# Terms use as taxonomies for food
class FoodTerm(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    term = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False)
    description = db.Column(JSON,nullable=True)
    image = db.Column(db.String(50), nullable=False, default='default_food.png')
    is_inactive = db.Column(db.Boolean, nullable=False, default=False) 
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # FoodTaxonomy one to many
    food = db.relationship('FoodTermMap', backref='foodterm',  lazy=True)
    # OrderFoodTaxonomy one to many
    order_taxonomy = db.relationship('OrderFoodTaxonomy', backref='foodterm',  lazy=True)
    # PromoFood one to many
    promo = db.relationship('PromoFood', backref='foodterm',  lazy=True)
    # AdFood one to many
    ad = db.relationship('AdFood', backref='foodterm',  lazy=True)
    
    def __repr__(self):
        return f"FoodTerm('{self.term}')"


# Food taxonomy
# Terms fall into taxonomies
class FoodTaxonomy(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    taxonomy = db.Column(db.String(50), nullable=False) # category, addon, size
    description = db.Column(db.String(100), nullable=True)
    term_id = db.Column(db.Integer, db.ForeignKey('food_term.id'), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('food_term.id'), nullable=True)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=True) # Seller id not null when add by seller
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # Term relationship aliase
    food_term = db.relationship("FoodTerm", foreign_keys=[term_id])
    parent_term = db.relationship("FoodTerm", foreign_keys=[parent_id])

    def __repr__(self):
        return f"GroceryProductTaxonomy('{self.taxonomy}')"


# Map food with grocery food taxonomy terms
class FoodTermMap(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('food_term.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint(food_id, term_id),) # Composite unique key

    def __repr__(self):
        return f"FoodTermMap('{self.id}')"


# Food
class Food(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text(), nullable=True)
    regular_price = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    sale_price = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    is_feature = db.Column(db.Boolean, nullable=False, default=False) # Promotion option
    state = db.Column(db.Integer, nullable=False) # 0 = Inactice, 1 = Live, 2 = Pause
    is_reject = db.Column(db.Boolean, nullable=False, default=False)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    image = db.Column(db.String(50), nullable=False, default='default_food.png')   
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

     # Map term taxonomies for food
    taxonomies = db.relationship('FoodTermMap', backref='food',  lazy=True)
    # OrderFood one to many
    order = db.relationship('OrderFood', backref='food',  lazy=True)

    def __repr__(self):
        return f"Food('{self.ref_no}')"


# Order
class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(1), nullable=False) # g = Grocery f = Food
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    gross =  db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    discount = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    pay_process_fee = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    delivery_fee = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    net = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    is_mobile = db.Column(db.Boolean, nullable=False, default=False) # Made using mobile app
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    is_hold = db.Column(db.Boolean, nullable=False, default=False)
    is_cancel = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # OrderMobile one to one 
    mobile = db.relationship('OrderMobile', uselist=False, backref='order', lazy=True)
    # OrderDeliveryAction one to one
    delivery_action = db.relationship('OrderDeliveryAction', uselist=False, backref='order', lazy=True)
    # OrderNote one to many
    note = db.relationship('OrderNote', backref='order', lazy=True)
    # OrderPayment one to many
    pay = db.relationship('OrderPayment', backref='order', lazy=True)
    # OrderGrocery one to many
    grocery = db.relationship('OrderGrocery', backref='order', lazy=True)
    # OrderFood one to many
    food = db.relationship('OrderFood', backref='order', lazy=True)
    # OrderReturn one to many
    order_return = db.relationship('OrderReturn', backref='order', lazy=True)
    # SellerPaymentArrears one to one
    seller_arrears = db.relationship('SellerPaymentArrears', uselist=False, backref='order', lazy=True)
    # DeliveryPaymentArrears one to many
    delivery_arrears = db.relationship('DeliveryPaymentArrears', uselist=False, backref='order', lazy=True)
    # DeliveryPaymentCashInHand one to one
    delivery_cash_in_hand = db.relationship('DeliveryPaymentCashInHand', uselist=False, backref='order', lazy=True)
    # Feedback one to many
    feedback = db.relationship('Feedback', backref='order', lazy=True)
    # OrderCupon one to many
    order_cupoon = db.relationship('OrderCupon', backref='order', lazy=True)

    def __repr__(self):
        return f"Order('{self.ref_no}')"


# Order mobile
# Order made using mobile app
class OrderMobile(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    is_accept = db.Column(db.Boolean, nullable=False, default=False) # Seller action
    is_reject = db.Column(db.Boolean, nullable=False, default=False) # Seller action
    prep_duration = db.Column(db.Float, nullable=True) # Seller action
    is_ready = db.Column(db.Boolean, nullable=False, default=False) # Seller action
    is_pick = db.Column(db.Boolean, nullable=False, default=False) # Deliverer action
    is_ship = db.Column(db.Boolean, nullable=False, default=False) # Seller action
    ship_time = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    is_deliver = db.Column(db.Boolean, nullable=False, default=False) # Deliverer action
    is_recive = db.Column(db.Boolean, nullable=False, default=False) # Customer    
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False)
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=True)
    latitude = db.Column(db.Float, nullable=False) # Customer location
    longitude = db.Column(db.Float, nullable=False) # Customer Location
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"OrderMobile('{self.ref_no}')"


# Order addon
# Delivere action update for seller
class OrderDeliveryAction(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    is_accept = db.Column(db.Boolean, nullable=False, default=False)
    is_arrive = db.Column(db.Boolean, nullable=False, default=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"OrderDeliveryAction('{self.id}')"


# Order note
class OrderNote(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"OrderDeliveryAction('{self.id}')"


# Payments of order
class OrderPayment(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    overdue = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    payment = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # OrderPaymentDetails one to many
    pay_dt = db.relationship('OrderPaymentDetails', backref='orderpayment', lazy=True)

    def __repr__(self):
        return f"OrderPayment('{self.id}')"


# Note for order payment
class OrderPaymentDetails(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    overdue = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    payment = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    balance = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    method = db.Column(db.String(1), nullable=False) # c = Card, o = COD
    contnet = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    pay_id = db.Column(db.Integer, db.ForeignKey('order_payment.id'), nullable=False)
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    is_cancel = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"OrderPaymentNote('{self.ref_no}')"


# Grocery product order
class OrderGrocery(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Float, nullable=False)
    reg_rate = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Regular price rate
    sub_unit_rate = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Sale unit rate
    unit_rate = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Sold unit rate
    sub_total = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Sale unit rate x qty
    total = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Sold unit rate x qty
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('grocery_product.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # OrderReturnGrocery one to one 
    return_grocery = db.relationship('OrderReturnGrocery', uselist=False, backref='order', lazy=True)

    def __repr__(self):
        return f"OrderGrocery('{self.id}')"


# Food order
class OrderFood(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Float, nullable=False)
    reg_rate = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Regular pr
    sub_unit_rate = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Sale unit rate
    unit_rate = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Sold unit rate
    sub_total = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Sale unit rate x qty
    total = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None)) # Sold unit rate x qty
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # OrderFoodTaxonomy one to many
    taxonomy = db.relationship('OrderFoodTaxonomy', backref='orderfood',  lazy=True)

    def __repr__(self):
        return f"FoodOrder('{self.id}')"


# Order Food Taxonomy
class OrderFoodTaxonomy(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    taxonomy = db.Column(db.String(50), nullable=False) # addon, size
    content = db.Column(JSON,nullable=True)
    food_order_id = db.Column(db.Integer, db.ForeignKey('order_food.id'), nullable=False)
    term_id = db.Column(db.Integer, db.ForeignKey('food_term.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"OrderFoodTaxonomy('{self.id}')"


# Order cupon
class OrderCupon(db.Model):

    id = db.Column(db.Integer, primary_key=True)    
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    cupon_id = db.Column(db.Integer, db.ForeignKey('cupon.id'), nullable=False, unique=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"OrderCupon('{self.id}')"


# Returns of order
# Grocery product only
class OrderReturn(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    note = db.Column(db.String(255), nullable=False)        
    is_accept = db.Column(db.Boolean, nullable=False, default=False) # Admin action
    is_reject = db.Column(db.Boolean, nullable=False, default=False) # Admin action
    is_pick = db.Column(db.Boolean, nullable=False, default=False) # Deliverer action
    is_receive = db.Column(db.Boolean, nullable=False, default=False) # Seller action
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    is_cancel = db.Column(db.Boolean, nullable=False, default=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # OrderReturnGrocery one to many
    return_grocery = db.relationship('OrderReturnGrocery', backref='orderreturn',  lazy=True)
    # CustomerRefund one to one
    refund = db.relationship('CustomerRefund', uselist=False, backref='orderreturn',  lazy=True)

    def __repr__(self):
        return f"OrderReturn('{self.ref_no}')"    


# Grocery return details
class OrderReturnGrocery(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    qty = db.Column(db.Float, nullable=False)
    return_id = db.Column(db.Integer, db.ForeignKey('order_return.id'), nullable=True)
    is_restock = db.Column(db.Boolean, nullable=False, default=False) # Re add to stock
    grocery_order_id = db.Column(db.Integer, db.ForeignKey('order_grocery.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"OrderReturnGrocery('{self.id}')" 


# Feedback of users
# Centreal table for review and rating
class Feedback(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    rate = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(255), nullable=True)
    is_use =  db.Column(db.Boolean, nullable=False, default=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # CustomerSellerFeedback one to one
    customer_seller = db.relationship('CustomerSellerFeedback', uselist=False, backref='feedback', lazy=True)
    # CustomerDeliveryFeedback one to one
    customer_delivery = db.relationship('CustomerDeliveryFeedback', uselist=False, backref='feedback', lazy=True)
    # SellerCustomerFeedback one to one
    seller_customer = db.relationship('SellerCustomerFeedback', uselist=False, backref='feedback', lazy=True)
    # SellerDeliveryFeedback one to one
    seller_delivery = db.relationship('SellerDeliveryFeedback', uselist=False, backref='feedback', lazy=True)
    # DeliveryCustomerFeedback one to one 
    delivery_customer = db.relationship('DeliveryCustomerFeedback', uselist=False, backref='feedback', lazy=True)
    # DeliverySellerFeedback one to one
    delivery_seller = db.relationship('DeliverySellerFeedback', uselist=False, backref='feedback', lazy=True)

    # Calculate rate
    def rate_cal(dividend, divisor):
        return rate_cal(dividend, divisor)

    def __repr__(self):
        return f"Feedback('{self.id}')"


# Cutomer -> Seller feedback
class CustomerSellerFeedback(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=True)
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerSellerFeedback('{self.id}')"


# Customer -> Delivery feedback
class CustomerDeliveryFeedback(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=True)
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False)
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerSellerFeedback('{self.id}')"


# Seller -> Customer feedback
class SellerCustomerFeedback(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=True)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerSellerFeedback('{self.id}')"


# Seller -> Delivery feedback
class SellerDeliveryFeedback(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=True)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerSellerFeedback('{self.id}')"


# Delivery -> Customer feedback
class DeliveryCustomerFeedback(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=True)
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=False)
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerSellerFeedback('{self.id}')"


# Delivery -> Seller feedback
class DeliverySellerFeedback(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'), nullable=True)
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=False)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerSellerFeedback('{self.id}')"


# Ticket categories for tickets
class TicketCategory(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(1), nullable=False) # s = Seller, d = Deliverer, c = Customer
    term = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # SellerTicket one to many
    seller_ticket = db.relationship('SellerTicket', backref='ticketcategory',  lazy=True)
    # DeliveryTicket one to many
    delivery_ticket = db.relationship('DeliveryTicket', backref='ticketcategory',  lazy=True)

    def __repr__(self):
        return f"TicketCategory('{self.id}')"  


# Seller ticket
class SellerTicket(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)    
    is_open = db.Column(db.Boolean, nullable=False, default=False)
    is_close = db.Column(db.Boolean, nullable=False, default=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('ticket_category.id'), nullable=True)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # SellerTicketMessage one to many
    message = db.relationship('SellerTicketMessage', backref='sellerticket',  lazy=True)

    def __repr__(self):
        return f"SellerTicket('{self.ref_no}')"  


# Seller messages of ticket
class SellerTicketMessage(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    seller_text = db.Column(db.Text(500), nullable=True)    
    admin_text = db.Column(db.Text(500), nullable=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('seller_ticket.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"SellerTicketMessage('{self.id}')" 


# Delivery ticket
class DeliveryTicket(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)    
    is_open = db.Column(db.Boolean, nullable=False, default=False)
    is_close = db.Column(db.Boolean, nullable=False, default=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('ticket_category.id'), nullable=True)
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # DeliveryTicketMessage one to many
    message = db.relationship('DeliveryTicketMessage', backref='deliveryticket',  lazy=True)

    def __repr__(self):
        return f"DeliveryTicket('{self.ref_no}')" 


# Delivery messages of ticket
class DeliveryTicketMessage(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    delivery_text = db.Column(db.Text(500), nullable=True)    
    admin_text = db.Column(db.Text(500), nullable=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('delivery_ticket.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"DeliveryTicketMessage('{self.id}')" 


# Customer ticket
class CustomerTicket(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)    
    is_open = db.Column(db.Boolean, nullable=False, default=False)
    is_close = db.Column(db.Boolean, nullable=False, default=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('ticket_category.id'), nullable=True)
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # CustomerTicketMessage one to many
    message = db.relationship('CustomerTicketMessage', backref='customerticket',  lazy=True)

    def __repr__(self):
        return f"CustomerTicket('{self.ref_no}')" 


# Customer messages of ticket
class CustomerTicketMessage(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    customer_text = db.Column(db.Text(500), nullable=True)    
    admin_text = db.Column(db.Text(500), nullable=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('customer_ticket.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerTicketMessage('{self.id}')" 


# Central promotions made by admin
class Promo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(1), nullable=False) # g = Grocery f = Food
    from_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    to_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    is_live = db.Column(db.Boolean, nullable=False, default=False)
    is_pause = db.Column(db.Boolean, nullable=False, default=False)
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    is_cancel = db.Column(db.Boolean, nullable=False, default=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # PromoGrocery one to many
    grocery = db.relationship('PromoGrocery', backref='promo', lazy=True)
    # PromoFood one to many
    food = db.relationship('PromoFood', backref='promo', lazy=True)
    # SellerPromo one to many
    seller = db.relationship('SellerPromo', backref='promo', lazy=True)

    def __repr__(self):
        return f"Promo('{self.ref_no}')" 


# Grocery promos
class PromoGrocery(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    discount = db.Column(db.String(4), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'), nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('grocery_product_term.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"PromoGrocery('{self.id}')" 


# Food promos
class PromoFood(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    discount = db.Column(db.String(4), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'), nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('food_term.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"PromoGrocery('{self.id}')" 


# Seller contribution to promo
class SellerPromo(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    is_open = db.Column(db.Boolean, nullable=False, default=False)
    is_close = db.Column(db.Boolean, nullable=False, default=False)
    promo_id = db.Column(db.Integer, db.ForeignKey('promo.id'), nullable=False)
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"PromoGrocery('{self.id}')"


# Ad created by admin
class Ad(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    type = db.Column(db.String(1), nullable=False) # g = Grocery f = Food
    from_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    to_date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    amount = db.Column(db.Numeric(precision=12, scale=2, asdecimal=True, decimal_return_scale=None))
    content = db.Column(JSON,nullable=True)
    is_live = db.Column(db.Boolean, nullable=False, default=False)
    is_pause = db.Column(db.Boolean, nullable=False, default=False)
    is_complete = db.Column(db.Boolean, nullable=False, default=False)
    is_cancel = db.Column(db.Boolean, nullable=False, default=False)
    image = db.Column(db.String(50), nullable=False, default='default_banner.png')
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # AdGrocery one to many
    grocery = db.relationship('AdGrocery', backref='promo', lazy=True)
    # AdFood one to many
    food = db.relationship('AdFood', backref='promo', lazy=True)

    def __repr__(self):
        return f"PromoGrocery('{self.id}')"


# Grocery promos
class AdGrocery(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('grocery_product_term.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"PromoGrocery('{self.id}')" 


# Food promos
class AdFood(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id'), nullable=False)
    cat_id = db.Column(db.Integer, db.ForeignKey('food_term.id'), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"PromoGrocery('{self.id}')" 


# Notification for admins
class AdminNotification(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    content = db.Column(JSON,nullable=True) # {"text":'String, "url":""}
    intend_user_permit = db.Column(db.String(80), nullable=False) # Target user permission group
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True) # Noticication opend user
    send_seller_id = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=True) # For seller create notification
    send_deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=True) # For delivery boy create notification
    send_cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=True) # For customer create notiification
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"AdminNotification('{self.id}')"


# Notification for seller
class SellerNotification(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    content = db.Column(JSON,nullable=True) # {"text":'String, "url":""}
    seller_prof = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=False) # Seller profile
    intend_user_permit = db.Column(db.String(80), nullable=False) # Target user permission group
    seller_id = db.Column(db.Integer, db.ForeignKey('seller_user.id'), nullable=True) # Noticication opend user
    send_admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True) # For admin create notification
    send_deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=True) # For delivery boy create notification
    send_cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=True) # For customer create notiification
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"SellerNotification('{self.id}')"


# Notification for delivery boy
class DeliveryNotification(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    content = db.Column(JSON,nullable=True) # {"text":'String, "url":""}
    deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=False)
    send_admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True) # For admin create notification
    send_seller_id = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=True) # For seller create notification
    send_cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=True) # For customer create notiification
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"DeliveryNotification('{self.id}')"


# Notification for delivery boy
class CustomerNotification(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    content = db.Column(JSON,nullable=True) # {"text":'String, "url":""}
    cus_id = db.Column(db.Integer, db.ForeignKey('customer_user.id'), nullable=False)
    send_admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=True) # For admin create notification
    send_seller_id = db.Column(db.Integer, db.ForeignKey('seller_profile.id'), nullable=True) # For seller create notification
    send_deliverer_id = db.Column(db.Integer, db.ForeignKey('delivery_user.id'), nullable=True) # For delivery create notiification
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    def __repr__(self):
        return f"CustomerNotification('{self.id}')"


# Cupons
class Cupon(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    ref_no = db.Column(db.String(20), unique=True, nullable=False)
    value = db.Column(db.String(7), nullable=False) # For precentage use % , For rate use .00
    expires_at = db.Column(db.DateTime, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin_user.id'), nullable=False)
    is_use = db.Column(db.Boolean, nullable=False, default=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    # OrderCupon one to one
    order_cupon = db.relationship('OrderCupon', uselist=False, backref='cupon', lazy=True)

    def __repr__(self):
        return f"Cupon('{self.ref_no}')"