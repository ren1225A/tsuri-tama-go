from flask import Blueprint, render_template, flash
from flask_login import current_user
from models import db, Badge, UserBadge
from datetime import datetime

badge_bp = Blueprint('badge', __name__, url_prefix='/badges')


# ===============================
# 🏆 バッジ付与チェック
# ===============================
def check_and_award_badges(user):

    if not user.is_authenticated:
        return []

    all_badges = Badge.query.all()

    already_earned_ids = {
        ub.badge_id
        for ub in UserBadge.query.filter_by(user_id=user.id).all()
    }

    newly_earned = []

    for badge in all_badges:

        if badge.id in already_earned_ids:
            continue

        earned = False

        if badge.badge_type == 'points':
            if user.total_points >= badge.required_points:
                earned = True

        if earned:
            new_badge = UserBadge(
                user_id=user.id,
                badge_id=badge.id,
                earned_at=datetime.utcnow()
            )
            db.session.add(new_badge)
            newly_earned.append(badge)

    if newly_earned:
        db.session.commit()

    return newly_earned


# ===============================
# 🎖 バッジ一覧ページ
# ===============================
@badge_bp.route('/')
def badge_list():

    all_badges = Badge.query.all()

    if not current_user.is_authenticated:
        return render_template(
            'badges.html',
            badges=all_badges,
            earned_ids=set()
        )

    newly_earned = check_and_award_badges(current_user)

    for badge in newly_earned:
        flash(f'🎉 新しいバッジ「{badge.name}」を獲得しました！', 'success')

    earned_ids = {
        ub.badge_id
        for ub in UserBadge.query.filter_by(user_id=current_user.id).all()
    }

    return render_template(
        'badges.html',
        badges=all_badges,
        earned_ids=earned_ids
    )