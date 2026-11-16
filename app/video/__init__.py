from flask import Blueprint

bp = Blueprint("video", __name__, url_prefix="/video")

from app.video import routes
