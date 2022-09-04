
from flask_restx.reqparse import RequestParser


#
# ---------------------------------------Request parsers--------------------------------------------------------------------------
# 

# Use on review_create
rev_parser = RequestParser(bundle_errors=True)
rev_parser.add_argument('rate', type=int, location="json", required=True, nullable=False, help="int 1 to 5 ")
rev_parser.add_argument('review',type=str, location="json", required=False, nullable=True,help="review as string(255)")
rev_parser.add_argument('order_id',type=int, location="json",required=False,nullable=False,help="order-id as int ")