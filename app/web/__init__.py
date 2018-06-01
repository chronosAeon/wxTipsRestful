from flask import Blueprint

web = Blueprint('web', __name__)
from app.web import announcement
from app.web import user
