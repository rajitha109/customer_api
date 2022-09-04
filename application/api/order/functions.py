from http import HTTPStatus
import ast
from datetime import datetime


from flask import current_app, jsonify

from .utils import gen_ref_key, gen_order_id
from application import db
from application import bcrypt
from application.models import (
    CustomerCard,
    CustomerRefund,
    CustomerTicket,
    CustomerTicketMessage,
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
    SellerProfile
)
from application.helpers import token_required

#################################################
##################### Grocery ###################
#################################################

#################### place order Grocery####################
##### mandatory : seller_id,datadic->products id,qty,net,gross,delivery  #####################
@token_required
def place_order(seller_id, data):
    datadic = str(data.get("stringDic"))
    net_price = data.get("net")
    gross_price = data.get("gross")
    delivery_fee = data.get("delivery_fee")
    coupon_id = data.get("coupon_id")
    is_mobile = data.get("is_mobile")
    longitude = data.get("longitude")
    latitude = data.get("latitude")
    customer_id = data.get("customer_id")
    payment_plan_id = data.get("payment_plan_id")

    result = ast.literal_eval(datadic)

    flag = True

    try:
        # Variable Declaration
        res = {}
        product_id = 0
        sold_price = 0
        qty = 0
        subtotal = 0
        total = 0
        discount = 0
        pay_process_val = 0
        reg_price = 0
        sale_price = 0
        coupon_expire_msg = ""
        coupon_used_msg = ""
        now = datetime.now()

        #
        #  genereate Order id
        order_id = gen_order_id(Order)

        for id, info in result.items():
           

            for key in info:
                sold_price = key
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
                        status="Fail",
                        product_id=product_id,
                        message="quantity not available",
                        available_quantity=available_quantity,
                    )
                    # print("not available")

                else:

                    ###### get product price#####
                    sale_price = (
                        db.session.query(GroceryProductStock)
                        .filter(
                            GroceryProductStock.product_id == product_id
                            and GroceryProductStock.seller_prof == seller_id
                        )
                        .first()
                    )

                    reg_price = sale_price.regular_price
                    sale_price = sale_price.sale_price

                    ##### calculate subtotal####
                    subtotal = float(sale_price) * float(qty)

                    ###### calculate Total#######
                    total = float(sold_price) * float(qty)
                # print(product_id, sold_price, qty)

                ###### add To orderGrocery #####
                new_order_grocery = OrderGrocery(
                    qty=qty,
                    reg_rate=reg_price,
                    sub_unit_rate=sale_price,
                    unit_rate=sold_price,
                    sub_total=subtotal,
                    total=total,
                    order_id=order_id,
                    product_id=product_id,
                )
                db.session.add(new_order_grocery)
                db.session.flush
                # print(product_id, qty, sold_price, order_id,subtotal,total)

                

        if flag == True:

            ref_no = gen_ref_key(Order, "O")

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
                        discount = (float(net_price) * float(coupon_val)) / 100 #calculate coupon discounts
                        net_price = float(net_price) - discount  # calculate total net
                    else:
                        discount = coupon_val
                        net_price = float(net_price) - float(coupon_val)  # calculate total net

                    # update Coupon is_use
                    coupon.is_use = True
                    db.session.flush()

            # print(ref_no, is_mobile,latitude,longitude)
            #print(gross_price, net_price, delivery_fee, coupon_id, discount)

            # calculate Process Fee
            pay_process_fee = (
                db.session.query(PaymentProcessPricePlan)
                .filter_by(id=payment_plan_id)
                .first()
            )
            pay_process_val = pay_process_fee.value

            if "%" in pay_process_val:
                pay_process_val = pay_process_val.replace("%", "")
                pay_process_val = (float(net_price) * float(pay_process_val)) / 100
                net_price = float(net_price) + float( pay_process_val )  # calculate total net
            
            else:
                net_price = float(net_price) + float(  pay_process_val )  # calculate total net

            print(order_id, net_price)

            # Save Order
            new_order = Order(
                id=order_id,
                date=now,
                ref_no=ref_no,
                type="g",
                gross=gross_price,
                discount=discount,
                pay_process_fee=pay_process_val,
                delivery_fee=delivery_fee,
                net=net_price,
                seller_prof=seller_id,
                is_mobile=is_mobile,
            )
            db.session.add(new_order)
            db.session.flush()

            """order_id = (
                db.session.query(Order).filter_by(ref_no=ref_no).first()
            )  # order ref no generate
            order_id = order_id.id"""

            # add to OrderCoupon table
            if coupon_id != "" and coupon_id != 0:
                new_order_coupon = OrderCupon(
                    order_id=order_id,
                    cupon_id=coupon_id,
                )
                db.session.add(new_order_coupon)
                db.session.flush()

            # add to order mobile
            #
            if is_mobile == True:
                new_mobile_order = OrderMobile(
                    order_id=order_id,
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
def pay_order(seller_id, data):
    order_id = data.get("order_id")
    payment_confirm = data.get("payment_confirm")
    method = data.get("pay_method")
    content = data.get("content")
    

    try:
        # Get net price
        net = db.session.query(Order).filter_by(id=order_id).first()
        net = net.net

        # Get product id and qty
        order_grocery = (
            db.session.query(OrderGrocery).filter_by(order_id=order_id).all()
        )

        if payment_confirm == True and method == "o":
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

            # update Order
            order_confirm = db.session.query(Order).filter_by(id=order_id).first()
            # print(order_confirm)
            order_confirm.is_complete = True
            db.session.flush()

            # insert payments
            order_payment = OrderPayment(overdue=0, payment=net, order_id=order_id)
            db.session.add(order_payment)
            db.session.flush()
            pay_id = db.session.query(OrderPayment).filter_by(order_id=order_id).first()
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
            print(new_payment)
            db.session.commit()
            res = jsonify(status="success", message="Payment added")

        elif payment_confirm == False:
            res = jsonify(status="Fail", message="Payment Failed")

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
def place_food_order(seller_id, data):
    try:
        net_price = data.get("net")
        gross_price = data.get("gross")
        delivery_fee = data.get("delivery_fee")
        coupon_id = data.get("coupon_id")
        is_mobile = data.get("is_mobile")
        longitude = data.get("longitude")
        latitude = data.get("latitude")
        customer_id = data.get("customer_id")
        payment_plan_id=data.get("payment_plan_id")
        

        food = str(data.get("food"))
        foodresult = ast.literal_eval(food)

        size = str(data.get("size"))
        addon = str(data.get("addon"))        

        #Variable Declaration
        res = {}
        flag = True #can place order if flag is true
        food_id = 0
        qty = 0 #food qty
        f_subtotal = 0 #food subtotal
        f_total = 0 #food total
        discount = 0        
        sale_price = 0 #food sale price
        sold_price = 0 #food sold price
        size_sold_price = 0 #size sold price
        s_food_id=0# size food id
        s_total=0 #Size Total
        s_subtotal=0#size Sub total
        coupon_expire_msg = ""
        coupon_used_msg = ""


        # Create Order id
        ord_id = gen_order_id(Order)

        ######## Get food prices #############
        for id, info in foodresult.items():

            for key in info:
                sold_price = key
                qty = info[key]
                food_id=id                
                food_data = db.session.query(Food).filter_by(id=food_id).first()
                state = food_data.state    
                
                
                #Check State
                if state == 0:
                    flag = False
                elif state == 1:
                    flag = True
                    

                regular_price = food_data.regular_price
                sale_price = food_data.sale_price

                ##### calculate food sub total ####
                f_subtotal = float(sale_price) * float(qty)

                ###### calculate Total#######
                f_total = float(sold_price) * float(qty)                                    
            
                

            ###### add To orderGrocery #####
            new_order_food = OrderFood(
                qty=qty,
                reg_rate=regular_price,
                sub_unit_rate=sale_price,  # sale_price
                unit_rate=sold_price,
                sub_total=f_subtotal,
                total=f_total,
                order_id=ord_id,
                food_id=food_id,
            )
            db.session.add(new_order_food)
            db.session.flush
                             
           

        ########## food size prices #############
        if size != "":
            sizeresult = ast.literal_eval(size)
            for id2, info2 in sizeresult.items():
                for key2 in info2:
                    s_food_id = key2                        
                    size_sold_price = info2[key2]
                size_id = id2  
                                
                

                #################################
                ##### Get SizePrice   ############
                ###################################

                #Check Whether the Food is with a Size or not , then proceed  with size
                             
                
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
                size_regular_price = size_price.description["regular_price"]

                #Get qty from order food to update according to  size
                qty2 = db.session.query(OrderFood).filter(OrderFood.food_id==s_food_id,OrderFood.order_id==ord_id).first()
                qty2=qty2.qty
                               
                ##### calculate size sub total ####
                s_subtotal = float(size_sale_price) * float(qty2)

                ###### calculate size Total#######
                s_total = float(size_sold_price) * float(qty2)
                #print(size_sold_price)         

                #Assign to food total
                f_subtotal=s_subtotal
                f_total=s_total 
                #print(ord_id)

                #######################################
                ## update Order Food according to size #######
                # #####################################
                o_id = db.session.query(OrderFood).filter(OrderFood.food_id==s_food_id,OrderFood.order_id==ord_id).first()
                o_id.reg_rate=size_regular_price
                o_id.sub_unit_rate=size_sale_price
                o_id.unit_rate=size_sold_price
                o_id.sub_total=f_subtotal
                o_id.total=f_total
                db.session.flush()                      

                #Content in Taxonomy
                content = {}
                content = {"regular_price": size_sale_price, "sale_price": size_sold_price} 

                

                #######################################
                ## Create new order Food Size Taxonomy#######
                # #####################################
                new_order_food_tax = OrderFoodTaxonomy(
                    taxonomy="size",
                    content=content,
                    food_order_id=ord_id,
                    term_id=size_id,
                )

                db.session.add(new_order_food_tax)
                db.session.flush()
                

            #print(new_order_food_tax)

        ######### food addon prices #############
        if addon != "":
            addonresult = ast.literal_eval(addon)
            ########## Get food addon prices #############
            for id3, info3 in addonresult.items():

                for key3 in info3:
                    food_id = key3
                    a_qty = info3[key3]

                addon_id = id3
                # print(addon_id,qty,food_id) #

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
                #print(addon_price)

                ####### calculate addon Total#######
                a_total = float(addon_price) * float(a_qty)


                #Assign to food total
                f_subtotal=f_subtotal+a_total
                f_total=f_total+a_total   

                #######################################
                ## update Order Food according to addon#######
                # #####################################
                print(f_subtotal)
                
                o_id = db.session.query(OrderFood).filter(OrderFood.food_id==food_id,OrderFood.order_id==ord_id).first()            
                o_id.sub_total=f_subtotal                
                o_id.total=f_total
                db.session.flush()                      

                content = {}
                content = {"qty": a_qty, "price": addon_price, "total": a_total}

                #######################################
                ## Create new order Food addon Taxonomy#######
                # #####################################
                new_order_food_tax = OrderFoodTaxonomy(
                    taxonomy="addon",
                    content=content,
                    food_order_id=ord_id,
                    term_id=addon_id,
                )

                db.session.add(new_order_food_tax)
                db.session.flush()             
         

        if flag == True: #State is 1 and Seller available

            ref_no = gen_ref_key(Order, "O")
            
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
                        discount = (float(net_price) * float(coupon_val)) / 100 #calculate coupon discounts
                        net_price = float(net_price) - discount  # calculate total net
                    else:
                        discount = coupon_val
                        net_price = float(net_price) - float(coupon_val)  # calculate total net

                    # update Coupon is_use
                    coupon.is_use = True
                    db.session.flush() 
                   

            # calculate Process Fee
            pay_process_fee = (
                db.session.query(PaymentProcessPricePlan)
                .filter_by(id=payment_plan_id)
                .first()
            )
            pay_process_val = pay_process_fee.value
            print(pay_process_val) 
            

            if "%" in pay_process_val:
                pay_process_val = pay_process_val.replace("%", "")
                pay_process_val = (float(net_price) * float(pay_process_val)) / 100
                net_price = float(net_price) + float( pay_process_val )  # calculate total net
            
            else:
                net_price = float(net_price) + float(  pay_process_val )  # calculate total net      

            ################# Save Order ######################
            new_order = Order(
                id=ord_id,
                ref_no=ref_no,
                type="f",
                gross=gross_price,
                discount=discount,
                pay_process_fee=pay_process_val,
                delivery_fee=delivery_fee,
                net=net_price,
                seller_prof=seller_id,
                is_mobile=is_mobile,
            )
            db.session.add(new_order)
            db.session.flush()
            #print(new_order)

            order_id = (
                db.session.query(Order).filter_by(ref_no=ref_no).first()
            )  # order no
            order_id = order_id.id

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

    try:
        # Get net price
        net = db.session.query(Order).filter_by(id=order_id).first()
        net = net.net

        if payment_confirm == True and method == "o":

            # update Order
            order_confirm = db.session.query(Order).filter_by(id=order_id).first()
            # print(order_confirm)
            order_confirm.is_complete = True
            db.session.flush()

            # insert payments
            order_payment = OrderPayment(overdue=0, payment=net, order_id=order_id)
            db.session.add(order_payment)
            db.session.flush()
            pay_id = db.session.query(OrderPayment).filter_by(order_id=order_id).first()
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
            print(new_payment)
            db.session.commit()
            res = jsonify(status="success", message="Payment added")

        elif payment_confirm == False:
            res = jsonify(status="fail", message="Payment fail")

    except Exception as e:
        res = jsonify(Status="Fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return res



#Order Return
@token_required
def return_order(order_id,data):
    try:
        product_data = str(data.get("product_data"))
        return_note=data.get("return_note")
        result = ast.literal_eval(product_data)
        ref_no = gen_ref_key(OrderReturn, "OR")#order return reference number
        now = datetime.now()
        

        #add to order return
        new_order_return=OrderReturn(ref_no=ref_no,date=now,note=return_note,order_id=order_id)
        db.session.add(new_order_return)
        db.session.flush()
        return_id=new_order_return.id       
        
        for id, info in result.items():        

            for key in info:                
                qty = info[key]
                product_id = key
            

            #add to order grocery return
            new_return_grocery=OrderReturnGrocery(qty=qty,return_id=return_id,grocery_order_id=order_id)
            db.session.add(new_return_grocery)
            db.session.flush()

        db.session.commit()       

        res = jsonify(status="success", message="Order Return successfully")
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res    
    

#Order Cancel
@token_required
def cancel_order(ord_id,data):
    try:
        type=data.get("type")#food or grocery f/g
        cancel_note=data.get("cancel_note")            
        pro_id=0
        qty=0
        seller_id=0

        order_status=db.session.query(OrderMobile).filter_by(order_id=ord_id).first()
        order_details=db.session.query(Order).filter_by(id=ord_id).first()   
        seller_id=order_details.seller_prof
        print(seller_id) 
        order_payment=db.session.query(OrderPayment).filter_by(id=ord_id).first()
        payment_id=order_payment.id    
        order_payment_details=db.session.query(OrderPaymentDetails).filter_by(id=payment_id).first()    
        #print(payment_id)   

        if order_status.is_pick==False and order_status.is_ship==False and order_status.is_deliver==False and order_status.is_recive==False and order_status.is_ready==False: 
            print("Can be Cancelled")   
            #update order
            order_details.is_complete=False
            order_details.is_cancel=True

            #update orderpayment details
            order_payment_details.contnet=cancel_note
            order_payment_details.is_complete=False
            order_payment_details.is_cancel=True


            #add OrderNote
            order_note=OrderNote(content=cancel_note,order_id=ord_id)
            db.session.add(order_note)
            db.session.flush()

            if type=="g":
                #update grocery stock for cancel products
                order_cancel=db.session.query(OrderGrocery.id,OrderGrocery.qty,OrderGrocery.product_id).filter_by(order_id=ord_id).all()

                for i in order_cancel:
                    pro_id=i.product_id
                    qty=i.qty
                    #print(pro_id,qty)

                    grocery_stock=db.session.query(GroceryProductStock).filter(GroceryProductStock.seller_prof==seller_id,GroceryProductStock.product_id==pro_id).first()
                    print(grocery_stock.product_id)
                    grocery_stock.qty=grocery_stock.qty+qty
                    db.session.flush()  
               


            db.session.commit()

        res = jsonify(status="success", message="order cancelled")
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res   
   

#All Orders
@token_required
def all_orders(customer_id):
    try:
        res = []       
        orders=db.session.query(Order.id,Order.is_complete,Order.seller_prof,Order.date,Order.net,SellerProfile.organization,SellerProfile.street_address).join(SellerProfile,SellerProfile.id==Order.seller_prof).join(OrderMobile,OrderMobile.order_id==Order.id).filter(OrderMobile.cus_id==customer_id).all()
        #print(orders)
        for i in orders:
            info = {"order_id": i.id, "is_complete": i.is_complete, "seller_name": i.organization,"street_address":i.street_address,"Order_date":i.date,"net":i.net}
            res.append(info)
            

        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res   

@token_required
def completed_orders(customer_id):
    try:
        res = []       
        orders=db.session.query(Order.id,Order.is_complete,Order.seller_prof,Order.date,Order.net,SellerProfile.organization,SellerProfile.street_address).join(SellerProfile,SellerProfile.id==Order.seller_prof).join(OrderMobile,OrderMobile.order_id==Order.id).filter(OrderMobile.cus_id==customer_id,Order.is_complete==True).all()
        #print(orders)
        for i in orders:
            info = {"order_id": i.id, "is_complete": i.is_complete, "seller_name": i.organization,"street_address":i.street_address,"Order_date":i.date,"net":i.net}
            res.append(info)
            

        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res   

@token_required
def ongoing_orders(customer_id):
    try:
        res = []       
        orders=db.session.query(Order.id,Order.is_complete,Order.seller_prof,Order.date,Order.net,SellerProfile.organization,SellerProfile.street_address).join(SellerProfile,SellerProfile.id==Order.seller_prof).join(OrderMobile,OrderMobile.order_id==Order.id).filter(OrderMobile.cus_id==customer_id,Order.is_complete==False).all()
        #print(orders)
        for i in orders:
            info = {"order_id": i.id, "is_complete": i.is_complete, "seller_name": i.organization,"street_address":i.street_address,"Order_date":i.date,"net":i.net}
            res.append(info)
            

        res = jsonify(res)
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res   


#Per Order Status 
@token_required
def grocery_order_status(order_id):
    try:
        res=[]
        res2={}       
        #get order details
        order=db.session.query(Order.id,Order.is_complete,Order.seller_prof,Order.date,Order.net,SellerProfile.organization,SellerProfile.street_address).join(SellerProfile,SellerProfile.id==Order.seller_prof).join(OrderMobile,OrderMobile.order_id==Order.id).filter(Order.id==order_id).first()
        #get order_grocery details
        order_grocery=db.session.query(OrderGrocery.qty,OrderGrocery.total,OrderGrocery.product_id,GroceryProduct.name).join(GroceryProduct, GroceryProduct.id==OrderGrocery.product_id).filter(OrderGrocery.order_id==order_id).all()
       
        for i in order_grocery:
            info = {"product_name": i.name, "qty": i.qty,"Total":i.total}
            res.append(info)

        res2={ "net_price":order.net, "is_complete":order.is_complete,"order_date":order.date,"organization":order.organization,"seller_address":order.street_address}
    
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
    customer_id=data.get("customer_id")
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


#Customer Ticket
@token_required
def customer_ticket(data):
    try:
        
        ticket_category_id=data.get("ticket_category_id")
        customer_text=data.get("customer_text")
        customer_id=data.get("customer_id")
       
        
        ref_no = gen_ref_key(CustomerTicket, "CT")
        now = datetime.now()
        res={}
            
        
        #new Ticket
        ticket=CustomerTicket(ref_no=ref_no,date=now,is_open=True,cat_id=ticket_category_id,cus_id=customer_id)                
        db.session.add(ticket)                  
        db.session.flush()
            

        #new Customer Ticket Message
        new_cus_message=CustomerTicketMessage(customer_text=customer_text,ticket_id=ticket.id)
        db.session.add(new_cus_message)
        db.session.commit()
        
       

        res = jsonify(status="success", message="Ticket added")
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return res


#Customer Ticket
@token_required
def save_card(data):
    try:
        bank_number=str(data.get("bank_number"))
        type=data.get("type")
        card_number=str(data.get("card_number"))
        expire=data.get("expire")
        cvv=str(data.get("cvv"))
        holder=data.get("holder")
        customer_id=data.get("customer_id")
           



        #Bcrypt card details
        bank_number = bcrypt.generate_password_hash(bank_number)
        card_number=bcrypt.generate_password_hash(card_number)
        cvv=bcrypt.generate_password_hash(cvv)       
        

        new_card=CustomerCard(bank_name=bank_number,type=type,card_no=card_number,cvv=cvv,holder=holder,expires_at=expire,cus_id=customer_id)
        db.session.add(new_card)
        db.session.commit()
            

        res = jsonify(status="success", message="Card details saved")
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res