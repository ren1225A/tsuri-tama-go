from flask import Flask, render_template
from flask_login import LoginManager, current_user
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tsuri.db'

from models import db
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from models import db, User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from routes.auth import auth_bp
from routes.learn import learn_bp
from routes.mission import mission_bp

app.register_blueprint(auth_bp)
app.register_blueprint(learn_bp)
app.register_blueprint(mission_bp)

@app.route('/')
def index():
    best_catch = None
    return render_template('index.html', best_catch=best_catch)

with app.app_context():
    db.create_all()
    print("DBを作成しました！")

if __name__ == '__main__':
    app.run(debug=True)