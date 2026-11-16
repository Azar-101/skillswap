from flask import Blueprint

bp = Blueprint("reviews", __name__, url_prefix="/reviews")

from app.reviews import routes
