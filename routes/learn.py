from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, Badge, UserBadge
from datetime import datetime
import random

learn_bp = Blueprint('learn', __name__, url_prefix='/learn')


# ===============================
# 学習トップ
# ===============================
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


# ===============================
# 道具ページ
# ===============================
@learn_bp.route('/tools')
@login_required
def tools():

    if not current_user.has_read_tools:
        current_user.has_read_tools = True
        db.session.commit()

    check_beginner_badge()

    return render_template('tools.html')


# ===============================
# 条件ページ
# ===============================
@learn_bp.route('/conditions')
@login_required
def conditions():

    if not current_user.has_read_conditions:
        current_user.has_read_conditions = True
        db.session.commit()

    check_beginner_badge()

    return render_template('conditions.html')


# ===============================
# 場所ページ
# ===============================
@learn_bp.route('/spots')
@login_required
def spots():

    if not current_user.has_read_spots:
        current_user.has_read_spots = True
        db.session.commit()

    check_beginner_badge()

    return render_template('spots.html')


# ===============================
# 初心者バッジチェック
# ===============================
def check_beginner_badge():

    # 3つ全部読んだか？
    if (
        current_user.has_read_tools and
        current_user.has_read_conditions and
        current_user.has_read_spots
    ):

        # 既に取得済みか確認
        existing = UserBadge.query.join(Badge).filter(
            UserBadge.user_id == current_user.id,
            Badge.name == "初心者バッジ"
        ).first()

        if not existing:
            beginner_badge = Badge.query.filter_by(name="初心者バッジ").first()

            if beginner_badge:
                new_badge = UserBadge(
                    user_id=current_user.id,
                    badge_id=beginner_badge.id,
                    acquired_at=datetime.utcnow()
                )
                db.session.add(new_badge)
                db.session.commit()
    return render_template('spots.html')

@learn_bp.route('/rules')
def rules():
    return render_template('rules.html')

