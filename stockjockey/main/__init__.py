from ..stocksnap import stocksnap_bp
from flask import Blueprint

main_bp = Blueprint('main', __name__, template_folder='templates')
main_bp.register_blueprint(stocksnap_bp)  # nested blueprint


from . import views
