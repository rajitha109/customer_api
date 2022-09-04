
from http import HTTPStatus
from flask_restx import Namespace, Resource

from application.helpers import token_required
from .dto import rev_parser
from .functions import (
    get_seller,
    get_grocery_category,
    get_food_category,
    get_grocery_products,
    get_food_products,
    review_create,
    get_seller_review
)

seller_ns = Namespace(name="seller", validate=True)


# Seller details
@seller_ns.route("/<int:seller_id>", endpoint="seller_profile")
class GetSeller(Resource):
    """Handles HTTP requests to URL: /api/v1/seller/<seller_id>"""

    @seller_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @seller_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, seller_id):
        """
        Get seller details
        Demo pass value
        { seller_id : '1' }
        Intended result
        {
            'ref_no':'number',
            'type':'g/f,
            'org':'organization',
            'street':'street address',
            'city':'city',
            'postcode':postcode,
            'contact_no':contact_no,
            'longitude':float,
            'latitude':float,
            'state':'active/inactive',
            'rating':'number'
            'img':url
        }
        """
        return get_seller(seller_id)


# Seller grocery categories
@seller_ns.route(
    "/grocery/category/<int:seller_id>/<int:counter>",
    endpoint="seller_grocery_category",
)
class GroceryCategory(Resource):
    """Handles HTTP requests to URL: /api/v1/seller/grocery/category/<seller_id>/<counter>"""

    @seller_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @seller_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, seller_id, counter):
        """
        Get seller categories
        Demo pass value
        { seller_id : '1', counter : integer, default = 1 }
        Intended result
        {
            'category_id':integer,
            'name':'category name',
            'img':url
        }
        """
        return get_grocery_category(seller_id, counter)


# Seller food categories
@seller_ns.route(
    "/food/category/<int:seller_id>/<int:counter>", endpoint="seller_food_category"
)
class GroceryCategory(Resource):
    """Handles HTTP requests to URL: /api/v1/seller/food/category/<seller_id>/<counter>"""

    @seller_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @seller_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, seller_id, counter):
        """
        Get seller categories
        Demo pass value
        { seller_id : '1', counter : integer, default = 1 }
        Intended result
        {
            'category_id':integer,
            'name':'category name',
            'img':url
        }
        """
        return get_food_category(seller_id, counter)


# Seller shop
# Get all grocery product without categroy filter
@seller_ns.route(
    "/grocery/product/<int:seller_id>/<int:counter>", endpoint="seller_grocery_shop"
)
class GroceryShop(Resource):
    """Handles HTTP requests to URL: /api/v1/seller/grocery/shop/<seller_id>/<counter>"""

    @seller_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @seller_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, seller_id, counter):
        """
        Get seller allgrocery products without category filter
        Demo pass value
        { seller_id : '1', counter : integer, default = 1 }
        Intended result
        {
            'product_id':integer,
            'ref_no':'product unique referece no',
            'name':'name',
            'desc':'description as html',
            'qry': float, ignore food qty,
            'feature':true/false,
            'regular_price':decimal,
            'sale_price': decimal,
            "img": url,
        }
        """
        return get_grocery_products(seller_id, None, counter)


# Seller shelf
# Get grocery product with categroy filter
@seller_ns.route(
    "/grocery/product/<int:seller_id>/<int:category_id>/<int:counter>",
    endpoint="seller_grocery_shelf",
)
class GroceryShelf(Resource):
    """Handles HTTP requests to URL: /api/v1/seller/grocery/shop/<seller_id>/<category_id>/<counter>"""

    @seller_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @seller_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, seller_id, category_id, counter):
        """
        Get seller all grocery products with category filter
        Demo pass value
        { seller_id : '1', category_id=integer, counter : integer, default = 1 }
        Intended result
        {
            'product_id':integer,
            'ref_no':'product unique referece no',
            'name':'name',
            'desc':'description as html',
            'qry': float, ignore food qty,
            'feature':true/false,
            'regular_price':decimal,
            'sale_price': decimal,
            "img": url,
        }
        """
        return get_grocery_products(seller_id, category_id, counter)


# Seller shop
# Get all food product without categroy filter
@seller_ns.route(
    "/food/product/<int:seller_id>/<int:counter>", endpoint="seller_food_shop"
)
class FoodShop(Resource):
    """Handles HTTP requests to URL: /api/v1/seller/food/shop/<seller_id>/<counter>"""

    @seller_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @seller_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, seller_id, counter):
        """
        Get seller all food products without category filter
        Demo pass value
        { seller_id : '1', counter : integer, default = 1 }
        Intended result
        {
            'product_id':integer,
            'ref_no':'product unique referece no',
            'name':'name',
            'desc':'description as html',
            'feature':true/false,
            'regular_price':decimal,
            'sale_price': decimal,
            'addon': true/false,
            "img": url,
        }
        """
        return get_food_products(seller_id, None, counter)


# Seller shelf
# Get food product with categroy filter
@seller_ns.route(
    "/food/product/<int:seller_id>/<int:category_id>/<int:counter>",
    endpoint="seller_food_shelf",
)
class FoodShelf(Resource):
    """Handles HTTP requests to URL: /api/v1/seller/food/shop/<seller_id>/<category_id>/<counter>"""

    @seller_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @seller_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, seller_id, category_id, counter):
        """
        Get seller all food products with category filter
        Demo pass value
        { seller_id : '1', category_id=integer, counter : integer, default = 1 }
        Intended result
        {
            'product_id':integer,
            'ref_no':'product unique referece no',
            'name':'name',
            'desc':'description as html',
            'feature':true/false,
            'regular_price':decimal,
            'sale_price': decimal,
            'addon': true/false,
            "img": url,
        }
        """
        return get_food_products(seller_id, category_id, counter)

@seller_ns.route("/review/<int:seller_id>",
    endpoint="seller_review")
class Review(Resource):
    """Handles HTTP requests to URL: /api/v1/seller/review/<int:seller_id"""

    @seller_ns.doc(security="Bearer")
    @seller_ns.expect(rev_parser)

    @seller_ns.response(int(HTTPStatus.OK), "Profile saved.")
    @seller_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @seller_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    

    def post(self,seller_id):
        ''' Post customer-seller review 
        Demo pass values
        { seller_id:'1', rate:Integer ,review:String,order_id:Integer  }

        Intended Result
        { 
            status:success/fail,
            message:review_created or error

        }        
        '''
        data=rev_parser.parse_args()
        res=review_create(seller_id,data)
        
        return res
    
    def get(self,seller_id):
        '''
        Get customers_seller reviews
        
        Demo pass value
        { seller_id : '1 }
        Intended result
        {
            'first_name':Reviewd Customer first name,
            'rate':integer 1-5,
            'review':String,            
        }
        '''
        return get_seller_review(seller_id)

    
    

   


   

    
    



    

