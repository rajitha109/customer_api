from turtle import end_poly
from flask_restx import Namespace, Resource
from http import HTTPStatus


from .dto import (
    gcart_parser,
    order_parser,
    pay_parser,
    food_order_parser,
    food_pay_parser,
    return_parser,
    order_cancel_parser,
    rev_parser,
    ticket_parser,
    payment_parser
   
)
from .functions import (
    add_cart,
    customer_ticket,
    place_order,
    pay_order,
    place_food_order,
    pay_food_order,
    return_order,
    cancel_order,
    all_orders,
    grocery_order_status,
    review_create,
    customer_ticket,
    save_card,
    completed_orders,
    ongoing_orders,
)

order_ns = Namespace(name="order", validate=True)

##### Grocery  Qty ########
# check QTY
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


# Place Order
@order_ns.route("/grocery/order/<int:seller_id>", endpoint="add_order")
class Order(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(order_parser)
    # @order_ns.expect(x)
    @order_ns.response(int(HTTPStatus.OK), "Added to order.")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self, seller_id):

        """Post param to Add Grocery order
        Demo pass values
        { Seller_id:1,
        stringDic: "{'product_id':{'sold_price':'qty'},'product_id':{'sold_price':'qty'}}" ,
        "gross": 200,
        "delivery_fee": 75,
        "net": 275,
        "coupon_id": 1
        "is_mobile":True of False,
        "customer_id":6,
        "longitude":80,
        "latitude":7,
        "Payment process Price plan":1,

        }

        Intended Result
        {
            status:success/fail,
            message:added to cart / already in cart/ quantity not available /seller invalid/place order,
            availble_quantity=stock availability float,

        }
        """
        data = order_parser.parse_args()
        return place_order(seller_id, data)


# Payment Grocery
@order_ns.route("/grocery/payment/<int:seller_id>", endpoint="pay_confirm")
class Pay(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(pay_parser)
    @order_ns.response(int(HTTPStatus.OK), "paid")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self, seller_id):

        """Post param to Grocery pay
        Demo pass values
        { Seller_id:1,
        order_id:1,
        pay_method:c/o c=cash or o=card,
        payment_confirm:True/False,
        content:{"receipt_no": "990761", "type": "visa", "holder_name":"",card_no:"4444","expire","11/24","cvv":"600"}
        }

        }

        Intended Result
        {
            status:success/fail,
            message:payment added,

        }
        """
        data = pay_parser.parse_args()
        return pay_order(seller_id, data)


##### Food   ########
# Place Food Order
@order_ns.route("/food/order/<int:seller_id>", endpoint="food_order")
class FoodOrder(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(food_order_parser)
    @order_ns.response(int(HTTPStatus.OK), "Added to food order.")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self, seller_id):

        """Post param to Add Food order
        Demo pass values
        { Seller_id:1,
        "food": " {'food_id':{'sold_price':'qty'},'food_id':{'sold_price':'qty'}}" ,
        "size": "{'size_term_id':{'food_id':'sold_price'},'size_term_id':{'food_id':'sold_price'}}", or ""
        "addon": "{'addon_term_id':{'food_id':'qty'},'addon_term_id':{'food_id':'qty'}}", or ""
        "gross": 200,
        "delivery_fee": 75,
        "net": 275,
        "coupon_id": 1,
        "is_mobile":True of False,
        "customer_id":6,
        "longitude":80,
        "latitude":7,
        "payment_plan_id":1

        }

        Intended Result
        {
            status:success/fail,
            message:place order/failed to load,
            availble_quantity=stock availability float,

        }
        """
        data = food_order_parser.parse_args()
        return place_food_order(seller_id, data)


