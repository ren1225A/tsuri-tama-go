from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from models import Quest, UserQuestProgress, db
from datetime import datetime
from routes.badge import check_and_award_badges

quest_bp = Blueprint("quest", __name__)

@quest_bp.route("/quests")
@quest_bp.route("/quests/")
def show_quests():
    quests = Quest.query.all()
    
    if current_user.is_authenticated:
        completed_ids = {
            p.quest_id for p in current_user.quests if p.status == '完了'
        }
    else:
        completed_ids = set()
    
    return render_template("quests.html", quests=quests, completed_ids=completed_ids)


@quest_bp.route("/quests/complete/<int:quest_id>")
def complete_quest(quest_id):
    if not current_user.is_authenticated:
        return redirect(url_for("quest.show_quests"))

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
        current_user.total_points = (current_user.total_points or 0) + quest.reward_points
        db.session.commit()
        check_and_award_badges(current_user)

    if progress and progress.status == '完了':
        return redirect(url_for("quest.show_quests"))

    elif progress.status != '完了':
        progress.status = '完了'
        progress.progress_percent = 100
        progress.completed_at = datetime.utcnow()
        current_user.total_points += quest.reward_points
        db.session.commit()
        check_and_award_badges(current_user)
        db.session.commit()

    return redirect(url_for("quest.show_quests"))


@quest_bp.route("/quests/reset/<int:quest_id>")
def reset_quest(quest_id):
    if not current_user.is_authenticated:
        return redirect(url_for("quest.show_quests"))

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
        progress.completed_at = None
        db.session.commit()

    return redirect(url_for("quest.show_quests"))