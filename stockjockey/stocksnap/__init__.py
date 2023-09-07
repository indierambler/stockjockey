from flask import Blueprint


stocksnap_bp = Blueprint('stocksnap', __name__, template_folder='templates')


from . import views
