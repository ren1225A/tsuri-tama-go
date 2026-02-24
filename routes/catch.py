from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Catch, FishSpecies, FishingSpot, UserQuestProgress, Quest
from datetime import datetime
from routes.badge import check_and_award_badges

catch_bp = Blueprint('catch', __name__, url_prefix='/catch')


# ===============================
# 🎯 クエスト進捗更新関数（合計サイズ型）
# ===============================
def update_quest_progress_by_size(user, catch_size):

    user_quests = UserQuestProgress.query.filter_by(user_id=user.id).all()

    for uq in user_quests:

        if uq.status == "達成":
            continue

        quest = Quest.query.get(uq.quest_id)

        # 合計サイズ加算
        uq.current_total_size += catch_size

        if uq.current_total_size >= quest.target_total_size:
            uq.status = "達成"
            uq.completed_at = datetime.utcnow()
            user.total_points += quest.reward_points

    db.session.commit()


# ===============================
# 🎣 釣果登録
# ===============================
@catch_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_catch():

    if request.method == 'POST':

        fish_name = request.form['fish_name']
        spot_name = request.form['spot_name']
        size_cm = float(request.form['size_cm'])

        earned_points = 5 + int(size_cm)

        new_catch = Catch(
            user_id=current_user.id,
            fish_name=fish_name,
            spot_name=spot_name,
            size_cm=size_cm,
            earned_points=earned_points
        )

        db.session.add(new_catch)

        current_user.total_points += earned_points

        db.session.commit()

        # 🔥 クエスト進捗更新
        update_quest_progress_by_size(current_user, size_cm)

        # （既存バッジチェックがあればそのまま）
        check_and_award_badges(current_user)

        flash(f"釣果登録完了！ +{earned_points}pt", "success")

        return redirect(url_for('catch.add_catch'))

    return render_template('add_catch.html')