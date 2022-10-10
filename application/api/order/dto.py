from datetime import datetime
from flask_restx.reqparse import RequestParser



#
# ---------------------------------------------Models-----------------------------------------------------------------------------
#


#
# ---------------------------------------Request parsers--------------------------------------------------------------------------
#


# Use in add to cart on Grocery
"""gcart_parser = RequestParser(bundle_errors=True)
gcart_parser.add_argument('quantity', type=float, location="json", required=True, nullable=False, help="Float")
gcart_parser.add_argument('grocery_id', type=int, location="json", required=True, nullable=False, help="Int")"""


# Use in Place Order on Grocery
order_parser = RequestParser(bundle_errors=True)
order_parser.add_argument(
    "stringDic", type=str, location="json", required=True, nullable=False, help="json"
)
order_parser.add_argument(
    "gross", type=float, location="json", required=True, nullable=False, help="float"
)
order_parser.add_argument(
    "delivery_fee",
    type=float,
    location="json",
    required=True,
    nullable=True,
    help="int",
)
order_parser.add_argument(
    "net", type=float, location="json", required=True, nullable=False, help="float"
)
order_parser.add_argument(
    "coupon_id", type=int, location="json", required=False, nullable=True, help="int"
)
order_parser.add_argument(
    "seller_id",
    type=int,
    location="json",
    required=True,
    nullable=False,
    help="seller id",
)
order_parser.add_argument(
    "longitude",
    type=int,
    location="json",
    required=True,
    nullable=False,
    help="longitude",
)
order_parser.add_argument(
    "latitude",
    type=int,
    location="json",
    required=True,
    nullable=False,
    help="latitude",
)
order_parser.add_argument('pay_method', type=str, location="json",required=True, nullable=False,help="Payment method")

# Payments Confirm
pay_parser = RequestParser(bundle_errors=True)
pay_parser.add_argument(
    "order_id", type=int, location="json", required=True, nullable=False, help="int"
)
pay_parser.add_argument(
    "seller_id", type=int, location="json", required=True, nullable=False, help="int"
)
pay_parser.add_argument(
    "pay_method", type=str, location="json", required=True, nullable=False, help="int"
) 
pay_parser.add_argument(
    "payment_confirm",
    type=bool,
    location="json",
    required=True,
    nullable=False,
    help="payment confirmation",
)
pay_parser.add_argument(
    "content",
    type=str,
    location="json",
    required=False,
    nullable=True,
    help="card details",
)


# food order parser
food_order_parser = RequestParser(bundle_errors=True)
food_order_parser.add_argument(
    "seller_id",
    type=int,
    location="json",
    required=True,
    nullable=False,
    help="seller id",
)
food_order_parser.add_argument(
    "food", type=str, location="json", required=True, nullable=False, help="json"
)
food_order_parser.add_argument(
    "size", type=str, location="json", required=False, nullable=True, help="json"
)
food_order_parser.add_argument(
    "addon", type=str, location="json", required=False, nullable=True, help="json"
)
food_order_parser.add_argument(
    "gross", type=float, location="json", required=True, nullable=False, help="float"
)
food_order_parser.add_argument(
    "delivery_fee",
    type=float,
    location="json",
    required=False,
    nullable=True,
    help="int",
)
food_order_parser.add_argument(
    "net", type=float, location="json", required=True, nullable=False, help="float"
)
food_order_parser.add_argument(
    "coupon_id", type=int, location="json", required=False, nullable=True, help="int"
)
food_order_parser.add_argument(
    "longitude",
    type=int,
    location="json",
    required=True,
    nullable=False,
    help="longitude",
)
food_order_parser.add_argument(
    "latitude",
    type=int,
    location="json",
    required=True,
    nullable=False,
    help="latitude",
)
food_order_parser.add_argument('pay_method', type=str, location="json",required=True, nullable=False,help="Payment method")

# food pay parser
food_pay_parser = pay_parser.copy()


# order return parser
return_parser = RequestParser(bundle_errors=True)
return_parser.add_argument(
    "order_id", type=int, location="json", required=True, nullable=False, help="int"
)
return_parser.add_argument(
    "product_data",
    type=str,
    location="json",
    required=True,
    nullable=False,
    help="json",
)
return_parser.add_argument(
    "return_note",
    type=str,
    location="json",
    required=True,
    nullable=False,
    help="return note string",
)


# Order Cancel Parser
order_cancel_parser = RequestParser(bundle_errors=True)
order_cancel_parser.add_argument(
    "order_id", type=int, location="json", required=True, nullable=False, help="int"
)
order_cancel_parser.add_argument(
    "type",
    type=str,
    location="json",
    required=True,
    nullable=False,
    help="return note string",
)
order_cancel_parser.add_argument(
    "cancel_note",
    type=str,
    location="json",
    required=True,
    nullable=False,
    help="return note string",
)


# review_create Parser
rev_parser = RequestParser(bundle_errors=True)
rev_parser.add_argument(
    "rate", type=int, location="json", required=True, nullable=False, help="int 1 to 5 "
)
rev_parser.add_argument(
    "review",
    type=str,
    location="json",
    required=False,
    nullable=True,
    help="review as string(255)",
)
rev_parser.add_argument(
    "order_id",
    type=int,
    location="json",
    required=True,
    nullable=False,
    help="order-id as int ",
)


# Payment Details Parser
payment_parser = RequestParser(bundle_errors=True)
payment_parser.add_argument(
    "bank_number",
    type=int,
    location="json",
    required=True,
    nullable=False,
    help="string",
)
payment_parser.add_argument(
    "type",
    type=str,
    location="json",
    required=True,
    nullable=False,
    help="v=visa m=master a=Amex",
)
payment_parser.add_argument(
    "card_number",
    type=int,
    location="json",
    required=True,
    nullable=False,
    help="string",
)
payment_parser.add_argument(
    "expire",
    type=str,
    location="json",
    required=True,
    nullable=False,
    help="expire date",
)
payment_parser.add_argument(
    "cvv", type=int, location="json", required=True, nullable=False, help="string"
)
payment_parser.add_argument(
    "holder", type=str, location="json", required=True, nullable=False, help="string"
)


# Customer Ticket
ticket_parser = RequestParser(bundle_errors=True)
ticket_parser.add_argument(
    "ticket_category_id",
    type=int,
    location="json",
    required=False,
    nullable=True,
    help="ticket category",
)
ticket_parser.add_argument(
    "customer_text",
    type=str,
    location="json",
    required=False,
    nullable=True,
    help="string ticket message",
)