# Payment Food
@order_ns.route("/food/payment", endpoint="food_pay_confirm")
class FoodPay(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(food_pay_parser)
    @order_ns.response(int(HTTPStatus.OK), "paid")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):

        """Post param to Food pay
        Demo pass values
        {
        order_id:1,
        pay_method:c/o c=cash or o=card,
        payment_confirm:True/False,
        content:{"receipt_no": "990761", "type": "visa", "holder_name":"",card_no:"4444","expire","11/24","cvv":"600"}
        }

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
@order_ns.route("/grocery/order/return/<int:order_id>", endpoint="order_return")
class OrderReturn(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(return_parser)
    @order_ns.response(int(HTTPStatus.OK), "Order return")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self, order_id):

        """Post param to return Order
        Demo pass values
        {
        order_id:1,
        product_data: "{'1':{'product_id':'qty'},'2':{'product_id':'qty'}}" ,
        return_note:adasdsad

        }

        }

        Intended Result
        {
            status:success/fail,
            message:Order Return,

        }
        """
        data = return_parser.parse_args()
        return return_order(order_id, data)


# Order cancel
@order_ns.route("/cancel/<int:order_id>", endpoint="order_cancel")
class OrderCancel(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(order_cancel_parser)
    @order_ns.response(int(HTTPStatus.OK), "Order Cancel")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self, order_id):

        """Post param to Cancel Order
        Demo pass values
        {
        order_id:1,
        type:f or g
        }

        }

        Intended Result
        {
            status:success/fail,
            message:Order Return,

        }
        """
        data = order_cancel_parser.parse_args()
        return cancel_order(order_id, data)

#See all orders
@order_ns.route("/all/<int:customer_id>", endpoint="all_orders")
class SeeOrders(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "All Orders")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, customer_id):
        
        return all_orders(customer_id)


#See Completed orders
@order_ns.route("/completed/<int:customer_id>", endpoint="completed_orders")
class CompletedOrders(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "Completed Orders")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, customer_id):
        
        return completed_orders(customer_id)

#See ongoing orders
@order_ns.route("/ongoing/<int:customer_id>", endpoint="ongoing_orders")
class OngoingOrders(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "ongoing Orders")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, customer_id):
        
        return ongoing_orders(customer_id)




#See order status
@order_ns.route("/grocery/status/<int:order_id>", endpoint="order_status")
class OrderStatus(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.response(int(HTTPStatus.OK), "Order Status")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, order_id):

       
        
        return grocery_order_status(order_id)



@order_ns.route("/review/<int:deliver_id>", endpoint="deliverer_review")
class Review(Resource):
    """Handles HTTP requests to URL: /api/v1/order/review/<int:deliver_id"""

    @order_ns.doc(security="Bearer")
    @order_ns.expect(rev_parser)

    @order_ns.response(int(HTTPStatus.OK), "rate saved.")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @order_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    

    def post(self,deliver_id):
        ''' Post customer-deliverer review 
        Demo pass values
        { deliverer_id:'1', rate:Integer ,review:String,order_id:Integer,customer_id:Integer  }

        Intended Result
        { 
            status:success/fail,
            message:review_created or error

        }        
        '''
        data=rev_parser.parse_args()
        res=review_create(deliver_id,data)
        
        return res


#Customer Ticket
@order_ns.route("/ticket", endpoint="customer_ticket")
class CustomerTicket(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(ticket_parser)
    @order_ns.response(int(HTTPStatus.OK), "Customer Ticket")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):
        ''' Post customer Ticket 
        Demo pass values
        { ticket_category_id:1, 
        customer_text:str ,
        customer_id:int,
          }

        Intended Result
        { 
            status:success/fail,
            message:

        }        
        '''
        data=ticket_parser.parse_args()
        res=customer_ticket(data)        
        return res


#Payment Save
@order_ns.route("/savecard", endpoint="save_card")
class SaveCard(Resource):
    @order_ns.doc(security="Bearer")
    @order_ns.expect(payment_parser)
    @order_ns.response(int(HTTPStatus.OK), "Save Payment")
    @order_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):
        '''
        Post param to save payment details
         Demo pass values
        { bank_number:1, 
        type:str ,
        card_number:int,
        expire:"11/25",
        cvv:123,
        holder:"",
        customer_id:,
          }

        Intended Result
        { 
            status:success/fail,
            message:save card

        }        
                
        
        '''
        data=payment_parser.parse_args()        
        return save_card(data)