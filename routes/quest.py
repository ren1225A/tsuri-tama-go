from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from models import Quest, db

quest_bp = Blueprint("quest", __name__)

@quest_bp.route("/quests")
def show_quests():
    quests = Quest.query.all()
    return render_template("quests.html", quests=quests)


@quest_bp.route("/quests/complete/<int:quest_id>")

def complete_quest(quest_id):
    quest = Quest.query.get_or_404(quest_id)
    
    if not quest.is_completed:
        quest.is_completed = True
        # current_user.total_points += mission.points
        db.session.commit()
    return redirect(url_for("quest.show_quests"))

@quest_bp.route("/quests/reset/<int:quest_id>")
def reset_quest(quest_id):
    quest = Quest.query.get_or_404(quest_id)
    quest.is_completed = False
    db.session.commit()
    return redirect(url_for("quest.show_quests"))