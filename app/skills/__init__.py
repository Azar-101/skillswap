from flask import Blueprint

bp = Blueprint("skills", __name__, url_prefix="/skills")

from app.skills import routes
