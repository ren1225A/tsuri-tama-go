from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Catch, FishSpecies, FishingSpot
from datetime import datetime
from routes.badge import check_and_award_badges

catch_bp = Blueprint('catch', __name__, url_prefix='/catch')


@catch_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_catch():

    fishes = FishSpecies.query.all()
    spots = FishingSpot.query.all()

    if request.method == 'POST':

        fish_id = int(request.form['fish_id'])
        spot_id = int(request.form['spot_id'])
        size_cm = float(request.form['size_cm'])

        # 🎯 ポイント計算
        earned_points = 5 + int(size_cm)

        new_catch = Catch(
            user_id=current_user.id,
            fish_id=fish_id,
            spot_id=spot_id,
            size_cm=size_cm,
            earned_points=earned_points
        )

        db.session.add(new_catch)

        # 🔥 ユーザー総ポイントに加算
        current_user.total_points += earned_points

        db.session.commit()

        # 🔥 バッジチェック
        newly_earned = check_and_award_badges(current_user)
        for badge in newly_earned:
            flash(f'🎉 新しいバッジ「{badge.name}」を獲得しました！', 'success')

        flash(f"釣果登録完了！ +{earned_points}pt", "success")

        return redirect(url_for('catch.add_catch'))

    return render_template(
        'add_catch.html',
        fishes=fishes,
        spots=spots
    )