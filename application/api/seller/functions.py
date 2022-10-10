import os
from flask import current_app, jsonify
from sqlalchemy import func
from http import HTTPStatus

from application import db
from application.helpers import token_required
from application.models import (
    FoodTaxonomy,
    FoodTerm,
    SellerProfile,
    GroceryProductStock,
    GroceryProduct,
    GroceryProductTerm,
    GroceryProductTermMap,
    GroceryProductTaxonomy,
    Feedback,
    CustomerSellerFeedback,
    Food,
    FoodTermMap,
    CustomerUser,
    CustomerProfile,
)


# Seller details
# Display initial details of seller (Organization Name, Main category, Rating, Address)
def get_seller(seller_id):

    rate_q = (
        db.session.query(
            Feedback.rate_cal(func.sum(Feedback.rate), func.count(Feedback.id)).label(
                "rateing"
            ),
            CustomerSellerFeedback.seller_prof,
        )
        .join(CustomerSellerFeedback, Feedback.id == CustomerSellerFeedback.seller_prof)
        .filter(CustomerSellerFeedback.seller_prof == seller_id)
        .group_by(CustomerSellerFeedback.seller_prof)
        .order_by("rateing")
        .subquery()
    )
    # Fetech seller
    seller = (
        db.session.query(
            SellerProfile,
            func.IF(rate_q.c.rateing != None, rate_q.c.rateing, 0).label("rateing"),
        )
        .outerjoin(rate_q, rate_q.c.seller_prof == SellerProfile.id)
        .filter(SellerProfile.id == seller_id)
        .first()
    )

    state = "active"
    if seller.SellerProfile.is_inactive == True:
        state = "inactive"

    res = {
        "ref_no": seller.SellerProfile.ref_no,
        "type": seller.SellerProfile.type,
        "org": seller.SellerProfile.organization,
        "street": seller.SellerProfile.street_address,
        "city": seller.SellerProfile.city_address,
        "postcode": seller.SellerProfile.postcode,
        "contact_no": seller.SellerProfile.contact_no,
        "longitude": seller.SellerProfile.longitude,
        "latitude": seller.SellerProfile.longitude,
        "state": state,
        "rateing": seller.rateing,
        "img": current_app.config.get("DOWNLOAD_PATH")
        + "/img/seller_usr/"
        + seller.SellerProfile.image,
    }

    return jsonify(res)


# Seller grocery categories
# Seller grocery categories based on stocked product
def get_grocery_category(seller_id, counter):

    stock_q = (
        db.session.query(
            GroceryProduct.id.label("prd_id"),
            GroceryProductStock.seller_prof,
            GroceryProductTermMap.term_id,
        )
        .join(GroceryProductStock, GroceryProductStock.product_id == GroceryProduct.id)
        .join(
            GroceryProductTermMap,
            GroceryProductTermMap.product_id == GroceryProduct.id,
        )
        .filter(
            GroceryProduct.state == 1,
            GroceryProductStock.is_idle == False,
            GroceryProductStock.seller_prof == seller_id,
        )
        .group_by(GroceryProductTermMap.term_id)
        .subquery()
    )

    cat = (
        db.session.query(
            GroceryProductTerm.id,
            GroceryProductTerm.term,
            GroceryProductTerm.image,
            GroceryProductTaxonomy.taxonomy,
            stock_q.c.prd_id,
        )
        .join(
            GroceryProductTaxonomy,
            GroceryProductTaxonomy.term_id == GroceryProductTerm.id,
        )
        .join(stock_q, stock_q.c.term_id == GroceryProductTerm.id)
        .filter(GroceryProductTaxonomy.taxonomy == "category")
        .paginate(page=counter, per_page=current_app.config.get("DISPLAY_LIST_LENGTH"))
    )

    res = []
    for i in cat.items:
        info = {
            "category_id": i.id,
            "name": i.term,
            "img": current_app.config.get("DOWNLOAD_PATH") + "/img/inv/" + i.image,
        }
        res.append(info)

    return res


