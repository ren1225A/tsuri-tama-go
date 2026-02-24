from flask import Flask, render_template, url_for
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tsuri.db'


from models import db, Quest
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from models import db, User


from routes.auth import auth_bp
from routes.learn import learn_bp
from routes.mission import mission_bp
from routes.quest import quest_bp   # ← ここに移動
from routes.badge import badge_bp
from routes.catch import catch_bp

app.register_blueprint(auth_bp)
app.register_blueprint(learn_bp)
app.register_blueprint(mission_bp)
app.register_blueprint(quest_bp)   # ← ここに移動
app.register_blueprint(badge_bp)
app.register_blueprint(catch_bp)

@app.route('/')
def index():
    best_catch = None
    bg_image = url_for('static', filename='images/background.png')
    return render_template('index.html', best_catch=best_catch, bg_image=bg_image)

@app.route('/register')
def register():
    bg_image = url_for('static', filename='images/background.png')
    return render_template('register.html', bg_image=bg_image)

with app.app_context():
    db.create_all()
    print("DBを作成しました！")
    # ↓ ここに一時的に追加
    if Quest.query.count() == 0:
        q1 = Quest(title="初めての釣り", description="魚を1匹釣ろう", reward_points=10)
        db.session.add(q1)
        db.session.commit()
        print("クエストを追加しました！")
if __name__ == '__main__':
    app.run(debug=True)

@app.route("/badges")
def badge_list():
    user = current_user

    all_badges = Badge.query.all()
    user_badges = UserBadge.query.filter_by(user_id=user.id).all()

    acquired_badge_ids = [ub.badge_id for ub in user_badges]

    return render_template(
        "badges.html",
        badges=all_badges,
        acquired_badge_ids=acquired_badge_ids,
        total_points=user.total_points
    )
    