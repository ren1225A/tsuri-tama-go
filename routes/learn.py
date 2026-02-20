from flask import Blueprint

learn_bp = Blueprint('learn', __name__, url_prefix='/learn')

@learn_bp.route('/')
def index():
    return '学習トップ（Bさんが作る）'