# Seller grocery categories
# Seller grocery categories based on stocked product
def get_food_category(seller_id, counter):

    food_q = (
        db.session.query(Food.id.label("food_id"), FoodTermMap.term_id)
        .join(FoodTermMap, FoodTermMap.food_id == Food.id)
        .filter(Food.seller_prof == seller_id, Food.state == 1)
        .group_by(FoodTermMap.term_id)
        .subquery()
    )

    cat = (
        db.session.query(
            FoodTerm.id,
            FoodTerm.term,
            FoodTerm.image,
            FoodTaxonomy.taxonomy,
            food_q.c.food_id,
        )
        .join(FoodTaxonomy, FoodTaxonomy.term_id == FoodTerm.id)
        .join(food_q, food_q.c.term_id == FoodTerm.id)
        .filter(FoodTaxonomy.taxonomy == "category")
        .paginate(page=counter, per_page=current_app.config.get("DISPLAY_LIST_LENGTH"))
    )

    res = []
    for i in cat.items:
        info = {
            "category_id": i.id,
            "name": i.term,
            "img": current_app.config.get("DOWNLOAD_PATH") + "/img/inv/" + i.image,
        }
        res.append(info)

    return res


# Seller grocery product
# Madatory = seller_id, Optinal = category id
def get_grocery_products(seller_id, cat_id, counter):

    prd = (
        db.session.query(
            GroceryProduct.id.label("prd_id"),
            GroceryProduct.ref_no,
            GroceryProduct.name,
            GroceryProduct.description.label("desc"),
            GroceryProduct.is_feature,
            GroceryProduct.image,
            GroceryProductStock.qty,
            GroceryProductStock.regular_price.label("reg_price"),
            GroceryProductStock.app_price,
            GroceryProductTermMap.term_id,
        )
        .join(GroceryProductStock, GroceryProductStock.product_id == GroceryProduct.id)
        .join(
            GroceryProductTermMap,
            GroceryProductTermMap.product_id == GroceryProduct.id,
        )
        .filter(
            GroceryProductStock.seller_prof == seller_id,
            GroceryProductStock.is_idle == False,
            GroceryProduct.state == 1,
        )
    )

    if cat_id != None:
        prd = prd.filter(GroceryProductTermMap.term_id == cat_id)

    prd = prd.group_by("prd_id").paginate(
        page=counter, per_page=current_app.config.get("DISPLAY_LIST_LENGTH")
    )

    res = []
    for i in prd.items:
        cat = (
            db.session.query(
                GroceryProductTerm.term,
                GroceryProductTaxonomy.taxonomy,
                GroceryProductTermMap.product_id,
            )
            .join(
                GroceryProductTaxonomy,
                GroceryProductTaxonomy.term_id == GroceryProductTerm.id,
            )
            .join(
                GroceryProductTermMap,
                GroceryProductTermMap.term_id == GroceryProductTerm.id,
            )
            .filter(GroceryProductTermMap.product_id == i.prd_id)
            .all()
        )
        brand = ""
        size = ""
        unit = ""
        for j in cat:
            if j.taxonomy == "brand":
                brand = j.term.capitalize()
            elif j.taxonomy == "size":
                size = j.term.capitalize()
            elif j.taxonomy == "unit":
                unit = j.term

        info = {
            "product_id": i.prd_id,
            "ref_no": i.ref_no,
            "name": i.name,
            "desc": i.desc,
            "qry": i.qty,
            "feature": i.is_feature,
            "regular_price": i.reg_price,
            "sale_price": i.app_price,
            "brand": brand,
            "size": size,
            "unit": unit,
            "img": current_app.config.get("DOWNLOAD_PATH") + "/img/inv/" + i.image,
        }
        res.append(info)

    return jsonify(res)


