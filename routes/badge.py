from flask import Blueprint, render_template, flash
from flask_login import login_required, current_user
from models import db, Badge, UserBadge
from datetime import datetime

badge_bp = Blueprint('badge', __name__)


def check_and_award_badges(user):
    """バッジの取得条件をチェックして、条件を満たしていれば付与する"""
    all_badges = Badge.query.all()
    already_earned_ids = {ub.badge_id for ub in user.badges}
    newly_earned = []

    for badge in all_badges:
        if badge.id in already_earned_ids:
            continue  # すでに取得済みはスキップ

        earned = False

        # ① ポイント数による条件チェック
        if badge.badge_type == 'points':
            if user.total_points >= badge.required_points:
                earned = True

        # ② 釣った魚の数による条件チェック
        elif badge.badge_type == 'catch_count':
            catch_count = len(user.catches)
            if catch_count >= badge.required_points:  # required_pointsを必要数として流用
                earned = True

        # ③ クエスト完了数による条件チェック
        elif badge.badge_type == 'quest_count':
            completed_quests = sum(
                1 for q in user.quests if q.status == '完了'
            )
            if completed_quests >= badge.required_points:
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

    return newly_earned  # 新たに獲得したバッジのリストを返す


@badge_bp.route('/badges')
@login_required
def badge_list():
    """バッジ一覧ページ"""
    # 条件チェックして新しいバッジがあればflashで通知
    newly_earned = check_and_award_badges(current_user)
    for badge in newly_earned:
        flash(f'🎉 新しいバッジ「{badge.name}」を獲得しました！', 'success')

    all_badges = Badge.query.all()
    earned_ids = {ub.badge_id for ub in current_user.badges}

    return render_template('badge.html', badges=all_badges, earned_ids=earned_ids)