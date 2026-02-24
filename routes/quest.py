from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from models import Quest, UserQuestProgress, db
from datetime import datetime
from routes.badge import check_and_award_badges

quest_bp = Blueprint("quest", __name__)


# ===============================
# 🎯 クエスト一覧表示（自動進捗対応）
# ===============================
@quest_bp.route("/quests")
@quest_bp.route("/quests/")
@login_required
def show_quests():

    # ユーザーの進捗情報を取得
    user_quests = UserQuestProgress.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "quests.html",
        user_quests=user_quests
    )


# ===============================
# 🔘 手動達成（既存機能保持）
# ===============================
@quest_bp.route("/quests/complete/<int:quest_id>")
@login_required
def complete_quest(quest_id):

    quest = Quest.query.get_or_404(quest_id)

    progress = UserQuestProgress.query.filter_by(
        user_id=current_user.id,
        quest_id=quest_id
    ).first()

    if progress is None:
        progress = UserQuestProgress(
            user_id=current_user.id,
            quest_id=quest_id,
            status='完了',
            progress_percent=100,
            completed_at=datetime.utcnow()
        )
        db.session.add(progress)

    if progress.status != '完了':
        progress.status = '完了'
        progress.progress_percent = 100
        progress.completed_at = datetime.utcnow()
        current_user.total_points += quest.reward_points

    db.session.commit()
    check_and_award_badges(current_user)

    return redirect(url_for("quest.show_quests"))


# ===============================
# 🔄 クエストリセット（既存保持）
# ===============================
@quest_bp.route("/quests/reset/<int:quest_id>")
@login_required
def reset_quest(quest_id):

    progress = UserQuestProgress.query.filter_by(
        user_id=current_user.id,
        quest_id=quest_id
    ).first()

    if progress:
        quest = Quest.query.get_or_404(quest_id)

        current_user.total_points -= quest.reward_points
        if current_user.total_points < 0:
            current_user.total_points = 0

        progress.status = '未着手'
        progress.progress_percent = 0
        progress.current_total_size = 0  # 🔥 サイズ型用に追加
        progress.completed_at = None

        db.session.commit()

    return redirect(url_for("quest.show_quests"))