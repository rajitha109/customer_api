import os
from datetime import datetime
from flask import current_app, jsonify
from sqlalchemy import column, func, and_, or_

from application import db
from application.models import (
    GroceryProduct,
    SellerProfile,
    Feedback,
    CustomerSellerFeedback,
    Ad,
    AdGrocery,
    AdFood,
    GroceryProductTerm,
    GroceryProductTaxonomy,
    Food,
    FoodTerm,
    FoodTaxonomy,
    FoodTermMap,
    GroceryProductStock,
    SellerGroceryCategory,
)


# Home screen function
def home():

    # Get Latest two ads
    res_ad = []
    ad = (
        db.session.query(Ad.id, Ad.image)
        .filter(
            and_(
                Ad.from_date >= datetime.today().strftime("%Y-%m-%d"),
                Ad.to_date <= datetime.today().strftime("%Y-%m-%d"),
            ),
            Ad.is_live == True,
        )
        .order_by(Ad.id.desc())
        .limit(2)
        .all()
    )
    for i in ad:
        info = {
            "id": i.id,
            "img": os.path.join(
                current_app.root_path,
                current_app.config.get("UPLOAD_PATH") + "/img/ad" + i.image,
            ),
        }
        res_ad.append(info)

    # # Get top sellers
    # res_seller = []
    # rate_q = (
    #     db.session.query(
    #         Feedback.rate_cal(func.sum(Feedback.rate), func.count(Feedback.id)).label(
    #             "rateing"
    #         ),
    #         CustomerSellerFeedback.seller_prof,
    #     )
    #     .join(CustomerSellerFeedback, Feedback.id == CustomerSellerFeedback.seller_prof)
    #     .group_by(CustomerSellerFeedback.seller_prof)
    #     .order_by("rateing")
    #     .subquery()
    # )

    # prof = (
    #     db.session.query(
    #         SellerProfile,
    #         SellerProfile.distance(long, lati).label("distance"),
    #         rate_q.c.rateing,
    #     )
    #     .having(column("distance") < current_app.config.get("MAX_DISTANCE"))
    #     .outerjoin(rate_q, rate_q.c.seller_prof == SellerProfile.id)
    #     .filter(SellerProfile.is_inactive == False)
    #     .order_by("distance")
    #     .limit(5)
    #     .all()
    # )

    # for i in prof:

    #     info = {
    #         "id": i.SellerProfile.id,
    #         "org": i.SellerProfile.organization,
    #         "type": i.SellerProfile.type,
    #         "img": os.path.join(
    #             current_app.root_path,
    #             current_app.config.get("UPLOAD_PATH")
    #             + "/img/seller_usr"
    #             + i.SellerProfile.image,
    #         ),
    #     }
    #     res_seller.append(info)

    data = {"ad": res_ad}
    return jsonify(data)


# Grocery home screen function
def grocery_home():
    return get_home(GroceryProductTerm, GroceryProductTaxonomy, AdGrocery)


# Food home screen function
def food_home():
    return get_home(FoodTerm, FoodTaxonomy, AdFood)


# Get product home
def get_home(term_db, tax_db, ad_db):
    # Category
    cat = (
        db.session.query(
            term_db.id,
            term_db.term,
            term_db.image,
            tax_db.taxonomy,
        )
        .join(
            tax_db,
            tax_db.term_id == term_db.id,
        )
        .filter(tax_db.taxonomy == "category", tax_db.parent_id == None)
        .all()
    )

    res_cat = []
    for i in cat:
        info = {
            "category_id": i.id,
            "name": i.term,
            "img": os.path.join(
                current_app.root_path,
                current_app.config.get("UPLOAD_PATH") + "/img/inv" + i.image,
            ),
        }
        res_cat.append(info)

    # Get Latest two ads
    ad = (
        db.session.query(Ad.id, Ad.image, ad_db.cat_id)
        .join(ad_db, ad_db.ad_id == Ad.id)
        .filter(
            and_(
                Ad.from_date >= datetime.today().strftime("%Y-%m-%d"),
                Ad.to_date <= datetime.today().strftime("%Y-%m-%d"),
            ),
            Ad.is_live == True,
        )
        .order_by(Ad.id.desc())
        .limit(2)
        .all()
    )

    res_ad = []
    for i in ad:
        info = {
            "ad_id": i.id,
            "img": os.path.join(
                current_app.root_path,
                current_app.config.get("UPLOAD_PATH") + "/img/ad" + i.image,
            ),
        }
        res_ad.append(info)

    data = {"cat": res_cat, "ad": res_ad}
    return jsonify(data)


