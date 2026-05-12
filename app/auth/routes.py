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
