from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tsuri.db'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from routes.auth import auth_bp
from routes.learn import learn_bp
from routes.mission import mission_bp

app.register_blueprint(auth_bp)
app.register_blueprint(learn_bp)
app.register_blueprint(mission_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)