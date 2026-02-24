from flask import Blueprint, render_template
from flask_login import current_user
import random

learn_bp = Blueprint('learn', __name__, url_prefix='/learn')

@learn_bp.route('/')
def index():
    from models import FishLog

    best_catch = None
    if current_user.is_authenticated:
        best_catch = FishLog.query.filter_by(user_id=current_user.id)\
                                  .order_by(FishLog.size_cm.desc()).first()

    bg_images = ['sea1.png', 'sea2.png', 'sea3.png']  # 実際のファイル名に合わせてください
    bg_image = random.choice(bg_images)

    return render_template('index.html', best_catch=best_catch, bg_image=bg_image)

@learn_bp.route('/tools')
def tools():
    return render_template('tools.html')

@learn_bp.route('/conditions')
def conditions():
    return render_template('conditions.html')

@learn_bp.route('/spots')
def spots():
    return render_template('spots.html')

@learn_bp.route('/rules')
def rules():
    return render_template('rules.html')