# Seller all food product
# Madatory = seller_id, type, Optinal = category id
def get_food_products(seller_id, cat_id, counter):

    prd = (
        db.session.query(
            Food.id.label("prd_id"),
            Food.ref_no,
            Food.name,
            Food.description.label("desc"),
            Food.is_feature,
            Food.image,
            Food.regular_price.label("reg_price"),
            Food.app_price,
            FoodTermMap.term_id,
        )
        .join(FoodTermMap, FoodTermMap.food_id == Food.id)
        .filter(Food.seller_prof == seller_id, Food.state == 1)
    )

    if cat_id != None:
        prd = prd.filter(FoodTermMap.term_id == cat_id)

    prd = prd.group_by("prd_id").paginate(
        page=counter, per_page=current_app.config.get("DISPLAY_LIST_LENGTH")
    )

    res = []
    for i in prd.items:

        cat = (
            db.session.query(
                FoodTerm.id,
                FoodTerm.term,
                FoodTerm.description,
                FoodTaxonomy.taxonomy,
                FoodTermMap.food_id,
            )
            .join(FoodTaxonomy, FoodTaxonomy.term_id == FoodTerm.id)
            .join(FoodTermMap, FoodTermMap.term_id == FoodTerm.id)
            .filter(FoodTermMap.food_id == i.prd_id)
            .all()
        )

        size = []
        addon = []
        for j in cat:
            if j.taxonomy == "size":
                size_price = (
                    db.session.query(
                        FoodTerm.description, FoodTaxonomy.taxonomy, FoodTermMap.food_id
                    )
                    .join(FoodTaxonomy, FoodTaxonomy.term_id == FoodTerm.id)
                    .join(FoodTermMap, FoodTermMap.term_id == FoodTerm.id)
                    .filter(
                        FoodTermMap.food_id == i.prd_id,
                        FoodTaxonomy.parent_id == j.id,
                        FoodTaxonomy.taxonomy == "size-price",
                    )
                    .first()
                )
                info = {
                    "id": j.id,
                    "term": j.term.capitalize(),
                    "regular_price": size_price.description["regular_price"],
                    "sale_price": size_price.description["app_price"],
                }
                size.append(info)
            elif j.taxonomy == "addon":
                min_qty = "None"
                max_qty = "None"
                if j.description["min_qty"] > 0:
                    min_qty = j.description["min_qty"]
                if j.description["max_qty"] > 0:
                    max_qty = j.description["max_qty"]
                req_class = ""
                if j.description["require"] == True:
                    req_class = "lbl-mand"
                info = {
                    "id": j.id,
                    "term": j.term.capitalize(),
                    "price": j.description["price"],
                    "desc": j.description["desc"],
                    "min_qty": min_qty,
                    "max_qty": max_qty,
                    "req_class": req_class,
                    "require": str(j.description["require"]),
                }
                addon.append(info)

        info = {
            "product_id": i.prd_id,
            "ref_no": i.ref_no,
            "name": i.name,
            "desc": i.desc,
            "feature": i.is_feature,
            "regular_price": i.reg_price,
            "sale_price": i.app_price,
            "size": size,
            "addon": addon,
            "img": current_app.config.get("DOWNLOAD_PATH") + "/img/inv/" + i.image,
        }
        res.append(info)

    return jsonify(res)


# Review Create customer_seller
# Create from mandatory = rate
# review,order_id
@token_required
def review_create(seller_id, data):
    rate = data.get("rate")
    review = data.get("review")
    order_id = data.get("order_id")
    if order_id == 0:
        order_id = None

    res = {}

    try:
        new_feedback = Feedback(rate=rate, review=review, order_id=order_id)
        db.session.add(new_feedback)
        db.session.flush()
        feedback_id = new_feedback.id
        new_customer_seller = CustomerSellerFeedback(
            feedback_id=feedback_id, cus_id=review_create.user_id, seller_prof=seller_id
        )
        db.session.add(new_customer_seller)
        db.session.commit()

        res = jsonify(status="success", message="review created")
        res.status_code = HTTPStatus.CREATED
    except Exception as e:
        res = jsonify(status="fail", message=str(e))
        res.status_code = HTTPStatus.INTERNAL_SERVER_ERROR

    return res


# Get all seller reviews
def get_seller_review(seller_id):
    seller_rev = (
        db.session.query(
            Feedback.id, Feedback.rate, Feedback.review, CustomerProfile.first_name
        )
        .join(CustomerSellerFeedback, CustomerSellerFeedback.feedback_id == Feedback.id)
        .join(CustomerUser, CustomerSellerFeedback.cus_id == CustomerUser.id)
        .join(CustomerProfile, CustomerUser.id == CustomerProfile.cus_id)
        .filter(CustomerSellerFeedback.seller_prof == seller_id)
        .limit(50)
    )
    res = []
    for i in seller_rev:
        info = {"first_name": i.first_name, "rate": i.rate, "review": i.review}

        res.append(info)
    return jsonify(res)
