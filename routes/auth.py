from flask import Blueprint

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login')
def login():
    return 'ログインページ（Aさんが作る）'

@auth_bp.route('/register')
def register():
    return '登録ページ（Aさんが作る）'