# Find sellers
# Filter fields mandatory = [Longtitude, Latitude], optional = [category, keyword]
def seller_find(data, type):

    long = data.get("longitude")
    lati = data.get("latitude")
    cat = data.get("category")
    keyword = data.get("keyword")
    counter = data.get("counter")

    seller_q = (
        db.session.query(
            SellerProfile.id,
            SellerProfile.organization.label("org"),
            SellerProfile.street_address.label("street"),
            SellerProfile.city_address.label("city"),
            SellerProfile.image,
            SellerProfile.distance(long, lati).label("distance"),
        )
        .having(column("distance") < current_app.config.get("MAX_DISTANCE"))
        .order_by("distance")
        .filter(SellerProfile.is_inactive == False, SellerProfile.type == type)
        .subquery()
    )

    query = ""
    # Type = grocery
    if type == "g":
        # Taxonomy
        tax = (
            db.session.query(
                GroceryProductTerm.id.label("term_id"),
                SellerGroceryCategory.cat_id,
                seller_q.c.id,
                seller_q.c.org,
                seller_q.c.image,
            )
            .join(
                GroceryProductTerm,
                GroceryProductTerm.id == SellerGroceryCategory.cat_id,
            )
            .join(seller_q, seller_q.c.id == SellerGroceryCategory.seller_prof)
        )
        # Category avilable
        if cat != "":
            tax = tax.filter(GroceryProductTerm.id == cat)
        if keyword != "":
            keyword = "%{}%".format(keyword)
            tax = tax.filter(
                or_(
                    seller_q.c.org.like(keyword),
                    seller_q.c.street.like(keyword),
                    seller_q.c.city.like(keyword),
                    GroceryProductTerm.term.like(keyword),
                )
            )
        query = tax.paginate(
            page=counter, per_page=current_app.config.get("DISPLAY_LIST_LENGTH")
        )
    # Type = food
    elif type == "f":
        item_q = (
            db.session.query(
                Food.id.label("food_id"),
                seller_q.c.id,
                seller_q.c.org,
                seller_q.c.image,
                seller_q.c.street,
                seller_q.c.city,
            )
            .join(seller_q, seller_q.c.id == Food.seller_prof)
            .subquery()
        )
        # Taxonomy
        tax = (
            db.session.query(
                FoodTerm.term,
                FoodTermMap.food_id,
                item_q.c.id,
                item_q.c.org,
                item_q.c.image,
            )
            .join(FoodTerm, FoodTerm.id == FoodTermMap.term_id)
            .join(item_q, item_q.c.food_id == FoodTermMap.food_id)
        )
        if cat != "":
            tax = tax.filter(FoodTerm.id == cat)
        if keyword != "":
            keyword = "%{}%".format(keyword)
            tax = tax.filter(
                or_(
                    item_q.c.org.like(keyword),
                    item_q.c.street.like(keyword),
                    item_q.c.city.like(keyword),
                    FoodTerm.term.like(keyword),
                )
            )
        query = tax.group_by(item_q.c.id).paginate(
            page=counter, per_page=current_app.config.get("DISPLAY_LIST_LENGTH")
        )

    res = []
    for i in query.items:

        info = {
            "id": i.id,
            "org": i.org,
            "img": os.path.join(
                current_app.root_path,
                current_app.config.get("UPLOAD_PATH") + "/img/seller_usr",
            )
            + i.image,
        }
        res.append(info)

    return res


# Find grocery product
# Filter fields mandatory = [Longtitude, Latitude], optional = [category, keyword]
def grocery_product_find(data):

    long = data.get("longitude")
    lati = data.get("latitude")
    cat = data.get("category")
    keyword = data.get("keyword")
    counter = data.get("counter")

    seller_q = (
        db.session.query(
            SellerProfile.id.label("seller_id"),
            SellerProfile.type.label("type"),
            SellerProfile.distance(long, lati).label("distance"),
        )
        .having(column("distance") < current_app.config.get("MAX_DISTANCE"))
        .order_by("distance")
        .filter(SellerProfile.is_inactive == False, SellerProfile.type == "g")
        .subquery()
    )

    # Taxonomy
    tax_q = (
        db.session.query(
            GroceryProductTerm.term,
            SellerGroceryCategory.cat_id,
            seller_q.c.seller_id,
            seller_q.c.type,
        )
        .join(
            GroceryProductTerm,
            GroceryProductTerm.id == SellerGroceryCategory.cat_id,
        )
        .join(seller_q, seller_q.c.seller_id == SellerGroceryCategory.seller_prof)
    )
    # Category avilable
    if cat != "":
        tax_q = tax_q.filter(GroceryProductTerm.id == cat)
    tax_q = tax_q.subquery()
    prd = (
        db.session.query(
            GroceryProduct.id,
            GroceryProduct.ref_no,
            GroceryProduct.name,
            GroceryProduct.description.label("desc"),
            GroceryProduct.is_feature,
            GroceryProduct.image,
            GroceryProductStock.qty,
            GroceryProductStock.regular_price.label("reg_price"),
            GroceryProductStock.sale_price,
            tax_q.c.seller_id,
        )
        .join(GroceryProduct, GroceryProduct.id == GroceryProductStock.product_id)
        .join(tax_q, tax_q.c.seller_id == GroceryProductStock.seller_prof)
        .filter(GroceryProduct.state == 1, GroceryProductStock.is_idle == False)
    )
    if keyword != "":
        keyword = "%{}%".format(keyword)
        prd = prd.filter(
            or_(
                GroceryProduct.name.like(keyword),
                GroceryProduct.description.like(keyword),
                tax_q.c.term.like(keyword),
            )
        )

    prd = prd.paginate(
        page=counter, per_page=current_app.config.get("DISPLAY_LIST_LENGTH")
    )

    res = []
    for i in prd.items:
        info = {
            "product_id": i.id,
            "seller_id": i.seller_id,
            "ref_no": i.ref_no,
            "name": i.name,
            "desc": i.desc,
            "qty": str(i.qty),
            "reg_price": str(i.reg_price),
            "sale_price": str(i.sale_price),
            "img": os.path.join(
                current_app.root_path,
                current_app.config.get("UPLOAD_PATH") + "/img/seller_usr",
            )
            + i.image,
        }
        res.append(info)

    return res


