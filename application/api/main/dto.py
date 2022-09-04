from flask_restx.reqparse import RequestParser

#
# ---------------------------------------Request parsers--------------------------------------------------------------------------
# 

# Use on search
search_parser = RequestParser(bundle_errors=True)
search_parser.add_argument('longitude', type=float, location="json", required=True, nullable=False, help="Location longitude in float")
search_parser.add_argument('latitude', type=float, location="json", required=True, nullable=False, help="Location latitude in float")
search_parser.add_argument('category', type=str, location="json", help="Integer value of category id")
search_parser.add_argument('keyword', type=str, location="json", help="Values as a list eg: [Type(g/f), Cat_id(1), ...]")
search_parser.add_argument('counter', type=int, location="json", required=True, help="Staring from 1 send incremented value on infite scroll")