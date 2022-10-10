from flask_restx import Namespace, Resource
from http import HTTPStatus


from .dto import (
    # gcart_parser,
    order_parser,
    pay_parser,
    food_order_parser,
    food_pay_parser,
    return_parser,
    order_cancel_parser,
    rev_parser,
    ticket_parser,
    #payment_parser,
)
from .functions import (
    # add_cart,
    customer_ticket,
    order_grocery_create,
    pay_grocery_order,
    order_food_create,
    pay_food_order,
    return_order,
    cancel_order,
    grocery_orders,
    grocery_order_details,
    review_create,
    customer_ticket,
    save_card,
    return_list,
    return_details,
    food_orders,
    food_order_details,
    #get_available_coupons,
    get_ticket_categories,
    get_coupon_details,
    changestate
)

order_ns = Namespace(name="order", validate=True)

##### Grocery  Qty ########
# check QTY
'''
@order_ns.route("/grocery/cart/<int:seller_id>", endpoint="add_cart")
class GCart(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(gcart_parser)
    @order_ns.response(int(HTTPStatus.OK), "Added to cart.")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self, seller_id):

        """Post param to check Grocery Item QTY when adding to Cart
        Demo pass values
        { Seller_id:1,,Grocery_id:'1', quantity:float }

        Intended Result
        {
            status:success/fail,
            message:added to cart / quantity not available /seller invalid,
            availble_quantity=stock availability float,
            price=float,
            name=product name string
        }
        """
        data = gcart_parser.parse_args()
        return add_cart(seller_id, data)

'''

# Place Order
@order_ns.route("/grocery/create", endpoint="add_order")
class Order(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(order_parser)
    @order_ns.response(int(HTTPStatus.OK), "Added to order.")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):

        """Add Grocery order
        Demo pass values
        {
        stringDic: "{'product_id':{'product_total_price':'qty'},'product_id':{'product_total_price':'qty'}}" ,
        "gross": 200,
        "delivery_fee": 75,
        "net": 275,
        "coupon_id": 1
        "is_mobile":True of False,
        "seller_id":1,
        "longitude":80,
        "latitude":7,
        "pay_method":"p",p=payhere


        }

        Intended Result
        {
            status:success/fail,
            message:added to cart / already in cart/ quantity not available /seller invalid/place order,
            availble_quantity=stock availability float,

        }
        """
        data = order_parser.parse_args()
        return order_grocery_create(data)


# Payment Grocery
@order_ns.route("/grocery/payment", endpoint="pay_confirm")
class Pay(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(pay_parser)
    @order_ns.response(int(HTTPStatus.OK), "paid")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):

        """Order Grocery payment
        Demo pass values
        {
        Seller_id:1,
        order_id:1,
        pay_method:"s": "Cash", "c": "Card", "o": "COD","r":"credit",
        payment_confirm:True/False,
        content:"{'receipt_no': '990761', 'type': 'visa', 'holder_name':'',card_no:'4444','expire','11/24','cvv':'600'}"

        }

        Intended Result
        {
            status:success/fail,
            message:payment added,

        }
        """
        data = pay_parser.parse_args()
        return pay_grocery_order(data)


##### Food   ########
# Place Food Order
@order_ns.route("/food/create", endpoint="food_order")
class FoodOrder(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(food_order_parser)
    @order_ns.response(int(HTTPStatus.OK), "Added to food order.")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):

        """Add Food order
        Demo pass values
        {
        "Seller_id":1,
        "food": " {'food_id':{'food_total_price':'qty'},'food_id':{'food_total_price':'qty'}}" ,
        "size": "{'size_term_id':{'food_id':'food_size_total_price'},'size_term_id':{'food_id':'food_size_total_price'}}", or ""
        "addon": "{'addon_term_id':{'food_id':'qty'},'addon_term_id':{'food_id':'qty'}}", or ""
        "gross": 200,
        "delivery_fee": 75,
        "net": 275,
        "coupon_id": 1,
        "longitude":80,
        "latitude":7,


        }

        Intended Result
        {
            status:success/fail,
            message:place order/failed to load,
            availble_quantity=stock availability float,

        }
        """
        data = food_order_parser.parse_args()
        return order_food_create(data)


# Payment Food
@order_ns.route("/food/payment", endpoint="food_pay_confirm")
class FoodPay(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(food_pay_parser)
    @order_ns.response(int(HTTPStatus.OK), "paid")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):

        """Food payment
        Demo pass values
        {
        order_id:1,
        pay_method:"s": "Cash", "c": "Card", "o": "COD","r":"credit",
        payment_confirm:True/False,
        content:{"receipt_no": "990761", "type": "visa", "holder_name":"",card_no:"4444","expire","11/24","cvv":"600"}
        }

        Intended Result
        {
            status:success/fail,
            message:payment added,

        }
        """
        data = food_pay_parser.parse_args()
        return pay_food_order(data)


