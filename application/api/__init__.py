from flask import Blueprint
from flask_restx import Api

from application.api.user.endpoints import user_ns
from application.api.main.endpoints import main_ns
from application.api.seller.endpoints import seller_ns
from application.api.order.endpoints import order_ns

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    api_bp,
    version="1.0",
    title="GoGett Customer App",
    description="GoGett Grocery and Food Customer App API.",
    doc='/ui',
    authorizations=authorizations,
)

# Namespaces

api.add_namespace(user_ns, path="/user")
api.add_namespace(main_ns, path="/main")
api.add_namespace(seller_ns, path="/seller")
api.add_namespace(order_ns,path="/order")