from flask import Blueprint

mission_bp = Blueprint('mission', __name__, url_prefix='/mission')

@mission_bp.route('/')
def index():
    return 'ミッション一覧（Cさんが作る）'