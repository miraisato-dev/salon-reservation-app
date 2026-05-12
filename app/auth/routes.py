# app/auth/routes.py
from flask import (
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_user,
    logout_user,
    login_required
)

from flask import Blueprint

from app.models import Users
from app.forms import LoginForm, SignUpForm
from app.extensions import db

auth_bp = Blueprint(
    "auth",
    __name__
)


# =================
# ルーティング
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝
# ログイン(Form使用)
@auth_bp.route('/login', methods=["GET", "POST"])
def login():

    # Formインスタンス生成
    form = LoginForm()
    
    if form.validate_on_submit():
        # データ入力取得
        username = form.username.data
        password = form.password.data
        # 対象User取得
        user = Users.query.filter_by(username=username).first()
        # 認証判定
        if user is not None and user.check_password(password):
            # 成功
            # 引数として渡されたuserオブジェクトを使用してユーザーをログイン状態にする
            login_user(user)
            # 画面遷移
            return redirect(url_for("index"))
        # 失敗
        flash("認証不備です")
    # GETの時
    return render_template(
        "auth/login.html", 
        form=form
    )


# ログアウト
@auth_bp.route("/logout")
@login_required
def logout():
    # 現在ログインしているユーザーをログアウトする
    logout_user()
    # フラッシュメッセージ
    flash("ログアウトしました")
    # 画面遷移
    return redirect(url_for("login"))


# サインアップ(Form使用)
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    # Formインスタンス生成
    form = SignUpForm()
    if form.validate_on_submit():
        # データ入力取得
        username = form.username.data
        password = form.password.data
        # モデルを生成
        user = Users(username=username)
        # パスワードハッシュ化
        user.set_password(password)
        # 登録処理
        db.session.add(user)
        db.session.commit()
        # フラッシュメッセージ
        flash("ユーザー登録しました")
        # 画面遷移
        return redirect(url_for("login"))
    # GET時
    # 画面遷移
    return render_template("auth/register.html", form=form)


# ゲストログイン
@auth_bp.route("/guest-login", methods=["POST"])
def guest_login():

    guest_user = Users.query.filter_by(username="guest").first()

    login_user(guest_user)

    flash("ゲストログインしました")

    return redirect(url_for("index"))