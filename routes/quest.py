from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from models import Quest, UserQuestProgress, db
from datetime import datetime
from routes.badge import check_and_award_badges

quest_bp = Blueprint("quest", __name__)

@quest_bp.route("/quests")
@login_required
def show_quests():
    quests = Quest.query.all()

    # ユーザーごとの完了済みクエストIDを取得
    completed_ids = {
        p.quest_id for p in current_user.quests if p.status == '完了'
    }

    return render_template("quests.html", quests=quests, completed_ids=completed_ids)


@quest_bp.route("/quests/complete/<int:quest_id>")
@login_required
def complete_quest(quest_id):
    quest = Quest.query.get_or_404(quest_id)

    # すでに完了しているか確認
    progress = UserQuestProgress.query.filter_by(
        user_id=current_user.id,
        quest_id=quest_id
    ).first()

    if progress is None:
        # 初めて達成する場合：新規作成
        progress = UserQuestProgress(
            user_id=current_user.id,
            quest_id=quest_id,
            status='完了',
            progress_percent=100,
            completed_at=datetime.utcnow()
        )
        db.session.add(progress)

        # ポイント付与
        current_user.total_points += quest.reward_points
        db.session.commit()

        # バッジ取得チェック
        check_and_award_badges(current_user)

    elif progress.status != '完了':
        # 進行中だった場合：完了に更新
        progress.status = '完了'
        progress.progress_percent = 100
        progress.completed_at = datetime.utcnow()
        current_user.total_points += quest.reward_points
        db.session.commit()

        # バッジ取得チェック
        check_and_award_badges(current_user)

    return redirect(url_for("quest.show_quests"))


@quest_bp.route("/quests/reset/<int:quest_id>")
@login_required
def reset_quest(quest_id):
    progress = UserQuestProgress.query.filter_by(
        user_id=current_user.id,
        quest_id=quest_id
    ).first()

    if progress:
        # ポイントを戻す
        quest = Quest.query.get_or_404(quest_id)
        current_user.total_points -= quest.reward_points
        if current_user.total_points < 0:
            current_user.total_points = 0

        progress.status = '未着手'
        progress.progress_percent = 0
        progress.completed_at = None
        db.session.commit()

    return redirect(url_for("quest.show_quests"))