# Order Return
@order_ns.route("/grocery/return/create", endpoint="order_return")
class OrderReturn(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(return_parser)
    @order_ns.response(int(HTTPStatus.OK), "Order return")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):

        """Post param to return Order
        Demo pass values
        {
        order_id:1,
        product_data: "{'1':{'product_id':'qty'},'2':{'product_id':'qty'},'3':{'product_id':'qty'}}" ,
        return_note:adasdsad

        }

        Intended Result
        {
            status:success/fail,
            message:Order Return,

        }
        """
        data = return_parser.parse_args()
        return return_order(data)


# Order cancel
@order_ns.route("/cancel", endpoint="order_cancel")
class OrderCancel(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(order_cancel_parser)
    @order_ns.response(int(HTTPStatus.OK), "Order Cancel")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):

        """Cancel Order
        Demo pass values
        {
        order_id:1,
        type:f or g
        }

        Intended Result
        {
            status:success/fail,
            message:Order Return,

        }
        """
        data = order_cancel_parser.parse_args()
        return cancel_order(data)


# all return orders
@order_ns.route("/grocery/return/all", endpoint="return_list")
class ReturnOrders(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "All return Orders")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self):
        """Customer All Return Orders"""

        return return_list()


# return product details
@order_ns.route("/grocery/return/<int:return_id>", endpoint="return_product")
class ReturnDetails(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "All return Orders")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, return_id):
        """Return Per Product details"""

        return return_details(return_id)


# See all orders
@order_ns.route("/grocery/all", endpoint="grocery_orders")
class SeeGrocery(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "All Orders")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self):
        """All Grocery Order Details"""

        return grocery_orders()


# See all orders
@order_ns.route("/food/all", endpoint="food_orders")
class SeeFood(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "All Orders")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self):
        """All Food Order Details"""

        return food_orders()


# See one order details
@order_ns.route("/grocery/<int:order_id>", endpoint="order_details")
class GroceryOrderDetails(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "Order Status")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, order_id):
        """One Groery Order Data"""

        return grocery_order_details(order_id)


# See one order details
@order_ns.route("/food/<int:order_id>", endpoint="food_order_details")
class FoodOrderDetails(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "Order Status")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, order_id):
        """One Food Order Data"""

        return food_order_details(order_id)


@order_ns.route("/review/<int:deliver_id>", endpoint="deliverer_review")
class Review(Resource):
    """Handles HTTP requests to URL: /api/v1/order/review/<int:deliver_id"""

    @order_ns.doc(security="Bearer")
    @order_ns.expect(rev_parser)
    @order_ns.response(int(HTTPStatus.OK), "rate saved.")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @order_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self, deliver_id):
        """Post customer-deliverer review
        Demo pass values
        { deliverer_id:'1', rate:Integer ,review:String,order_id:Integer,customer_id:Integer  }

        Intended Result
        {
            status:success/fail,
            message:review_created or error

        }
        """
        data = rev_parser.parse_args()
        res = review_create(deliver_id, data)

        return res


# Customer Ticket
@order_ns.route("/ticket", endpoint="customer_ticket")
class CustomerTicket(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(ticket_parser)
    @order_ns.response(int(HTTPStatus.OK), "Customer Ticket")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):
        """Post customer Ticket
        Demo pass values
        { ticket_category_id:1,
        customer_text:str ,

          }

        Intended Result
        {
            status:success/fail,
            message:

        }
        """
        data = ticket_parser.parse_args()
        res = customer_ticket(data)
        return res


# Payment Save
#@order_ns.route("/save_card", endpoint="save_card")
#class SaveCard(Resource):
#    @order_ns.doc(security="Bearer")
#    @order_ns.expect(payment_parser)
#    @order_ns.response(int(HTTPStatus.OK), "Save Payment")
#    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
#    def post(self):
        """
        Post param to save payment details
         Demo pass values
        { bank_number:1,
        type:str ,
        card_number:int,
        expire:"11/25",
        cvv:123,
        holder:"",
          }

        Intended Result
        {
            status:success/fail,
            message:save card

        }
        """
#        data = payment_parser.parse_args()
 #       return save_card(data)


# See one order details
#@order_ns.route("/coupons", endpoint="available_coupons")
#class AvailableCoupons(Resource):
#    @order_ns.doc(security="Bearer")
#    @order_ns.response(int(HTTPStatus.OK), "Order Status")
#    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
#    def get(self):
#        """All available Coupons"""

#        return get_available_coupons()


# See one order details
@order_ns.route("/coupons/<int:coupon_ref_no>", endpoint="coupon_details")
class CouponDetails(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "Order Status")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, coupon_ref_no):
        """Coupon Details"""

        return get_coupon_details(coupon_ref_no)


# See one order details
@order_ns.route("/ticket_categories", endpoint="ticket_categories")
class TicketCategories(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "Order Status")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self):
        """All ticket categories"""

        return get_ticket_categories()

#change state of order
@order_ns.route("/received/<int:order_id>", endpoint="received_state")
class ChangeState(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "Order Status")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")

    def put(self,order_id):
        return changestate(order_id)
