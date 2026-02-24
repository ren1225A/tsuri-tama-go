from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    level = db.Column(db.Integer, default=1)
    total_points = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Relationships ---
    quests = db.relationship('UserQuestProgress', backref='user', lazy=True)
    badges = db.relationship('UserBadge', back_populates='user', lazy=True)
    catches = db.relationship('Catch', backref='user', lazy=True)
    # 学習既読フラグ
has_read_tools = db.Column(db.Boolean, default=False)
has_read_conditions = db.Column(db.Boolean, default=False)
has_read_spots = db.Column(db.Boolean, default=False)
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
    

    badge = db.relationship('Badge', backref='quests', lazy=True)
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
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    icon_path = db.Column(db.String(255))  # staticフォルダ内の画像パス
    required_points = db.Column(db.Integer, default=0)
    badge_type = db.Column(db.String(50))
    
    # --- Relationships ---
    users = db.relationship('UserBadge', back_populates='badge', lazy=True)
class UserBadge(db.Model):
    __tablename__ = 'user_badges'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), nullable=False)

    acquired_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- Relationships ---
    user = db.relationship('User', back_populates='badges')
    badge = db.relationship('Badge', back_populates='users')


class FishingSpot(db.Model):
    __tablename__ = 'fishing_spots'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text)
    description = db.Column(db.Text)
    difficulty = db.Column(db.Integer, default=1)
    rules = db.Column(db.Text)
    tide_info = db.Column(db.Text)

class FishSpecies(db.Model):
    __tablename__ = 'fish_species'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    rarity_level = db.Column(db.Integer, default=1)
    description = db.Column(db.Text)
    season = db.Column(db.Text)
    habitat = db.Column(db.Text)

class Catch(db.Model):
    __tablename__ = 'catches'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    fish_id = db.Column(db.Integer, db.ForeignKey('fish_species.id'))
    spot_id = db.Column(db.Integer, db.ForeignKey('fishing_spots.id'))
    size_cm = db.Column(db.Float)
    earned_points = db.Column(db.Integer, default=0)

    fish = db.relationship('FishSpecies', backref='catches', lazy=True)
    spot = db.relationship('FishingSpot', backref='catches', lazy=True)