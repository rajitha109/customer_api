from http import HTTPStatus
from flask_restx import Namespace, Resource

from .functions import (
    home,
    grocery_home,
    food_home,
    seller_find,
    grocery_product_find,
    food_product_find,
    category_filter,
)
from .dto import search_parser

main_ns = Namespace(name="main", validate=True)


# Home of app
# Display main categories, Ads, top reviewd selers in  the area
@main_ns.route("/home", endpoint="home")
class Home(Resource):
    """Handles HTTP requests to URL: /api/v1/main/home"""

    @main_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @main_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self):
        """
        Get primary types(Grocery and food) and ads

        Intended result
            {
                'ad':[
                    {
                        'id':interger,
                        'img':url
                    },
                ]
            }
        """
        return home()


# Home of app
# Display main categories, Ads, top reviewd selers in  the area
@main_ns.route("/grocery/home", endpoint="grocery_home")
class GroceryHome(Resource):
    """Handles HTTP requests to URL: /api/v1/main/grocery"""

    @main_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @main_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self):
        """
        Get grocery main categoreis and ads

        Intended result
            {
                'cat':[
                    {
                        'category_id':interger,
                        'name':'category_name,
                        'img':url
                    },
                ],
                'ad':[
                    {
                        'id':interger,
                        'img':url
                    },
                ]
            }
        """
        return grocery_home()


# Home of app
# Display main categories, Ads, top reviewd selers in  the area
@main_ns.route("/food/home", endpoint="food_home")
class FoodHome(Resource):
    """Handles HTTP requests to URL: /api/v1/main/food"""

    @main_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @main_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self):
        """
        Get food main categories and ads

        Intended result
            {
                'cat':[
                    {
                        'category_id':interger,
                        'name':'category_name,
                        'img':url
                    },
                ],
                'ad':[
                    {
                        'id':interger,
                        'img':url
                    },
                ]
            }
        """
        return food_home()


# Search grocery sellers
# Filter options Mandatory = longitude and latitude, Optional = Category, Keyword
@main_ns.route("/grocery/search/seller", endpoint="grocery_seller_search")
class GrocerySellerSearch(Resource):
    """Handles HTTP requests to URL: /api/v1/main/grocery/search/seller"""

    @main_ns.expect(search_parser)
    @main_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @main_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):
        """
        Post parms and get nearest grocery sellers 
        
        Demo pass value
            {
                'longtitude':80.6679, **Required
                'latitude':7.2957, **Required
                'category': '1/2'.
                'keyword':'doe',
                'counter': '1,2,3..' **Required, Default = 1, Paginate result
            }
        Intended result
            {
                'id':integer,
                'org':'Organization name',
                'img': url
            }
        """
        data = search_parser.parse_args()
        res = seller_find(data, "g")
        return res


# Search food sellers
# Filter options Mandatory = longitude and latitude, Optional = Category, Keyword
@main_ns.route("/food/search/seller", endpoint="food_seller_search")
class FoodSellerSearch(Resource):
    """Handles HTTP requests to URL: /api/v1/main/food/search/seller"""

    @main_ns.expect(search_parser)
    @main_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @main_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):
        """
        Post parms and get nearest food sellers 

        Demo pass value
            {
                'longtitude':80.6679, **Required
                'latitude':7.2957, **Required
                'category': '1/2'.
                'keyword':'doe',
                'counter': '1,2,3..' **Required, Default = 1, Paginate result
            }
        Intended result
            {
                'id':integer,
                'org':'Organization name',
                'img': url
            }
        """
        data = search_parser.parse_args()
        res = seller_find(data, "f")
        return res


# Search item
# Filter options Mandatory = longitude and latitude, Optional = Category, Keyword
@main_ns.route("/grocery/search/product", endpoint="grocery_product_search")
class GroceryProductSearch(Resource):
    """Handles HTTP requests to URL: /api/v1/main/grocery/search/product"""

    @main_ns.expect(search_parser)
    @main_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @main_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):
        """
        Post params and get grocery product of nearest sellers

        Demo pass value
            {
                'longtitude':80.6679, **Required
                'latitude':7.2957, **Required
                'category': '1/2'.
                'keyword':'doe',
                'counter': '1,2,3..' **Required, Default = 1, Paginate result
            }
        Intended result
            {
                'product_id' = Interger,Product ID
                'seller_id' = Interger,seller ID
                'name' = Item name,
                'qty' = Stock quantity,
                'reg_price' = Regular price of item,
                'sale_price' = Sale price of item,
                'img' = Item image path
            }
        """
        data = search_parser.parse_args()
        res = grocery_product_find(data)
        return res


# Search item
# Filter options Mandatory = longitude and latitude, Optional = Category, Keyword
@main_ns.route("/food/search/product", endpoint="food_product_search")
class FoodProductSearch(Resource):
    """Handles HTTP requests to URL: /api/v1/main/food/search/product"""

    @main_ns.expect(search_parser)
    @main_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @main_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def post(self):
        """
        Post params and get food product of nearest sellers

        Demo pass value
            {
                'longtitude':80.6679, **Required
                'latitude':7.2957, **Required
                'category': '1/2'.
                'keyword':'doe',
                'counter': '1,2,3..' **Required, Default = 1, Paginate result
            }
        Intended result
            {
                'product_id' = Interger,Product ID
                'seller_id' = Interger,seller ID
                'name' = Item name,
                'reg_price' = Regular price of item,
                'sale_price' = Sale price of item,
                "addon" = 'True/False'
                'img' = Item image path
            }
        """
        data = search_parser.parse_args()
        res = food_product_find(data)
        return res


# Filter categories
# Filter cateries by type and previous category
@main_ns.route(
    "/grocery/filter/category/<int:cat_id>", endpoint="grocery_category_filter"
)
class GroceryCategoryFilter(Resource):
    """Handles HTTP requests to URL: /api/v1/main/grocery/filter/category/<category_id>"""

    @main_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @main_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self, cat_id):
        """
        Filter gorcery child categoris by parent categories

        Demo pass value
        { cat_id: integer }
        Intended result
        { 'id':'integer, 'term':'category name' }
        """
        return category_filter("g", cat_id)


# Filter categories
# Filter cateries by type and previous category
@main_ns.route("/food/filter/category", endpoint="food_category_filter")
class FoodCategoryFilter(Resource):
    """Handles HTTP requests to URL: /api/v1/main/food/filter/category"""

    @main_ns.response(int(HTTPStatus.OK), "Query run sucessfuly.")
    @main_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    def get(self):
        """
        Filter food child categoris by parent categories

        Demo pass value
        { cat_id: integer }
        Intended result
        { 'id':'integer, 'term':'category name' }
        """
        return category_filter("f", None)
