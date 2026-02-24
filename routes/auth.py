from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user
from models import User, db

auth_bp = Blueprint('auth', __name__,url_prefix='/auth'  )

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        # 🔥 ここから追加
        print("入力username:", username)
        print("入力password:", password)
        print("DB user:", user)
        if user:
            print("DB password:", user.password)
    # 🔥 ここまで追加

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('quest.show_quests'))

        return "ログイン失敗"

    return render_template('login.html')
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

         # 既に存在するかチェック
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "そのユーザー名は既に使われています"

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('register.html')    