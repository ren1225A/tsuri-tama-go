from flask import Blueprint, render_template

learn_bp = Blueprint('learn', __name__, url_prefix='/learn')

@learn_bp.route('/')
def index():
    return '学習トップ（Bさんが作る）'

@learn_bp.route('/tools')
def tools():
    return render_template('tools.html')

@learn_bp.route('/conditions')
def conditions():
    return render_template('conditions.html')

@learn_bp.route('/spots')
def spots():
    return render_template('spots.html')