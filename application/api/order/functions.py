from http import HTTPStatus
import ast
from datetime import datetime
import json


from flask import current_app, jsonify

from .utils import gen_ref_key
from application import db
from application import bcrypt
from application.models import (
    CustomerCard,
    CustomerTicket,
    CustomerTicketMessage,
    CustomerWallet,
    DeliveryProfile,
    DeliveryUser,
    DeliveryVehicle,
    Food,
    GroceryProductStock,
    Order,
    GroceryProduct,
    Cupon,
    OrderCupon,
    OrderFoodTaxonomy,
    OrderGrocery,
    OrderMobile,
    OrderNote,
    OrderPayment,
    OrderPaymentDetails,
    FoodTerm,
    FoodTaxonomy,
    FoodTermMap,
    OrderFood,
    PaymentProcessPricePlan,
    Feedback,
    CustomerDeliveryFeedback,
    OrderReturnGrocery,
    OrderReturn,
    SellerProfile,
    TicketCategory,
    SellerGroceryCategory,
    GroceryProductTerm,
)
from application.helpers import token_required

#################################################
##################### Grocery ###################
#################################################

#################### place order Grocery####################
##### mandatory : seller_id,datadic->products id,qty,net,gross,delivery  #####################
@token_required
def order_grocery_create(data):
    datadic = str(data.get("stringDic"))
    net_price = data.get("net")
    gross_price = data.get("gross")
    delivery_fee = data.get("delivery_fee")
    coupon_id = data.get("coupon_id")
    is_mobile = True
    longitude = data.get("longitude")
    latitude = data.get("latitude")
    seller_id = data.get("seller_id")
    pay_method = data.get("pay_method")

    result = ast.literal_eval(datadic)

    flag = True

    try:
        # Variable Declaration
        customer_id = order_grocery_create.user_id

        res = {}
        product_id = 0
        product_data = 0
        sold_price = 0  # app sold price
        sale_price = 0
        app_price = 0  # app price
        qty = 0
        subtotal = 0
        total = 0
        discount = 0
        pay_process_val = 0
        coupon_expire_msg = ""
        coupon_used_msg = ""
        backend_net_price = gross_price + delivery_fee  # backend net price
        now = datetime.now()

        ref_no = gen_ref_key(Order, "O")
        # Save Order
        new_order = Order(
            date=now,
            ref_no=ref_no,
            type="g",
            gross=gross_price,
            discount=0,  # update later
            pay_process_fee=pay_process_val,
            delivery_fee=delivery_fee,
            net=net_price,
            seller_prof=seller_id,
            is_mobile=is_mobile,
        )
        db.session.add(new_order)
        db.session.flush()

        #
        # Order id
        order_id = new_order.id
        for id, info in result.items():

            for key in info:
                # sold_price = key
                total = key
                qty = info[key]
                product_id = id

                ######## check availability #######
                available_quantity = (
                    db.session.query(GroceryProduct.id, GroceryProductStock.qty)
                    .join(
                        GroceryProductStock,
                        GroceryProductStock.product_id == GroceryProduct.id,
                    )
                    .filter(
                        GroceryProduct.id == product_id,
                        GroceryProductStock.seller_prof == seller_id,
                    )
                    .first()
                )

                available_quantity = available_quantity.qty
                # print(product_id,available_quantity,qty)
                if float(qty) > float(available_quantity):

                    flag = False
                    res = jsonify(
                        status="fail",
                        product_id=product_id,
                        message="quantity not available",
                        available_quantity=available_quantity,
                    )
                    # print("not available")

                else:

                    ###### get product price#####
                    product_data = (
                        db.session.query(GroceryProductStock)
                        .filter(
                            GroceryProductStock.product_id == product_id,
                            GroceryProductStock.seller_prof == seller_id,
                        )
                        .first()
                    )

                    sale_price = product_data.sale_price  # sale price
                    app_price = product_data.app_price

                    ##### calculate subtotal####
                    subtotal = float(app_price) * float(qty)

                    #### calculate sold price#####
                    sold_price = float(total) / float(qty)

                    ###### calculate Total#######
                    # total = float(sold_price) * float(qty)
                # print(product_id, sold_price, qty)

                ###### add To orderGrocery #####
                new_order_grocery = OrderGrocery(
                    qty=qty,
                    reg_rate=sale_price,
                    sub_unit_rate=app_price,
                    unit_rate=sold_price,
                    sub_total=subtotal,
                    total=total,
                    order_id=order_id,
                    product_id=product_id,
                )
                db.session.add(new_order_grocery)
                db.session.flush
                # print(product_id, qty,app_price, sold_price, order_id,subtotal,total)

        if flag == True:

            ###### Check if coupon available and get value  #######
            if coupon_id != "" and coupon_id != 0:
                coupon = db.session.query(Cupon).filter_by(id=coupon_id).first()
                coupon_val = coupon.value
                coupon_expire = coupon.expires_at
                coupon_is_use = coupon.is_use

                # Check coupon expired or not
                if now > coupon_expire:
                    coupon_expire_msg = "Coupon Expired"

                # Check coupon used or not
                elif coupon_is_use == True:
                    coupon_used_msg = "Coupon Already Used"

                else:

                    if "%" in coupon_val:
                        coupon_val = coupon_val.replace("%", "")
                        discount = (
                            float(net_price) * float(coupon_val)
                        ) / 100  # calculate coupon discounts
                        backend_net_price = (
                            float(backend_net_price) - discount
                        )  # calculate total net
                    else:
                        discount = coupon_val
                        backend_net_price = float(backend_net_price) - float(
                            coupon_val
                        )  # calculate total net
                    new_order.discount = discount

                    # update Coupon is_use
                    coupon.is_use = True
                    db.session.flush()

            print("hello")
            # calculate Process Fee
            if pay_method == "p":
                pay_method = "payhere"

            pay_process_fee = (
                db.session.query(PaymentProcessPricePlan)
                .filter_by(label=pay_method)
                .first()
            )
            pay_process_val = pay_process_fee.value

            if "%" in pay_process_val:
                pay_process_val = pay_process_val.replace("%", "")
                pay_process_val = (
                    float(backend_net_price) * float(pay_process_val)
                ) / 100
                net_price = float(backend_net_price) + float(
                    pay_process_val
                )  # calculate total net

            else:
                backend_net_price = float(backend_net_price) + float(
                    pay_process_val
                )  # calculate total net"""

            # print(order_id, backend_net_price)

            # add to OrderCoupon table
            if coupon_id != "" and coupon_id != 0:
                new_order_coupon = OrderCupon(
                    order_id=order_id,
                    cupon_id=coupon_id,
                )
                db.session.add(new_order_coupon)
                db.session.flush()

            # commission
            seller_grocery_cat = (
            db.session.query(
                SellerGroceryCategory.seller_prof,
                SellerGroceryCategory.cat_id,
                GroceryProductTerm.id,
                GroceryProductTerm.description,
            )
            .join(SellerGroceryCategory,SellerGroceryCategory.id==GroceryProductTerm.id)
            .filter_by(seller_prof=seller_id)
            .first()
            )

            x=json.loads(seller_grocery_cat.description)#load json
            commision=x["commission"]      


            # add to order mobile
            #
            if is_mobile == True:
                new_mobile_order = OrderMobile(
                    order_id=order_id,
                    commission=commision,
                    prep_duration=0,
                    cus_id=customer_id,
                    latitude=latitude,
                    longitude=longitude,
                )
                db.session.add(new_mobile_order)
                db.session.flush()
               

            db.session.commit()
            res = jsonify(
                status="success",
                message="Order Placed",
                order_id=order_id,
                net_price=net_price,
                coupon_expire_msg=coupon_expire_msg,
                coupon_used_msg=coupon_used_msg,
            )

    except Exception as e:
        res = jsonify(Status="Fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return res


# Grocery payment confirmation
# mandatory : seller_id,order_id
@token_required
def pay_grocery_order(data):
    seller_id = data.get("seller_id")
    order_id = data.get("order_id")
    payment_confirm = data.get("payment_confirm")
    method = data.get("pay_method")
    content = data.get("content")
    customer_id = pay_grocery_order.user_id
    res = {}

    try:
        # Get net price
        net = db.session.query(Order).filter_by(id=order_id).first()
        net = net.net
        wallet_amount = 0

        can_pay = True  # check payble or not using wallet
        message = ""

        # Get product id and qty
        order_grocery = (
            db.session.query(OrderGrocery).filter_by(order_id=order_id).all()
        )

        if payment_confirm == True and (
            method == "c" or method == "r"
        ):  # o - card payments #r-wallet
            for i in order_grocery:
                product_id = i.product_id
                qty = i.qty
                # print(product_id,qty)

                # get Grocery Stock
                stock = (
                    db.session.query(GroceryProductStock)
                    .filter(
                        GroceryProductStock.product_id == product_id,
                        GroceryProductStock.seller_prof == seller_id,
                    )
                    .first()
                )
                stock.qty = stock.qty - qty
                db.session.flush()
                # print(stock.qty)

            if method == "r":
                wallet = (
                    db.session.query(CustomerWallet)
                    .filter_by(cus_id=customer_id)
                    .first()
                )
                wallet_amount = wallet.amount

                if wallet_amount > net:
                    wallet.amount = wallet_amount - net
                    wallet.spent = wallet.spent + net
                    # wallet_amount=
                    db.session.flush()

                else:
                    can_pay = False
                    message = "wallet_insuffiecient"
                    res = jsonify(status="fail", message=message)

            if can_pay == True:
                # update Order
                order_confirm = db.session.query(Order).filter_by(id=order_id).first()
                # print(order_confirm)
                order_confirm.is_complete = True
                db.session.flush()

                # insert payments
                order_payment = OrderPayment(overdue=0, payment=net, order_id=order_id)
                db.session.add(order_payment)
                db.session.flush()
                pay_id = (
                    db.session.query(OrderPayment).filter_by(order_id=order_id).first()
                )
                pay_id = pay_id.id
                # print(pay_id)

                # insert payment details
                ref_no = gen_ref_key(OrderPaymentDetails, "PAY")
                new_payment = OrderPaymentDetails(
                    ref_no=ref_no,
                    overdue=0,
                    payment=net,
                    balance=0,
                    method=method,
                    contnet=content,
                    pay_id=pay_id,
                    is_complete=True,
                )
                db.session.add(new_payment)
                db.session.flush()
                message = "payment_succed"
                print(new_payment)
                db.session.commit()
                res = jsonify(status="success", message=message)

        elif method == "COD":
            message = "cash_pay"
            res = jsonify(status="success", message=message)
        elif payment_confirm == False:
            res = jsonify(status="Fail", message=message)

    except Exception as e:

        res = jsonify(Status="Fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return res


# Quantity Check
# Create from mandatory = seller_id,quantity,_grocery_id
# Check Quantity when adding grocery item
def add_cart(seller_id, data):
    quantity = data.get("quantity")
    grocery_id = data.get("grocery_id")
    res = {}
    try:
        # get product Name
        groceryproduct = (
            db.session.query(GroceryProduct.id, GroceryProduct.name)
            .filter_by(id=grocery_id)
            .first()
        )

        # get product price
        price = (
            db.session.query(GroceryProduct.id, GroceryProductStock.sale_price)
            .join(
                GroceryProductStock, GroceryProductStock.product_id == GroceryProduct.id
            )
            .filter(
                GroceryProduct.id == grocery_id
                and GroceryProductStock.seller_prof == seller_id
            )
            .first()
        )
        price = price.sale_price

        # Calculate Total Price
        totalPrice = float(price) * quantity

        # check availibilty of quantity
        available_quantity = (
            db.session.query(GroceryProduct.id, GroceryProductStock.qty)
            .join(
                GroceryProductStock, GroceryProductStock.product_id == GroceryProduct.id
            )
            .filter(
                GroceryProduct.id == grocery_id,
                GroceryProductStock.seller_prof == seller_id,
            )
            .first()
        )

        available_quantity = available_quantity.qty
        print(available_quantity)

        # return quantity not available
        if quantity > available_quantity:
            res = jsonify(
                status="Fail",
                message="quantity not available",
                available_quantity=available_quantity,
            )
        # return if quantity available
        else:
            res = jsonify(
                status="Success",
                message="Added to cart",
                quantity=quantity,
                item_price=price,
                total_price=totalPrice,
                name=groceryproduct.name,
            )

    except Exception as e:
        res = jsonify(Status="Fail", message="seller not available")
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


###############################################
##################### Food ###################
###############################################
# Place Food Order
@token_required
def order_food_create(data):
    try:
        net_price = data.get("net")
        gross_price = data.get("gross")
        delivery_fee = data.get("delivery_fee")
        coupon_id = data.get("coupon_id")
        longitude = data.get("longitude")
        latitude = data.get("latitude")
        seller_id = data.get("seller_id")
        pay_method = data.get("pay_method")

        food = str(data.get("food"))
        foodresult = ast.literal_eval(food)

        size = str(data.get("size"))
        addon = str(data.get("addon"))

        # Variable Declaration
        customer_id = order_food_create.user_id

        is_mobile = True
        res = {}
        flag = True  # can place order if flag is true
        food_id = 0
        qty = 0  # food qty
        f_subtotal = 0  # food subtotal
        f_total = 0  # food total
        discount = 0
        sale_price = 0  # food sale price
        sold_price = 0  # food sold price
        app_price = 0  # food app price
        size_sold_price = 0  # size sold price
        s_food_id = 0  # size food id
        s_total = 0  # Size Total
        s_subtotal = 0  # size Sub total
        coupon_expire_msg = ""
        coupon_used_msg = ""
        backend_net_price = gross_price + delivery_fee  # backend net price
        pay_process_val = 0
        state = True

        ref_no = gen_ref_key(Order, "O")

        ################# Save Order ######################
        new_order = Order(
            ref_no=ref_no,
            type="f",
            gross=gross_price,
            discount=0,
            pay_process_fee=pay_process_val,
            delivery_fee=delivery_fee,
            net=net_price,
            seller_prof=seller_id,
            is_mobile=is_mobile,
        )
        db.session.add(new_order)
        db.session.flush()
        # print(new_order)

        ord_id = new_order.id
        # print(ord_id)

        ######## Get food prices #############
        for id, info in foodresult.items():

            for key in info:
                f_total = key
                qty = info[key]
                food_id = id
                food_data = (
                    db.session.query(Food)
                    .filter(Food.id == food_id, Food.seller_prof == seller_id)
                    .first()
                )
                state = food_data.state

                # Check State
                if state == 0:
                    flag = False
                elif state == 1:
                    flag = True
                # print(state,flag)

                sale_price = food_data.sale_price
                app_price = food_data.app_price

                ##### calculate food sub total ####
                f_subtotal = float(app_price) * float(qty)

                ##### calculate sold price #######
                sold_price = float(f_total) / float(qty)

                ###### calculate Total#######
                # f_total = float(sold_price) * float(qty)

            ###### add To orderFood #####
            new_order_food = OrderFood(
                qty=qty,
                reg_rate=sale_price,
                sub_unit_rate=app_price,
                unit_rate=sold_price,
                sub_total=f_subtotal,
                total=f_total,
                order_id=ord_id,
                food_id=food_id,
            )
            db.session.add(new_order_food)
            db.session.flush
            # print(new_order_food.id)

        ########## food size prices #############
        if size != "":
            sizeresult = ast.literal_eval(size)
            for id2, info2 in sizeresult.items():
                for key2 in info2:
                    s_food_id = key2
                    s_total = info2[key2]
                size_id = id2

                #################################
                ##### Get SizePrice   ############
                ###################################

                # Check Whether the Food is with a Size or not , then proceed  with size

                size_price = (
                    db.session.query(
                        FoodTerm.id,
                        FoodTerm.description,
                        FoodTaxonomy.parent_id,
                        FoodTermMap.food_id,
                    )
                    .join(FoodTaxonomy, FoodTaxonomy.term_id == FoodTerm.id)
                    .join(FoodTermMap, FoodTermMap.term_id == FoodTerm.id)
                    .filter(
                        FoodTermMap.food_id == s_food_id,
                        FoodTaxonomy.taxonomy == "size-price",
                        FoodTerm.id == size_id,
                    )
                    .first()
                )

                size_sale_price = size_price.description["sale_price"]
                size_app_price = size_price.description["app_price"]
                print(size_app_price)

                # Get qty from order food to update according to  size
                qty2 = (
                    db.session.query(OrderFood)
                    .filter(
                        OrderFood.food_id == s_food_id, OrderFood.order_id == ord_id
                    )
                    .first()
                )
                qty2 = qty2.qty

                ##### calculate size sub total ####
                s_subtotal = float(size_app_price) * float(qty2)

                # calculate size sold price####
                size_sold_price = float(s_total) / float(qty2)

                ###### calculate size Total#######
                # s_total = float(size_sold_price) * float(qty2)

                # Assign to food total
                f_subtotal = s_subtotal
                f_total = s_total
                # print(ord_id)

                #######################################
                ## update Order Food according to size #######
                # #####################################
                o_id = (
                    db.session.query(OrderFood)
                    .filter(
                        OrderFood.food_id == s_food_id, OrderFood.order_id == ord_id
                    )
                    .first()
                )

                o_id.reg_rate = size_sale_price
                o_id.sub_unit_rate = size_app_price
                o_id.unit_rate = size_sold_price
                o_id.sub_total = f_subtotal
                o_id.total = f_total
                db.session.flush()

                print(o_id.id)

                # Content in Taxonomy
                content = {}
                content = {"app_price": size_app_price, "sale_price": size_sold_price}
                # print(content)

                #######################################
                ## Create new order Food Size Taxonomy#######
                # #####################################
                new_order_food_tax = OrderFoodTaxonomy(
                    taxonomy="size",
                    content=content,
                    food_order_id=o_id.id,
                    term_id=size_id,
                )

                db.session.add(new_order_food_tax)
                db.session.flush()

                # print(new_order_food_tax)

        ######### food addon prices #############
        if addon != "":
            addonresult = ast.literal_eval(addon)
            ########## Get food addon prices #############
            for id3, info3 in addonresult.items():

                for key3 in info3:
                    food_id = key3
                    a_qty = info3[key3]

                addon_id = id3
                print(addon_id, qty, food_id)  #

                #  Get Addon Price #
                #####################
                addon_price = (
                    db.session.query(
                        FoodTerm.id,
                        FoodTerm.description,
                        FoodTermMap.food_id,
                    )
                    .join(FoodTaxonomy, FoodTaxonomy.term_id == FoodTerm.id)
                    .join(FoodTermMap, FoodTermMap.term_id == FoodTerm.id)
                    .filter(
                        FoodTermMap.food_id == food_id,
                        FoodTaxonomy.taxonomy == "addon",
                        FoodTerm.id == addon_id,
                    )
                    .first()
                )
                addon_price = addon_price.description["price"]

                ####### calculate addon Total#######
                a_total = float(addon_price) * float(a_qty)

                # Assign to food total
                f_subtotal = float(f_subtotal) + float(a_total)
                f_total = float(f_total) + float(a_total)

                #######################################
                ## update Order Food according to addon#######
                # #####################################

                o_id = (
                    db.session.query(OrderFood)
                    .filter(OrderFood.food_id == food_id, OrderFood.order_id == ord_id)
                    .first()
                )
                o_id.sub_total = f_subtotal
                o_id.total = f_total
                db.session.flush()

                content = {}
                content = {"qty": a_qty, "price": addon_price, "total": a_total}

                #######################################
                ## Create new order Food addon Taxonomy#######
                # #####################################
                new_order_food_tax = OrderFoodTaxonomy(
                    taxonomy="addon",
                    content=content,
                    food_order_id=o_id.id,
                    term_id=addon_id,
                )

                db.session.add(new_order_food_tax)
                db.session.flush()
                print(new_order_food_tax)

        if flag == True:  # State is 1 and Seller available

            ###### Check if coupon available and get value  #######
            if coupon_id != "" and coupon_id != 0:
                coupon = db.session.query(Cupon).filter_by(id=coupon_id).first()
                coupon_val = coupon.value
                coupon_expire = coupon.expires_at
                coupon_is_use = coupon.is_use
                now = datetime.now()

                # Check coupon expired or not
                if now > coupon_expire:
                    coupon_expire_msg = "Coupon Expired"

                # Check coupon used or not
                elif coupon_is_use == True:
                    coupon_used_msg = "Coupon Already Used"

                else:

                    if "%" in coupon_val:
                        coupon_val = coupon_val.replace("%", "")
                        discount = (
                            float(backend_net_price) * float(coupon_val)
                        ) / 100  # calculate coupon discounts
                        backend_net_price = (
                            float(backend_net_price) - discount
                        )  # calculate total net
                    else:
                        discount = coupon_val
                        net_price = float(backend_net_price) - float(
                            coupon_val
                        )  # calculate total net

                    # update Coupon is_use
                    coupon.is_use = True
                    new_order.discount = discount
                    db.session.flush()

            # calculate Process Fee
            if pay_method == "p":
                pay_method = "payhere"

            pay_process_fee = (
                db.session.query(PaymentProcessPricePlan)
                .filter_by(label=pay_method)
                .first()
            )
            pay_process_val = pay_process_fee.value
            print(pay_process_val)

            if "%" in pay_process_val:
                pay_process_val = pay_process_val.replace("%", "")
                pay_process_val = (
                    float(backend_net_price) * float(pay_process_val)
                ) / 100
                net_price = float(backend_net_price) + float(
                    pay_process_val
                )  # calculate total net

            else:
                net_price = float(backend_net_price) + float(
                    pay_process_val
                )  # calculate total net

            # add to OrderCoupon table
            if coupon_id != "" and coupon_id != 0:
                new_order_coupon = OrderCupon(
                    order_id=ord_id,
                    cupon_id=coupon_id,
                )
                db.session.add(new_order_coupon)
                db.session.flush()

            # add to order mobile
            #
            if is_mobile == True:
                new_mobile_order = OrderMobile(
                    order_id=ord_id,
                    cus_id=customer_id,
                    latitude=latitude,
                    longitude=longitude,
                )
                db.session.add(new_mobile_order)
                db.session.flush()

            db.session.commit()

            res = jsonify(
                status="success",
                message="Order Placed",
                order_id=ord_id,
                net_price=net_price,
                coupon_expire_msg=coupon_expire_msg,
                coupon_used_msg=coupon_used_msg,
            )

        else:
            res = jsonify(
                status="fail",
                message="Seller not available at this time",
            )

    except Exception as e:
        res = jsonify(Status="Fail", message=str(e))
        print(e)
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# payment confirmation
# mandatory : seller_id,order_id
@token_required
def pay_food_order(data):
    order_id = data.get("order_id")
    payment_confirm = data.get("payment_confirm")
    method = data.get("pay_method")
    content = data.get("content")
    customer_id = pay_food_order.user_id
    can_pay = True

    try:
        # Get net price
        net = db.session.query(Order).filter_by(id=order_id).first()
        net = net.net
        print(net)

        if payment_confirm == True and (method == "c" or method == "r"):
            wallet = (
                db.session.query(CustomerWallet).filter_by(cus_id=customer_id).first()
            )
            wallet_amount = wallet.amount

            if wallet_amount > net:
                wallet.amount = wallet_amount - net
                wallet.spent = wallet.spent + net
                # wallet_amount=
                db.session.flush()

            else:
                can_pay = False
                message = "wallet_insuffiecient"
                res = jsonify(status="fail", message=message)

            if can_pay == True:
                # update Order
                order_confirm = db.session.query(Order).filter_by(id=order_id).first()
                # print(order_confirm)
                order_confirm.is_complete = True
                db.session.flush()

                # insert payments
                order_payment = OrderPayment(overdue=0, payment=net, order_id=order_id)
                db.session.add(order_payment)
                db.session.flush()
                pay_id = (
                    db.session.query(OrderPayment).filter_by(order_id=order_id).first()
                )
                pay_id = pay_id.id
                # print(pay_id)

                # insert payment details
                ref_no = gen_ref_key(OrderPaymentDetails, "PAY")
                new_payment = OrderPaymentDetails(
                    ref_no=ref_no,
                    overdue=0,
                    payment=net,
                    balance=0,
                    method=method,
                    contnet=content,
                    pay_id=pay_id,
                    is_complete=True,
                )
                db.session.add(new_payment)
                db.session.flush()
                message = "payment_succed"
            print(new_payment)
            # db.session.commit()
            res = jsonify(status="success", message=message)

        # CASH ON DELIVERY
        elif method == "COD":
            message = "cash_pay"
            res = jsonify(status="success", message=message)

        elif payment_confirm == False:
            res = jsonify(status="Fail", message=message)

    except Exception as e:
        res = jsonify(Status="Fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return res


# Order Return
@token_required
def return_order(data):
    try:
        order_id = data.get("order_id")
        product_data = str(data.get("product_data"))
        return_note = data.get("return_note")
        result = ast.literal_eval(product_data)
        ref_no = gen_ref_key(OrderReturn, "OR")  # order return reference number
        now = datetime.now()

        gro_order_id = 0

        # add to order return
        new_order_return = OrderReturn(
            ref_no=ref_no, date=now, note=return_note, order_id=order_id
        )
        db.session.add(new_order_return)
        db.session.flush()
        return_id = new_order_return.id

        for id, info in result.items():

            for key in info:
                qty = info[key]
                pro_id = key

                gro_order_id = (
                    db.session.query(OrderGrocery.id)
                    .filter(
                        OrderGrocery.product_id == pro_id,
                        OrderGrocery.order_id == order_id,
                    )
                    .first()
                )
                print(gro_order_id.id)

            # add to order grocery return
            new_return_grocery = OrderReturnGrocery(
                qty=qty, return_id=return_id, grocery_order_id=gro_order_id.id
            )
            db.session.add(new_return_grocery)
            db.session.flush()

        db.session.commit()

        res = jsonify(status="success", message="Order Return successfully")
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# Order Cancel
@token_required
def cancel_order(data):
    try:
        ord_id = data.get("order_id")
        type = data.get("type")  # food or grocery f/g
        cancel_note = data.get("cancel_note")
        pro_id = 0
        qty = 0
        seller_id = 0

        order_status = db.session.query(OrderMobile).filter_by(order_id=ord_id).first()
        order_details = db.session.query(Order).filter_by(id=ord_id).first()
        seller_id = order_details.seller_prof
        print(seller_id)
        order_payment = db.session.query(OrderPayment).filter_by(id=ord_id).first()
        payment_id = order_payment.id
        order_payment_details = (
            db.session.query(OrderPaymentDetails).filter_by(id=payment_id).first()
        )
        # print(payment_id)

        # cancel order before pick
        if (
            order_status.is_pick == False
            and order_status.is_ship == False
            and order_status.is_deliver == False
            and order_status.is_recive == False
            and order_status.is_ready == False
        ):
            print("Can be Cancelled")
            # update order
            order_details.is_complete = False
            order_details.is_cancel = True

            # update orderpayment details
            order_payment_details.contnet = cancel_note
            order_payment_details.is_complete = False
            order_payment_details.is_cancel = True

            # add OrderNote
            order_note = OrderNote(content=cancel_note, order_id=ord_id)
            db.session.add(order_note)
            db.session.flush()

            # if type is grocery reduce quantities
            if type == "g":
                # update grocery stock for cancel products
                order_cancel = (
                    db.session.query(
                        OrderGrocery.id, OrderGrocery.qty, OrderGrocery.product_id
                    )
                    .filter_by(order_id=ord_id)
                    .all()
                )

                for i in order_cancel:
                    pro_id = i.product_id
                    qty = i.qty
                    # print(pro_id,qty)

                    grocery_stock = (
                        db.session.query(GroceryProductStock)
                        .filter(
                            GroceryProductStock.seller_prof == seller_id,
                            GroceryProductStock.product_id == pro_id,
                        )
                        .first()
                    )
                    print(grocery_stock.product_id)
                    grocery_stock.qty = grocery_stock.qty + qty
                    db.session.flush()

            db.session.commit()

        res = jsonify(status="success", message="order cancelled")
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# All Grocery Orders
@token_required
def grocery_orders():
    try:
        customer_id = grocery_orders.user_id
        res = []
        orders = (
            db.session.query(
                Order.id,
                Order.type,
                Order.is_complete,
                Order.is_cancel,
                Order.seller_prof,
                Order.date,
                Order.net,
                OrderMobile.is_accept,
                OrderMobile.is_reject,
                OrderMobile.is_recive,
                OrderMobile.is_ready,
                SellerProfile.organization,
                SellerProfile.street_address,
            )
            .join(SellerProfile, SellerProfile.id == Order.seller_prof)
            .join(OrderMobile, OrderMobile.order_id == Order.id)
            .filter(OrderMobile.cus_id == customer_id, Order.type == "g")
            .all()
        )

        # print(orders)
        for i in orders:

            # order State

            is_complete = i.is_complete
            is_cancel = i.is_cancel
            is_accept = i.is_accept
            is_reject = i.is_reject
            is_receive = i.is_recive
            is_ready = i.is_ready

            if is_complete == True:
                state = "complete"
            elif is_cancel == True:
                state = "cancel"
            elif is_accept == True:
                state = "accept"
            elif is_reject == True:
                state = "reject"
            elif is_ready == True:
                state = "ready"
            elif is_receive == True:
                state = "receive"
            else:
                state = "pending"

            info = {
                "order_id": i.id,
                "state": state,
                "seller_name": i.organization,
                "street_address": i.street_address,
                "Order_date": i.date.strftime("%y-%m-%d"),
                "net": i.net,
            }
            res.append(info)

        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# All Grocery Orders
@token_required
def food_orders():
    try:
        customer_id = food_orders.user_id
        res = []
        orders = (
            db.session.query(
                Order.id,
                Order.is_complete,
                Order.is_cancel,
                Order.seller_prof,
                Order.date,
                Order.net,
                OrderMobile.is_accept,
                OrderMobile.is_reject,
                OrderMobile.is_recive,
                OrderMobile.is_ready,
                SellerProfile.organization,
                SellerProfile.street_address,
            )
            .join(SellerProfile, SellerProfile.id == Order.seller_prof)
            .join(OrderMobile, OrderMobile.order_id == Order.id)
            .filter(OrderMobile.cus_id == customer_id, Order.type == "f")
            .all()
        )

        # print(orders)
        for i in orders:
            # order State

            is_complete = i.is_complete
            is_cancel = i.is_cancel
            is_accept = i.is_accept
            is_reject = i.is_reject
            is_receive = i.is_recive
            is_ready = i.is_ready

            if is_complete == True:
                state = "complete"
            elif is_cancel == True:
                state = "cancel"
            elif is_accept == True:
                state = "accept"
            elif is_reject == True:
                state = "reject"
            elif is_ready == True:
                state = "ready"
            elif is_receive == True:
                state = "receive"
            else:
                state = "pending"

            info = {
                "order_id": i.id,
                "state": state,
                "seller_name": i.organization,
                "street_address": i.street_address,
                "Order_date": i.date.strftime("%y-%m-%d"),
                "net": i.net,
            }
            res.append(info)

        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# Per Order Status
@token_required
def grocery_order_details(order_id):
    try:
        deliverer_ref = None
        vehicle_type = None
        vechicle_reg_no = None

        res = []
        res2 = {}
        # get order details
        order = (
            db.session.query(
                Order.id,
                Order.is_complete,
                Order.is_cancel,
                Order.seller_prof,
                Order.date,
                Order.net,
                OrderMobile.is_accept,
                OrderMobile.is_reject,
                OrderMobile.is_recive,
                OrderMobile.is_ready,
                OrderMobile.deliverer_id,
                OrderMobile.latitude,
                OrderMobile.longitude,
                SellerProfile.seller_id,
                SellerProfile.ref_no.label("seller_ref_no"),
                SellerProfile.organization,
                SellerProfile.street_address,
                SellerProfile.contact_no,
                SellerProfile.latitude.label("seller_latitude"),
                SellerProfile.longitude.label("seller_longitude"),
            )
            .join(SellerProfile, SellerProfile.id == Order.seller_prof)
            .join(OrderMobile, OrderMobile.order_id == Order.id)
            .filter(Order.id == order_id)
            .first()
        )

        deliver_id = order.deliverer_id
        # print(deliver_id)
        # deliverer details
        if deliver_id != None:
            print("h")
            deliverer = (
                db.session.query(
                    DeliveryUser.id,
                    DeliveryProfile.ref_no,
                    DeliveryVehicle.type,
                    DeliveryVehicle.reg_no,
                ).join(DeliveryProfile, DeliveryProfile.deliverer_id == DeliveryUser.id)
                # .join(DeliveryVehicle,DeliveryVehicle.deliverer_id==DeliveryUser.id)
                .filter(DeliveryUser.id == deliver_id)
            ).first()
            deliverer_ref = deliverer.ref_no
            vechicle_reg_no = deliverer.reg_no
            vehicle_type = deliverer.type
            print(deliverer_ref)

        # get order_grocery details
        order_grocery = (
            db.session.query(
                OrderGrocery.qty,
                OrderGrocery.total,
                OrderGrocery.product_id,
                GroceryProduct.name,
            )
            .join(GroceryProduct, GroceryProduct.id == OrderGrocery.product_id)
            .filter(OrderGrocery.order_id == order_id)
            .all()
        )

        is_complete = order.is_complete
        print(is_complete)
        is_cancel = order.is_cancel
        is_accept = order.is_accept
        is_reject = order.is_reject
        is_receive = order.is_recive
        is_ready = order.is_ready

        if is_complete == True:
            state = "complete"
        elif is_cancel == True:
            state = "cancel"
        elif is_accept == True:
            state = "accept"
        elif is_reject == True:
            state = "reject"
        elif is_ready == True:
            state = "ready"
        elif is_receive == True:
            state = "receive"
        else:
            state = "pending"

        for i in order_grocery:

            info = {"product_name": i.name, "qty": i.qty, "Total": i.total}
            res.append(info)
        print(vechicle_reg_no)
        res2 = {
            "net_price": order.net,
            "state": state,
            "order_date": order.date.strftime("%y-%m-%d"),
            "seller_id": order.seller_prof,
            "seller_ref_no": order.seller_ref_no,
            "seller_contact_no": order.contact_no,
            "seller_latitude": order.seller_latitude,
            "seller_longitude": order.seller_longitude,
            "seller_organization": order.organization,
            "seller_address": order.street_address,
            "order_latitude": order.latitude,
            "order_longitude": order.longitude,
            "deliverer_ref_no": deliverer_ref,
            "vehicle_type": vehicle_type,
            "vehicle_no": vechicle_reg_no,
        }

        res.append(res2)
        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# Per Order Status
@token_required
def food_order_details(order_id):
    try:
        res = []
        res2 = {}
        deliverer_ref = None
        vehicle_type = None
        vechicle_reg_no = None
        # get order details
        order = (
            db.session.query(
                Order.id,
                Order.is_complete,
                Order.is_cancel,
                Order.seller_prof,
                Order.date,
                Order.net,
                OrderMobile.is_accept,
                OrderMobile.is_reject,
                OrderMobile.is_recive,
                OrderMobile.is_ready,
                OrderMobile.deliverer_id,
                OrderMobile.latitude,
                OrderMobile.longitude,
                SellerProfile.seller_id,
                SellerProfile.ref_no.label("seller_ref_no"),
                SellerProfile.organization,
                SellerProfile.street_address,
                SellerProfile.contact_no,
                SellerProfile.latitude.label("seller_latitude"),
                SellerProfile.longitude.label("seller_longitude"),
            )
            .join(SellerProfile, SellerProfile.id == Order.seller_prof)
            .join(OrderMobile, OrderMobile.order_id == Order.id)
            .filter(Order.id == order_id)
            .first()
        )

        deliver_id = order.deliverer_id
        print(deliver_id)
        # deliverer details
        if deliver_id != None:
            print("h")
            deliverer = (
                db.session.query(
                    DeliveryUser.id,
                    DeliveryProfile.ref_no,
                    DeliveryVehicle.type,
                    DeliveryVehicle.reg_no,
                ).join(DeliveryProfile, DeliveryProfile.deliverer_id == DeliveryUser.id)
                # .join(DeliveryVehicle,DeliveryVehicle.deliverer_id==DeliveryUser.id)
                .filter(DeliveryUser.id == deliver_id)
            ).first()
            deliverer_ref = deliverer.ref_no
            vechicle_reg_no = deliverer.reg_no
            vehicle_type = deliverer.type
            print(deliverer_ref)

        is_complete = order.is_complete
        is_cancel = order.is_cancel
        is_accept = order.is_accept
        is_reject = order.is_reject
        is_receive = order.is_recive
        is_ready = order.is_ready

        if is_complete == True:
            state = "complete"
        elif is_cancel == True:
            state = "cancel"
        elif is_accept == True:
            state = "accept"
        elif is_reject == True:
            state = "reject"
        elif is_ready == True:
            state = "ready"
        elif is_receive == True:
            state = "receive"
        else:
            state = "pending"

        # get order_food details
        order_Food = (
            db.session.query(
                OrderFood.id,
                OrderFood.qty,
                OrderFood.total,
                OrderFood.food_id,
                Food.name,
            )
            .join(Food, Food.id == OrderFood.food_id)
            .filter(OrderFood.order_id == order_id)
            .all()
        )

        for i in order_Food:
            info = {"food_name": i.name, "qty": i.qty, "Total": i.total}
            res.append(info)
            #    print(i.id)

            order_Food_tax = (
                db.session.query(
                    OrderFoodTaxonomy.taxonomy,
                    OrderFoodTaxonomy.content,
                    FoodTaxonomy.description,
                    OrderFoodTaxonomy.food_order_id,
                )
                .join(FoodTaxonomy, FoodTaxonomy.term_id == OrderFoodTaxonomy.term_id)
                .filter(
                    OrderFoodTaxonomy.food_order_id == i.id,
                    OrderFoodTaxonomy.taxonomy == "addon",
                )
                .all()
            )

        for i in order_Food_tax:
            info2 = {"addon_price": i.content["price"], "addon_qty": i.content["qty"]}
            res.append(info2)

        res2 = {
            "net_price": order.net,
            "state": state,
            "order_date": order.date.strftime("%y-%m-%d"),
            "seller_id": order.seller_prof,
            "seller_ref_no": order.seller_ref_no,
            "seller_contact_no": order.contact_no,
            "seller_latitude": order.seller_latitude,
            "seller_longitude": order.seller_longitude,
            "seller_organization": order.organization,
            "seller_address": order.street_address,
            "order_latitude": order.latitude,
            "order_longitude": order.longitude,
            "deliverer_ref_no": deliverer_ref,
            "vehicle_type": vehicle_type,
            "vehicle_no": vechicle_reg_no,
        }

        res.append(res2)
        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# Review Create customer_Delivery
# Create from mandatory = rate
# review,order_id
@token_required
def review_create(deliver_id, data):
    rate = data.get("rate")
    review = data.get("review")
    order_id = data.get("order_id")
    customer_id = review_create.user_id
    if order_id == 0:
        order_id = None

    res = {}

    try:
        new_feedback = Feedback(rate=rate, review=review, order_id=order_id)
        db.session.add(new_feedback)
        db.session.flush()
        feedback_id = new_feedback.id
        new_customer_deliver = CustomerDeliveryFeedback(
            feedback_id=feedback_id, cus_id=customer_id, deliverer_id=deliver_id
        )
        db.session.add(new_customer_deliver)
        db.session.commit()

        res = jsonify(status="success", message="review created")
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# Customer Ticket
@token_required
def customer_ticket(data):
    try:

        ticket_category_id = data.get("ticket_category_id")
        customer_text = data.get("customer_text")
        customer_id = customer_ticket.user_id

        ref_no = gen_ref_key(CustomerTicket, "CT")
        now = datetime.now()
        res = {}

        # new Ticket
        ticket = CustomerTicket(
            ref_no=ref_no,
            date=now,
            is_open=True,
            cat_id=ticket_category_id,
            cus_id=customer_id,
        )
        db.session.add(ticket)
        db.session.flush()

        # new Customer Ticket Message
        new_cus_message = CustomerTicketMessage(
            customer_text=customer_text, ticket_id=ticket.id
        )
        db.session.add(new_cus_message)
        db.session.commit()

        res = jsonify(status="success", message="Ticket added")
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return res


# Customer Ticket
@token_required
def save_card(data):
    try:
        bank_number = str(data.get("bank_number"))
        type = data.get("type")
        card_number = str(data.get("card_number"))
        expire = data.get("expire")
        cvv = str(data.get("cvv"))
        holder = data.get("holder")

        customer_id = save_card.user_id

        # Bcrypt card details
        bank_number = bcrypt.generate_password_hash(bank_number)
        card_number = bcrypt.generate_password_hash(card_number)
        cvv = bcrypt.generate_password_hash(cvv)

        new_card = CustomerCard(
            bank_name=bank_number,
            type=type,
            card_no=card_number,
            cvv=cvv,
            holder=holder,
            expires_at=expire,
            cus_id=customer_id,
        )
        db.session.add(new_card)
        db.session.commit()

        res = jsonify(status="success", message="Card details saved")
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# All return Orders
@token_required
def return_list():
    try:
        customer_id = return_list.user_id
        res = []

        return_orders = (
            db.session.query(OrderReturn)
            .join(Order, Order.id == OrderReturn.order_id)
            .join(OrderMobile, OrderMobile.order_id == Order.id)
            .filter(OrderMobile.cus_id == customer_id)
            .all()
        )

        for i in return_orders:
            is_complete = i.is_complete
            if is_complete == True:
                is_complete = "complete"
            else:
                is_complete = ""

            info = {
                "return_id": i.id,
                "ref_no": i.ref_no,
                "date": i.date.strftime("%y-%m-%d"),
                "is_complete": is_complete,
            }
            res.append(info)

        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# one return order details
@token_required
def return_details(ret_id):
    try:

        customer_id = return_details.user_id
        res = []
        # roduct_details=0
        state = ""

        return_orders = (
            db.session.query(
                OrderReturn,
                Order.id.label("order_id"),
                OrderMobile.cus_id.label("cus_id"),
            )
            .join(Order, Order.id == OrderReturn.order_id)
            .join(OrderMobile, OrderMobile.order_id == Order.id)
            .filter(OrderMobile.cus_id == customer_id, OrderReturn.id == ret_id)
            .first()
        )

        # print(return_orders)
        if return_orders:
            i = return_orders
            is_complete = i.OrderReturn.is_complete
            is_cancel = i.OrderReturn.is_cancel
            is_accept = i.OrderReturn.is_accept
            is_reject = i.OrderReturn.is_reject

            state = "pending"
            if is_complete == True:
                state = "complete"
            elif is_cancel == True:
                state = "cancel"
            elif is_accept == True:
                state = "accept"
            elif is_reject == True:
                state = "reject"

            info = {
                "return_id": i.OrderReturn.id,
                "ref_no": i.OrderReturn.ref_no,
                "date": i.OrderReturn.date.strftime("%y-%m-%d"),
                "state": state,
                "note": i.OrderReturn.note,
            }
            res.append(info)

            product_details = (
                db.session.query(
                    OrderReturnGrocery.grocery_order_id,
                    OrderReturnGrocery.qty,
                    GroceryProduct.name,
                )
                .join(
                    OrderGrocery, OrderGrocery.id == OrderReturnGrocery.grocery_order_id
                )
                .join(GroceryProduct, GroceryProduct.id == OrderGrocery.product_id)
                .filter(OrderReturnGrocery.return_id == ret_id)
                .all()
            )
            # print(product_details)
            for x in product_details:
                info2 = {
                    "grocery_order_id": x.grocery_order_id,
                    "qty": x.qty,
                    "product_name": x.name,
                }
                res.append(info2)
        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# available coupons
"""@token_required
def get_available_coupons():
    coupons = (
        db.session.query(Cupon.id, Cupon.ref_no, Cupon.value, Cupon.expires_at)
        .filter(Cupon.is_use == False)
        .all()
    )
    res = []

    try:

        for i in coupons:
            info = {
                "coupon_id": i.id,
                "ref_no": i.ref_no,
                "value": i.value,
                "expires_at": i.expires_at.strftime("%y-%m-%d"),
            }
            print(info)
            res.append(info)

        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res
"""


@token_required
def get_coupon_details(coupon_ref):
    coupons = (
        db.session.query(
            Cupon.id, Cupon.ref_no, Cupon.value, Cupon.expires_at, Cupon.is_use
        )
        .filter(Cupon.ref_no == coupon_ref)
        .first()
    )
    is_use = ""    

    try:
        i = coupons
        coupon_val=i.value
        type=""

        if i.is_use == True:
            is_use = "used"
        else:
            is_use = "available"

        if "%" in coupon_val:
            type="percent"
            coupon_val = coupon_val.replace("%", "")
        
        else:
            type="rate"

        info = {
            "coupon_id": i.id,
            "ref_no": i.ref_no,
            "value": coupon_val,
            "value_type":type,
            "expires_at": i.expires_at.strftime("%y-%m-%d"),
            "is_use": is_use,
        }

        res = jsonify(info)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


@token_required
def get_ticket_categories():
    ticket = db.session.query(
        TicketCategory.id, TicketCategory.user_type, TicketCategory.term
    ).all()
    res = []

    try:

        for i in ticket:
            info = {
                "ticket_id": i.id,
                "user_type": i.user_type,
                "term": i.term,
            }

            res.append(info)

        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# change state
def changestate(or_id):
    try:
        res = {}
        order = db.session.query(OrderMobile).filter_by(order_id=or_id).first()
        order.is_recive = True
        db.session.commit()
        print(order.is_recive)
        res = {"status": "Success", "message": "order_received"}
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res
