from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from models import db, Badge, UserBadge
from datetime import datetime

badge_bp = Blueprint('badge', __name__, url_prefix='/badges')


# ===============================
# 🏆 バッジ付与チェック
# ===============================
def check_and_award_badges(user):
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

        # ① ポイント条件
        if badge.badge_type == 'points':
            if user.total_points >= badge.required_points:
                earned = True

        # ② 釣果数条件
        elif badge.badge_type == 'catch_count':
            if len(user.catches) >= badge.required_points:
                earned = True

        # ③ クエスト完了数条件
        elif badge.badge_type == 'quest_count':
            completed = sum(
                1 for q in user.quests if q.status == '完了'
            )
            if completed >= badge.required_points:
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
@login_required
def badge_list():

    newly_earned = check_and_award_badges(current_user)

    for badge in newly_earned:
        flash(f'🎉 新しいバッジ「{badge.name}」を獲得しました！', 'success')

    all_badges = Badge.query.all()
    earned_ids = {
        ub.badge_id for ub in UserBadge.query.filter_by(user_id=current_user.id).all()
    }

    return render_template(
        'badges.html',
        badges=all_badges,
        earned_ids=earned_ids
    )