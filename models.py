from app import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    level = db.Column(db.Integer, default=1)
    total_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Quest(db.Model):
    __tablename__ = 'quests'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text)
    description = db.Column(db.Text)
    reward_points = db.Column(db.Integer, default=0)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'))
    spot_id = db.Column(db.Integer, db.ForeignKey('fishing_spots.id'))
    order_index = db.Column(db.Integer, default=0)

class UserQuestProgress(db.Model):
    __tablename__ = 'user_quest_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    quest_id = db.Column(db.Integer, db.ForeignKey('quests.id'))
    status = db.Column(db.Text, default='未着手')
    progress_percent = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime)

class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)
    badge_type = db.Column(db.Text)
    required_points = db.Column(db.Integer, default=0)

class UserBadge(db.Model):
    __tablename__ = 'user_badges'
    id = db.Column(db.Integer, primary_ke