# Find grocery product
# Filter fields mandatory = [Longtitude, Latitude], optional = [category, keyword]
def food_product_find(data):

    long = data.get("longitude")
    lati = data.get("latitude")
    cat = data.get("category")
    keyword = data.get("keyword")
    counter = data.get("counter")

    seller_q = (
        db.session.query(
            SellerProfile.id.label("seller_id"),
            SellerProfile.type.label("type"),
            SellerProfile.distance(long, lati).label("distance"),
        )
        .having(column("distance") < current_app.config.get("MAX_DISTANCE"))
        .order_by("distance")
        .filter(SellerProfile.is_inactive == False, SellerProfile.type == "f")
        .subquery()
    )

    # Taxonomy
    tax_q = (
        db.session.query(FoodTerm.term, FoodTermMap.food_id, FoodTaxonomy.taxonomy)
        .join(FoodTaxonomy, FoodTaxonomy.term_id == FoodTerm.id)
        .join(FoodTermMap, FoodTermMap.term_id == FoodTerm.id)
        .filter(FoodTaxonomy.taxonomy == 'category')
    )
    # Category avilable
    if cat != "":
        tax_q = tax_q.filter(FoodTerm.id == cat)
    tax_q = tax_q.subquery()
    prd = (
        db.session.query(
            Food.id,
            Food.ref_no,
            Food.name,
            Food.description.label("desc"),
            Food.is_feature,
            Food.image,
            Food.regular_price.label("reg_price"),
            Food.sale_price,
            seller_q.c.seller_id,
        )
        .join(seller_q, seller_q.c.seller_id == Food.seller_prof)
        .join(tax_q, tax_q.c.food_id == Food.id)
        .filter(Food.state == 1)
    )
    if keyword != "":
        keyword = "%{}%".format(keyword)
        prd = prd.filter(
            or_(
                Food.name.like(keyword),
                Food.description.like(keyword),
                tax_q.c.term.like(keyword),
            )
        )
    prd = prd.group_by(Food.id).paginate(
        page=counter, per_page=current_app.config.get("DISPLAY_LIST_LENGTH")
    )

    res = []
    for i in prd.items:

        addon = (
            db.session.query(FoodTerm.term, FoodTermMap.food_id, FoodTaxonomy.taxonomy)
            .join(FoodTaxonomy, FoodTaxonomy.term_id == FoodTerm.id)
            .join(FoodTermMap, FoodTermMap.term_id == FoodTerm.id)
            .filter(FoodTaxonomy.taxonomy == 'addon', FoodTermMap.food_id == i.id)
            .first()
        ) is not None

        info = {
            "product_id": i.id,
            "seller_id": i.seller_id,
            "ref_no": i.ref_no,
            "name": i.name,
            "desc": i.desc,
            "reg_price": str(i.reg_price),
            "sale_price": str(i.sale_price),
            "addon":addon,
            "img": os.path.join(
                current_app.root_path,
                current_app.config.get("UPLOAD_PATH") + "/img/seller_usr",
            )
            + i.image,
        }
        res.append(info)

    return res


# Filter categorois
def category_filter(type, cat_id):
    # If type = Grocery
    tax = ""
    if type == "g":
        tax = (
            db.session.query(
                GroceryProductTerm.id,
                GroceryProductTerm.term,
                GroceryProductTaxonomy.taxonomy,
            )
            .join(
                GroceryProductTerm,
                GroceryProductTerm.id == GroceryProductTaxonomy.term_id,
            )
            .filter(
                GroceryProductTaxonomy.taxonomy == "category",
                GroceryProductTaxonomy.parent_id == cat_id,
                GroceryProductTerm.is_inactive == False,
            )
            .all()
        )
    elif type == "f":
        tax = (
            db.session.query(FoodTerm.id, FoodTerm.term, FoodTaxonomy.taxonomy)
            .join(FoodTaxonomy, FoodTaxonomy.term_id == FoodTerm.id)
            .filter(FoodTaxonomy.taxonomy == "category", FoodTerm.is_inactive == False)
            .all()
        )

    res = []
    for i in tax:
        info = {"id": i.id, "term": i.term}
        res.append(info)

    return res
