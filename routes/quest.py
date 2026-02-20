from flask import Blueprint, render_template
from models import Quest

quest_bp = Blueprint("quest", __name__)

@quest_bp.route("/quests")
def show_quests():
    return "クエスト画面OK"
