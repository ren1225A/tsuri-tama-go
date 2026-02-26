print("Template folder:", app.template_folder)
from flask import Flask, render_template, url_for
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tsuri.db'

# ======================
# DB 初期設定
# ======================
from models import db, User, Quest, Badge, UserBadge, FishLog
db.init_app(app)

# ======================
# ログイン設定
# ======================
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



# ======================
# Blueprint 登録
# ======================
from routes.auth import auth_bp
from routes.learn import learn_bp
from routes.mission import mission_bp
from routes.quest import quest_bp
from routes.badge import badge_bp
from routes.fish_log import fish_log_bp

app.register_blueprint(auth_bp)
app.register_blueprint(learn_bp)
app.register_blueprint(mission_bp)
app.register_blueprint(quest_bp)
app.register_blueprint(badge_bp)
app.register_blueprint(fish_log_bp)

# ======================
# トップページ
# ======================
@app.route('/')
def index():
    if current_user.is_authenticated:
        best_catch = FishLog.query.filter_by(
            user_id=current_user.id
        ).order_by(FishLog.size_cm.desc()).first()
    else:
        best_catch = None

    bg_image = url_for('static', filename='images/background.png')
    return render_template(
        'index.html',
        best_catch=best_catch,
        bg_image=bg_image
    )

# ======================
# 初期データ作成
# ======================
with app.app_context():
    db.create_all()
    print("DBを作成しました！")

    # クエスト初期データ
    if Quest.query.count() <= 1:
        Quest.query.delete()
        db.session.commit()

        quests = [
            Quest(title="魚を1匹釣ろう", description="魚を1匹釣ろう", category="釣果", reward_points=10),
            Quest(title="図鑑に登録しよう", description="計1匹 図鑑に登録する", category="釣果", reward_points=10),
            Quest(title="詳細を見よう", description="詳細を1個見よう！", category="道具図鑑", reward_points=5),
            Quest(title="詳細を3つ見よう", description="詳細を3つ見よう！", category="道具図鑑", reward_points=15),
        ]

        for q in quests:
            db.session.add(q)

        db.session.commit()

    # バッジ初期データ
    if Badge.query.count() == 0:

        badges = [
            Badge(
                name="初心者バッジ",
                description="トップ詳細を読んだ",
                badge_type="reading",
                image_url="/static/images/beginner.png"
            ),
            Badge(
                name="ブロンズバッジ",
                description="50pt達成",
                badge_type="points",
                required_points=50,
                image_url="/static/images/bronze.png"
            ),
            Badge(
                name="シルバーバッジ",
                description="100pt達成",
                badge_type="points",
                required_points=100,
                image_url="/static/images/silver.png"
            ),
            Badge(
                name="ゴールドバッジ",
                description="200pt達成",
                badge_type="points",
                required_points=200,
                image_url="/static/images/gold.png"
            ),
            Badge(
                name="プラチナバッジ",
                description="500pt達成",
                badge_type="points",
                required_points=500,
                image_url="/static/images/platinum.png"
            ),
            Badge(
                name="秘密の卵バッジ",
                description="1000pt達成",
                badge_type="points",
                required_points=1000,
                image_url="/static/images/secret.png"
            ),
        ]

        for b in badges:
            db.session.add(b)

        db.session.commit()
    print("バッジ初期データ作成完了")

# ======================
# 起動
# ======================
if __name__ == '__main__':
    app.run(debug=True)